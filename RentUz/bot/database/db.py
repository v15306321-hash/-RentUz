"""Работа с базой данных PostgreSQL (Neon) через asyncpg.

Одна база для всего: пользователи, объявления, фото, реклама, рефералы и
состояния диалогов (FSM). Данные больше не теряются при деплое Render."""
from __future__ import annotations

import json
import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import asyncpg

from config import DATABASE_URL

log = logging.getLogger(__name__)
_pool: asyncpg.Pool | None = None

# Статусы объявления
DRAFT_STATUSES = ("draft", "awaiting_photos", "awaiting_payment", "awaiting_receipt", "awaiting_crypto_payment")
# draft → awaiting_photos → awaiting_payment → awaiting_receipt / awaiting_crypto_payment
# → payment_review (чек) / moderation (crypto оплачено) → published
# Побочные: abandoned, rejected, unpublished

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id      BIGINT PRIMARY KEY,
    username     TEXT,
    full_name    TEXT,
    language     TEXT NOT NULL DEFAULT 'ru',
    intent       TEXT,
    phone        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id                 BIGSERIAL PRIMARY KEY,
    order_number       TEXT UNIQUE,
    user_id            BIGINT NOT NULL REFERENCES users(user_id),
    language           TEXT NOT NULL DEFAULT 'ru',
    status             TEXT NOT NULL DEFAULT 'draft',
    draft_step         TEXT,
    draft_data         JSONB NOT NULL DEFAULT '{}'::jsonb,
    city               TEXT,
    city_key           TEXT,
    district           TEXT,
    microdistrict      TEXT,
    property_type      TEXT,
    purpose            TEXT,
    area               DOUBLE PRECISION,
    rooms              INTEGER,
    property_floor     INTEGER,
    description        TEXT,
    price_uzs          BIGINT,
    price_usd          DOUBLE PRECISION,
    exchange_rate      DOUBLE PRECISION,
    commission_rate    DOUBLE PRECISION,
    base_fee           BIGINT,
    discount_percent   INTEGER NOT NULL DEFAULT 0,
    service_fee        BIGINT,
    phone              TEXT,
    contact_name       TEXT,
    contact_username   TEXT,
    payment_method     TEXT,
    payment_status     TEXT,
    receipt_file_id    TEXT,
    crypto_invoice_id  TEXT,
    crypto_invoice_url TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at       TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS orders_user_status ON orders(user_id, status);
CREATE INDEX IF NOT EXISTS orders_published ON orders(status, city_key, purpose);

CREATE TABLE IF NOT EXISTS order_photos (
    id             BIGSERIAL PRIMARY KEY,
    order_id       BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    file_id        TEXT NOT NULL,
    file_unique_id TEXT NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (order_id, file_unique_id)
);

CREATE TABLE IF NOT EXISTS ads (
    id                 BIGSERIAL PRIMARY KEY,
    user_id            BIGINT NOT NULL REFERENCES users(user_id),
    username           TEXT,
    full_name          TEXT,
    language           TEXT NOT NULL DEFAULT 'ru',
    duration_days      INTEGER NOT NULL,
    amount_uzs         BIGINT NOT NULL,
    banner_file_id     TEXT NOT NULL,
    caption            TEXT,
    link               TEXT,
    status             TEXT NOT NULL DEFAULT 'awaiting_payment',
    payment_method     TEXT,
    payment_status     TEXT,
    receipt_file_id    TEXT,
    crypto_invoice_id  TEXT,
    crypto_invoice_url TEXT,
    exchange_rate      DOUBLE PRECISION,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    starts_at          TIMESTAMPTZ,
    ends_at            TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS referrals (
    id                  BIGSERIAL PRIMARY KEY,
    referrer_id         BIGINT NOT NULL REFERENCES users(user_id),
    friend_id           BIGINT NOT NULL UNIQUE REFERENCES users(user_id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    qualified_at        TIMESTAMPTZ,
    qualifying_order_id BIGINT,
    used_order_id       BIGINT,
    CHECK (referrer_id <> friend_id)
);
CREATE INDEX IF NOT EXISTS referrals_referrer ON referrals(referrer_id);

CREATE TABLE IF NOT EXISTS fsm_storage (
    key        TEXT PRIMARY KEY,
    state      TEXT,
    data       JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

ORDER_COLUMNS = {
    "order_number", "language", "status", "draft_step", "draft_data", "city", "city_key", "district",
    "microdistrict", "property_type", "purpose", "area", "rooms", "property_floor", "description",
    "price_uzs", "price_usd", "exchange_rate", "commission_rate", "base_fee", "discount_percent",
    "service_fee", "phone", "contact_name", "contact_username", "payment_method", "payment_status",
    "receipt_file_id", "crypto_invoice_id", "crypto_invoice_url", "published_at",
}
AD_COLUMNS = {
    "username", "full_name", "language", "duration_days", "amount_uzs", "banner_file_id", "caption",
    "link", "status", "payment_method", "payment_status", "receipt_file_id", "crypto_invoice_id",
    "crypto_invoice_url", "exchange_rate", "starts_at", "ends_at",
}
USER_COLUMNS = {"username", "full_name", "language", "intent", "phone"}


def _clean_dsn(dsn: str) -> str:
    """Neon добавляет channel_binding=require — asyncpg его не понимает."""
    parts = urlsplit(dsn)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "channel_binding"]
    return urlunsplit(parts._replace(query=urlencode(query)))


async def _init_connection(conn: asyncpg.Connection) -> None:
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


async def init_db() -> None:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            _clean_dsn(DATABASE_URL), min_size=1, max_size=5,
            statement_cache_size=0,  # совместимость с пулером Neon (pgbouncer)
            init=_init_connection, command_timeout=30,
        )
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA)


async def close_db() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database is not initialised; call init_db() first")
    return _pool


def _row(row) -> dict | None:
    return dict(row) if row else None


def _set_clause(fields: dict, allowed: set[str], start: int = 1) -> tuple[str, list]:
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Unknown columns: {sorted(unknown)}")
    keys = list(fields)
    clause = ", ".join(f"{key} = ${i}" for i, key in enumerate(keys, start))
    return clause, [fields[k] for k in keys]


# ---------------------------------------------------------------- users

async def upsert_user(user_id: int, username: str | None, full_name: str | None,
                      language: str | None = None) -> bool:
    """Создаёт или обновляет пользователя. Возвращает True, если пользователь новый."""
    row = await pool().fetchrow(
        """
        INSERT INTO users (user_id, username, full_name, language)
        VALUES ($1, $2, $3, COALESCE($4, 'ru'))
        ON CONFLICT (user_id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                language = COALESCE($4, users.language)
        RETURNING (xmax = 0) AS created
        """,
        user_id, username, full_name, language,
    )
    return bool(row["created"])


async def get_user(user_id: int) -> dict | None:
    return _row(await pool().fetchrow("SELECT * FROM users WHERE user_id = $1", user_id))


async def update_user(user_id: int, **fields) -> None:
    if not fields:
        return
    clause, values = _set_clause(fields, USER_COLUMNS, 2)
    await pool().execute(f"UPDATE users SET {clause} WHERE user_id = $1", user_id, *values)


# ---------------------------------------------------------------- orders

async def create_draft_order(user_id: int, language: str, intent: str = "listing") -> dict:
    row = await pool().fetchrow(
        "INSERT INTO orders (user_id, language, status) VALUES ($1, $2, 'draft') RETURNING *",
        user_id, language,
    )
    order = dict(row)
    number = f"R-{order['id']}"
    await pool().execute("UPDATE orders SET order_number = $2 WHERE id = $1", order["id"], number)
    order["order_number"] = number
    return order


async def get_draft_order(user_id: int) -> dict | None:
    """Незавершённая заявка пользователя (любой шаг до отправки чека)."""
    return _row(await pool().fetchrow(
        "SELECT * FROM orders WHERE user_id = $1 AND status = ANY($2::text[]) ORDER BY id DESC LIMIT 1",
        user_id, list(DRAFT_STATUSES),
    ))


async def get_order(order_id: int | str) -> dict | None:
    return _row(await pool().fetchrow("SELECT * FROM orders WHERE id = $1", int(order_id)))


async def get_order_by_number(number: str) -> dict | None:
    return _row(await pool().fetchrow("SELECT * FROM orders WHERE upper(order_number) = upper($1)", number))


async def update_order(order_id: int | str, **fields) -> None:
    if not fields:
        return
    clause, values = _set_clause(fields, ORDER_COLUMNS, 2)
    await pool().execute(
        f"UPDATE orders SET {clause}, updated_at = now() WHERE id = $1", int(order_id), *values
    )


async def transition_order(order_id: int | str, from_statuses: tuple[str, ...] | list[str],
                           to_status: str, **fields) -> dict | None:
    """Атомарно меняет статус, только если текущий статус из from_statuses.
    Защищает от двойного нажатия «Одобрить» и повторной доставки обновлений."""
    clause, values = _set_clause({**fields, "status": to_status}, ORDER_COLUMNS, 3)
    row = await pool().fetchrow(
        f"UPDATE orders SET {clause}, updated_at = now() "
        f"WHERE id = $1 AND status = ANY($2::text[]) RETURNING *",
        int(order_id), list(from_statuses), *values,
    )
    return _row(row)


async def abandon_draft_order(order_id: int | str) -> None:
    async with pool().acquire() as conn, conn.transaction():
        await conn.execute(
            "UPDATE orders SET status = 'abandoned', updated_at = now() "
            "WHERE id = $1 AND status = ANY($2::text[])",
            int(order_id), list(DRAFT_STATUSES),
        )
        await conn.execute("UPDATE referrals SET used_order_id = NULL WHERE used_order_id = $1", int(order_id))


async def update_draft_progress(order_id: int, step: str, data: dict) -> None:
    clean = {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
    await pool().execute(
        "UPDATE orders SET draft_step = $2, draft_data = $3, updated_at = now() WHERE id = $1",
        int(order_id), step, clean,
    )


async def finalize_draft_order(order_id: int, fields: dict) -> dict | None:
    clause, values = _set_clause({**fields, "status": "awaiting_photos"}, ORDER_COLUMNS, 2)
    row = await pool().fetchrow(
        f"UPDATE orders SET {clause}, updated_at = now() WHERE id = $1 "
        f"AND status = ANY($%d::text[]) RETURNING *" % (len(values) + 2),
        int(order_id), *values, list(DRAFT_STATUSES),
    )
    return _row(row)


async def add_photo_to_order(order_id: int, file_id: str, file_unique_id: str, limit: int) -> tuple[bool, int]:
    """Добавляет фото (без дублей). Возвращает (добавлено ли, всего фото)."""
    async with pool().acquire() as conn, conn.transaction():
        await conn.execute("SELECT id FROM orders WHERE id = $1 FOR UPDATE", int(order_id))
        count = await conn.fetchval("SELECT count(*) FROM order_photos WHERE order_id = $1", int(order_id))
        if count >= limit:
            return False, count
        added = await conn.fetchval(
            "INSERT INTO order_photos (order_id, file_id, file_unique_id) VALUES ($1, $2, $3) "
            "ON CONFLICT (order_id, file_unique_id) DO NOTHING RETURNING id",
            int(order_id), file_id, file_unique_id,
        )
        return added is not None, count + (1 if added else 0)


async def get_order_photos(order_id: int) -> list[dict]:
    rows = await pool().fetch("SELECT * FROM order_photos WHERE order_id = $1 ORDER BY id", int(order_id))
    return [dict(r) for r in rows]


async def get_photo(photo_id: int) -> dict | None:
    return _row(await pool().fetchrow(
        "SELECT p.*, o.status AS order_status FROM order_photos p JOIN orders o ON o.id = p.order_id "
        "WHERE p.id = $1", int(photo_id),
    ))


async def search_published(city_key: str | None = None, purpose: str | None = None, limit: int = 5) -> tuple[int, list[dict]]:
    where = ["status = 'published'"]
    args: list = []
    if city_key:
        args.append(city_key)
        where.append(f"city_key = ${len(args)}")
    if purpose:
        args.append(purpose)
        where.append(f"purpose = ${len(args)}")
    sql_where = " AND ".join(where)
    total = await pool().fetchval(f"SELECT count(*) FROM orders WHERE {sql_where}", *args)
    rows = await pool().fetch(
        f"SELECT * FROM orders WHERE {sql_where} ORDER BY published_at DESC NULLS LAST LIMIT {int(limit)}", *args
    )
    return total, [dict(r) for r in rows]


async def published_listings_with_photos() -> list[dict]:
    rows = await pool().fetch(
        """
        SELECT o.*, COALESCE(array_agg(p.id ORDER BY p.id) FILTER (WHERE p.id IS NOT NULL), '{}') AS photo_ids
        FROM orders o LEFT JOIN order_photos p ON p.order_id = o.id
        WHERE o.status = 'published'
        GROUP BY o.id ORDER BY o.published_at DESC NULLS LAST
        """
    )
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- referrals

async def register_referral(referrer_id: int, friend_id: int) -> bool:
    if referrer_id == friend_id:
        return False
    exists = await pool().fetchval("SELECT 1 FROM users WHERE user_id = $1", referrer_id)
    if not exists:
        return False
    row = await pool().fetchrow(
        "INSERT INTO referrals (referrer_id, friend_id) VALUES ($1, $2) "
        "ON CONFLICT (friend_id) DO NOTHING RETURNING id",
        referrer_id, friend_id,
    )
    return row is not None


async def qualify_referral(friend_id: int, order_id: int) -> int | None:
    """Друг опубликовал первое объявление → приглашение засчитывается.
    Возвращает ID пригласившего (или None, если уже засчитано/нет приглашения)."""
    return await pool().fetchval(
        "UPDATE referrals SET qualified_at = now(), qualifying_order_id = $2 "
        "WHERE friend_id = $1 AND qualified_at IS NULL RETURNING referrer_id",
        friend_id, int(order_id),
    )


async def referral_stats(user_id: int) -> dict:
    row = await pool().fetchrow(
        """
        SELECT count(*) AS invited,
               count(*) FILTER (WHERE qualified_at IS NOT NULL) AS qualified,
               count(*) FILTER (WHERE qualified_at IS NOT NULL AND used_order_id IS NULL) AS available
        FROM referrals WHERE referrer_id = $1
        """,
        user_id,
    )
    return dict(row)


async def reserve_referral_credits(user_id: int, order_id: int, max_count: int) -> int:
    """Закрепляет за заявкой до max_count засчитанных друзей. Повторный вызов для той же
    заявки не списывает новых друзей. Возвращает число друзей, закреплённых за заявкой."""
    async with pool().acquire() as conn, conn.transaction():
        already = await conn.fetchval(
            "SELECT count(*) FROM referrals WHERE referrer_id = $1 AND used_order_id = $2", user_id, int(order_id)
        )
        need = max(0, max_count - already)
        if need:
            await conn.execute(
                """
                UPDATE referrals SET used_order_id = $2
                WHERE id IN (
                    SELECT id FROM referrals
                    WHERE referrer_id = $1 AND qualified_at IS NOT NULL AND used_order_id IS NULL
                    ORDER BY qualified_at LIMIT $3 FOR UPDATE SKIP LOCKED
                )
                """,
                user_id, int(order_id), need,
            )
        return await conn.fetchval(
            "SELECT count(*) FROM referrals WHERE referrer_id = $1 AND used_order_id = $2", user_id, int(order_id)
        )


async def release_referral_credits(order_id: int) -> None:
    await pool().execute("UPDATE referrals SET used_order_id = NULL WHERE used_order_id = $1", int(order_id))


# ---------------------------------------------------------------- ads

async def create_advertising_request(*, user_id: int, username: str | None, full_name: str | None,
                                     language: str, duration_days: int, amount_uzs: int,
                                     banner_file_id: str, caption: str | None, link: str | None) -> dict:
    row = await pool().fetchrow(
        """
        INSERT INTO ads (user_id, username, full_name, language, duration_days, amount_uzs,
                         banner_file_id, caption, link)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING *
        """,
        user_id, username, full_name, language, duration_days, amount_uzs, banner_file_id, caption, link,
    )
    return dict(row)


async def get_advertising_request(request_id: int | str | None) -> dict | None:
    if request_id is None:
        return None
    return _row(await pool().fetchrow("SELECT * FROM ads WHERE id = $1", int(request_id)))


async def update_advertising_request(request_id: int | str, **fields) -> None:
    if not fields:
        return
    clause, values = _set_clause(fields, AD_COLUMNS, 2)
    await pool().execute(f"UPDATE ads SET {clause}, updated_at = now() WHERE id = $1", int(request_id), *values)


async def transition_ad(request_id: int | str, from_statuses, to_status: str, **fields) -> dict | None:
    clause, values = _set_clause({**fields, "status": to_status}, AD_COLUMNS, 3)
    row = await pool().fetchrow(
        f"UPDATE ads SET {clause}, updated_at = now() WHERE id = $1 AND status = ANY($2::text[]) RETURNING *",
        int(request_id), list(from_statuses), *values,
    )
    return _row(row)


async def activate_ad(request_id: int) -> dict | None:
    row = await pool().fetchrow(
        """
        UPDATE ads SET status = 'active', starts_at = now(),
               ends_at = now() + make_interval(days => duration_days), updated_at = now()
        WHERE id = $1 AND status = 'paid_pending_moderation' RETURNING *
        """,
        int(request_id),
    )
    return _row(row)


async def active_ads() -> list[dict]:
    rows = await pool().fetch(
        "SELECT * FROM ads WHERE status = 'active' AND starts_at <= now() AND ends_at > now() ORDER BY starts_at"
    )
    return [dict(r) for r in rows]


# ---------------------------------------------------------------- FSM storage

async def fsm_get(key: str) -> tuple[str | None, dict]:
    row = await pool().fetchrow("SELECT state, data FROM fsm_storage WHERE key = $1", key)
    return (row["state"], row["data"] or {}) if row else (None, {})


async def fsm_set_state(key: str, state: str | None) -> None:
    await pool().execute(
        "INSERT INTO fsm_storage (key, state) VALUES ($1, $2) "
        "ON CONFLICT (key) DO UPDATE SET state = EXCLUDED.state, updated_at = now()",
        key, state,
    )


async def fsm_set_data(key: str, data: dict) -> None:
    await pool().execute(
        "INSERT INTO fsm_storage (key, data) VALUES ($1, $2) "
        "ON CONFLICT (key) DO UPDATE SET data = EXCLUDED.data, updated_at = now()",
        key, data,
    )
