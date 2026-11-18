"""Crypto Pay API adapter; token is loaded from the environment."""
from aiocryptopay import AioCryptoPay, Networks

from config import CRYPTO_PAY_TOKEN


async def create_crypto_invoice(amount_usdt: float, description: str, order_id: int) -> dict:
    if not CRYPTO_PAY_TOKEN:
        raise RuntimeError("CRYPTO_PAY_TOKEN is not configured")
    client = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)
    try:
        invoice = await client.create_invoice(
            asset="USDT",
            amount=amount_usdt,
            payload=str(order_id),
            description=description,
        )
        if isinstance(invoice, dict):
            return invoice
        return {
            "invoice_id": getattr(invoice, "invoice_id", None),
            "bot_invoice_url": getattr(invoice, "bot_invoice_url", None),
        }
    finally:
        close = getattr(client, "close", None)
        if close:
            result = close()
            if hasattr(result, "__await__"):
                await result


async def get_crypto_invoice_status(invoice_id: str | int) -> str:
    if not CRYPTO_PAY_TOKEN:
        raise RuntimeError("CRYPTO_PAY_TOKEN is not configured")
    client = AioCryptoPay(token=CRYPTO_PAY_TOKEN, network=Networks.MAIN_NET)
    try:
        invoices = await client.get_invoices(invoice_ids=[int(invoice_id)])
        if isinstance(invoices, dict):
            items = invoices.get("items", [])
        else:
            items = invoices
        if not items:
            return "not_found"
        item = items[0]
        if isinstance(item, dict):
            return str(item.get("status", "unknown"))
        return str(getattr(item, "status", "unknown"))
    finally:
        close = getattr(client, "close", None)
        if close:
            result = close()
            if hasattr(result, "__await__"):
                await result
