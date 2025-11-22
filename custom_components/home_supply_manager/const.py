"""Constants for the Supply Manager integration."""
from datetime import timedelta

# Integration domain
DOMAIN = "home_supply_manager"

# Configuration keys
CONF_PRODUCT_NAME = "product_name"
CONF_STOCK_QUANTITY = "stock_quantity"
CONF_REPLACEMENT_INTERVAL_DAYS = "replacement_interval_days"
CONF_LAST_REPLACEMENT_DATE = "last_replacement_date"
CONF_PRODUCT_ID = "product_id"
CONF_ICON = "icon"

# Default values
DEFAULT_STOCK_QUANTITY = 1
DEFAULT_REPLACEMENT_INTERVAL_DAYS = 30
DEFAULT_ICON = "mdi:package-variant"

# Update interval
UPDATE_INTERVAL = timedelta(hours=1)

# Service names
SERVICE_REPLACE_ITEM = "replace_item"
SERVICE_ADD_STOCK = "add_stock"
SERVICE_REMOVE_STOCK = "remove_stock"
SERVICE_UPDATE_PRODUCT = "update_product"

# Sensor types
SENSOR_TYPE_DAYS_UNTIL_REPLACEMENT = "days_until_replacement"
SENSOR_TYPE_STOCK = "stock"

# Storage
STORAGE_VERSION = 1
STORAGE_KEY = "home_supply_manager_products"

# Icons
ICON_CALENDAR = "mdi:calendar-clock"
ICON_CART = "mdi:cart-arrow-down"
ICON_PACKAGE = "mdi:package-variant"



