from django.db.models import TextChoices


class WeekdayChoices(TextChoices):
    SUNDAY = 'sun', 'Воскресенье'
    MONDAY = 'mon', 'Понедельник'
    TUESDAY = 'tue', 'Вторник'
    WEDNESDAY = 'wed', 'Среда'
    THURSDAY = 'thu', 'Четверг'
    FRIDAY = 'fri', 'Пятница'
    SATURDAY = 'sat', 'Суббота'


class LinkTypeChoices(TextChoices):
    BLANK = 'blank', 'Без ссылки'
    STOCK = 'stock', 'Переход в акцию'
    PRODUCT = 'product_card', 'Переход в карточку товара'
    CATEGORY = 'category', 'Переход в категорию фильтрованую по бренду, типу'
    MAGAZINE = 'magazine', 'Tvoy.kz журнал'


class ObjectTypeChoices(TextChoices):
    POST = 'post', 'Постамат'
    PICKUP = 'pickup_point', 'Пункт выдачи'


class DiscountTypeChoices(TextChoices):
    FIXED = 'fix', 'Фиксированное (тг)'
    PERCENT = 'percent', 'Процентный (%)'


class ContactLinkChoices(TextChoices):
    PHONE = 'tel', 'Номер телефона'
    LINK = 'link', 'Ссылка на соц. сеть'


class StoryTypeChoices(TextChoices):
    NORMAL = 'normal', 'Сториз'
    MINI = 'mini', 'Мини баннер'


class BaseUnitChoices(TextChoices):
    PIECE = '796', 'Штук'


class PropertyTypeChoices(TextChoices):
    # do not use `_` on choices, because it will be split by this character
    STRING = 'str', 'Текст'
    COLOR = 'color', 'Цвет'
    INTEGER = 'int', 'Целое число'
    BOOLEAN = 'bool', 'Булевы'
    DECIMAL = 'decimal', 'Десятичная дробь'


class DeliveryTypeChoice(TextChoices):
    COURIER = 'courier', 'Курьер'
    POST = 'post', 'Постамат'
    PICKUP = 'pickup', 'Пункт выдачи заказов'


class PaymentTypeChoice(TextChoices):
    CARD = 'card', 'Оплата картой'
    CASH = 'cash', 'Оплата наличными'
    POS = 'pos', 'POS-терминал'


class OrderStatusChoices(TextChoices):
    NOT_FINISHED = 'not_finished', 'Не завершен'
    NEW = 'new', 'Новый'
    PROCESSING = 'processing', 'В обработке'
    IN_STOCK = 'in_stock', 'Комплектация'
    STAFFED = 'staffed', 'Укомплектован на складе'
    DELIVER_DEPARTMENT = 'delivery_department', 'Передан в отдел доставки'
    IN_DELIVER = 'delivery_courier', 'Передан курьеру'
    DELIVERED = 'delivered', 'Доставлен'
    COMPLETED = 'completed', 'Выполнен'
    CANCELED = 'canceled', 'Отменен'


class StorehouseTypeChoices(TextChoices):
    BASIC = 'basic', 'Обычный'
    DISCOUNT = 'discount', 'Скидка'


class AddressIconChoices(TextChoices):
    OTHER = 'other', 'Другое'
    HOME = 'home', 'Дом'
    OFFICE = 'office', 'Офис'


class CompilationTypeChoices(TextChoices):
    MANUAL = 'manual', 'Ручная выборка'
    IS_NEW = 'is_new', 'По новизне'
    RECENTLY = 'recently', 'Недавно просмотренные'
