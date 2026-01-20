"""
Handlers package __init__.py
Barcha handlerlarni import qilish
"""

from . import start
from . import driver_registration
from . import passenger_registration
from . import orders
from . import admin

__all__ = [
    'start',
    'driver_registration',
    'passenger_registration',
    'orders',
    'admin'
]
