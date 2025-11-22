"""DataUpdateCoordinator for Supply Manager."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_LAST_REPLACEMENT_DATE,
    CONF_PRODUCT_ID,
    CONF_PRODUCT_NAME,
    CONF_REPLACEMENT_INTERVAL_DAYS,
    CONF_STOCK_QUANTITY,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class SupplyManagerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Supply Manager data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry
        self.store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}")
        self._products: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from storage."""
        return self._products

    async def async_config_entry_first_refresh(self) -> None:
        """Perform first refresh and load stored data."""
        # Load products from storage
        stored_data = await self.store.async_load()
        if stored_data:
            self._products = stored_data.get("products", {})
        
        # If this is first time setup and we have data in config entry, migrate it
        product_id = self.entry.data.get(CONF_PRODUCT_ID)
        if product_id and not self._products:
            # Migrate from old config entry format
            self._products[product_id] = {
                CONF_PRODUCT_ID: product_id,
                CONF_PRODUCT_NAME: self.entry.data.get(CONF_PRODUCT_NAME),
                CONF_STOCK_QUANTITY: self.entry.data.get(CONF_STOCK_QUANTITY),
                CONF_REPLACEMENT_INTERVAL_DAYS: self.entry.data.get(
                    CONF_REPLACEMENT_INTERVAL_DAYS
                ),
                CONF_LAST_REPLACEMENT_DATE: self.entry.data.get(
                    CONF_LAST_REPLACEMENT_DATE
                ),
            }
            await self._async_save_products()

        await super().async_config_entry_first_refresh()

    async def _async_save_products(self) -> None:
        """Save products to storage."""
        await self.store.async_save({"products": self._products})

    def calculate_days_until_replacement(self, product_id: str) -> int | None:
        """Calculate days until next replacement."""
        if product_id not in self._products:
            return None

        product = self._products[product_id]
        last_replacement_str = product.get(CONF_LAST_REPLACEMENT_DATE)
        replacement_interval = product.get(CONF_REPLACEMENT_INTERVAL_DAYS)

        if not last_replacement_str or not replacement_interval:
            return None

        try:
            last_replacement = datetime.fromisoformat(last_replacement_str).date()
            next_replacement = last_replacement + timedelta(days=replacement_interval)
            today = datetime.now().date()
            days_until = (next_replacement - today).days
            return days_until
        except (ValueError, TypeError) as err:
            _LOGGER.error("Error calculating days until replacement: %s", err)
            return None


    async def replace_item(self, product_id: str) -> None:
        """Replace an item and update the last replacement date."""
        if product_id not in self._products:
            _LOGGER.error("Product %s not found", product_id)
            return

        # Decrease stock by 1
        current_stock = self._products[product_id].get(CONF_STOCK_QUANTITY, 0)
        new_stock = max(0, current_stock - 1)
        
        self._products[product_id][CONF_STOCK_QUANTITY] = new_stock
        self._products[product_id][CONF_LAST_REPLACEMENT_DATE] = datetime.now().date().isoformat()

        await self._async_save_products()
        await self.async_refresh()

    async def add_stock(self, product_id: str, quantity: int) -> None:
        """Add stock to a product."""
        if product_id not in self._products:
            _LOGGER.error("Product %s not found", product_id)
            return

        current_stock = self._products[product_id].get(CONF_STOCK_QUANTITY, 0)
        self._products[product_id][CONF_STOCK_QUANTITY] = current_stock + quantity

        await self._async_save_products()
        await self.async_refresh()

    async def remove_stock(self, product_id: str, quantity: int) -> None:
        """Remove stock from a product."""
        if product_id not in self._products:
            _LOGGER.error("Product %s not found", product_id)
            return

        current_stock = self._products[product_id].get(CONF_STOCK_QUANTITY, 0)
        new_stock = max(0, current_stock - quantity)
        self._products[product_id][CONF_STOCK_QUANTITY] = new_stock

        await self._async_save_products()
        await self.async_refresh()

    async def update_product(self, product_id: str, updates: dict[str, Any]) -> None:
        """Update product configuration."""
        if product_id not in self._products:
            _LOGGER.error("Product %s not found", product_id)
            return

        self._products[product_id].update(updates)

        await self._async_save_products()
        await self.async_refresh()

    async def add_product(self, product_data: dict[str, Any]) -> None:
        """Add a new product."""
        product_id = product_data[CONF_PRODUCT_ID]
        self._products[product_id] = product_data

        await self._async_save_products()
        await self.async_refresh()

    async def remove_product(self, product_id: str) -> None:
        """Remove a product."""
        if product_id in self._products:
            del self._products[product_id]
            await self._async_save_products()
            await self.async_refresh()


