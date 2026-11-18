from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    language = State()


class MenuForm(StatesGroup):
    draft_choice = State()


class ListingForm(StatesGroup):
    city = State()
    district = State()
    custom_district = State()
    microdistrict = State()
    custom_microdistrict = State()
    property_type = State()
    deal = State()
    area = State()
    rooms = State()
    floor = State()
    price = State()
    description = State()
    phone = State()


class PhotoForm(StatesGroup):
    waiting_photos = State()


class SearchForm(StatesGroup):
    city = State()
    deal = State()


class SupportForm(StatesGroup):
    message = State()


class PaymentForm(StatesGroup):
    choosing_method = State()
    waiting_receipt = State()
    waiting_crypto = State()


class AdvertisingForm(StatesGroup):
    choosing_tariff = State()
    banner = State()
    choosing_payment_method = State()
    waiting_receipt = State()
    waiting_crypto = State()
