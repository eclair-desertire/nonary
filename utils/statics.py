from utils.choices import OrderStatusChoices, DeliveryTypeChoice

ORDER_KEYS = {
    OrderStatusChoices.NEW: "O",
    OrderStatusChoices.PROCESSING: "P",
    OrderStatusChoices.IN_STOCK: "I",
    OrderStatusChoices.STAFFED: "B",
    OrderStatusChoices.DELIVER_DEPARTMENT: "F",
    OrderStatusChoices.IN_DELIVER: "J",
    OrderStatusChoices.DELIVERED: "Y",
    OrderStatusChoices.COMPLETED: "C",
    OrderStatusChoices.CANCELED: "D",
}

ORDER_STATUS_TRANSLATES = {
    'Не согласован': OrderStatusChoices.NEW,
    'Подтвержден': OrderStatusChoices.PROCESSING,
    'Комплектация': OrderStatusChoices.IN_STOCK,
    'Скомплектован': OrderStatusChoices.STAFFED,
    'Передан в доставку': OrderStatusChoices.DELIVER_DEPARTMENT,
    'В пути': OrderStatusChoices.IN_DELIVER,
    'Прибыл': OrderStatusChoices.DELIVERED,
    'Выполнено': OrderStatusChoices.COMPLETED,
    'Отмена': OrderStatusChoices.CANCELED,
}

ORDER_REVERSED_KEYS = {
    "O": OrderStatusChoices.NEW,
    "P": OrderStatusChoices.PROCESSING,
    "I": OrderStatusChoices.IN_STOCK,
    "B": OrderStatusChoices.STAFFED,
    "F": OrderStatusChoices.DELIVER_DEPARTMENT,
    "J": OrderStatusChoices.IN_DELIVER,
    "Y": OrderStatusChoices.DELIVERED,
    "C": OrderStatusChoices.COMPLETED,
    "D": OrderStatusChoices.CANCELED,
}

DELIVERY_KEYS = {
    DeliveryTypeChoice.PICKUP: "8",
    DeliveryTypeChoice.COURIER: "1",
    DeliveryTypeChoice.POST: "6",
}

DELIVERY_REVERSED_KEYS = {
    "8": DeliveryTypeChoice.PICKUP,
    "1": DeliveryTypeChoice.COURIER,
    "6": DeliveryTypeChoice.POST,
}
