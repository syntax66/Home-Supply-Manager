"""Number platform for Supply Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_PRODUCT_ID,
    CONF_PRODUCT_NAME,
    CONF_STOCK_QUANTITY,
    DOMAIN,
)
from .coordinator import SupplyManagerCoordinator
from .entity import SupplyManagerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Supply Manager numbers based on a config entry."""
    coordinator: SupplyManagerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SupplyManagerNumber] = []

    # Create stock number entity for each product
    for product_id in coordinator.data:
        entities.append(SupplyManagerStockNumber(coordinator, product_id))

    async_add_entities(entities)


class SupplyManagerNumber(SupplyManagerEntity, NumberEntity):
    """Base class for Supply Manager numbers."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, product_id)


class SupplyManagerStockNumber(SupplyManagerNumber):
    """Number entity to manage stock quantity."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the stock number."""
        super().__init__(coordinator, product_id)
        
        product = coordinator.data.get(product_id, {})
        product_name = product.get(CONF_PRODUCT_NAME, product_id)
        
        self._attr_unique_id = f"{product_id}_stock_number"
        self._attr_name = f"{product_name} Stock Quantity"
        self._attr_icon = "mdi:package-variant"
        self._attr_mode = NumberMode.BOX
        self._attr_native_min_value = 0
        self._attr_native_max_value = 999
        self._attr_native_step = 1

    @property
    def native_value(self) -> float:
        """Return the current stock quantity."""
        return float(self.product_data.get(CONF_STOCK_QUANTITY, 0))

    async def async_set_native_value(self, value: float) -> None:
        """Set the stock quantity."""
        new_stock = int(value)
        _LOGGER.info("Setting stock for %s to %d", self.product_id, new_stock)
        
        await self.coordinator.update_product(
            self.product_id,
            {CONF_STOCK_QUANTITY: new_stock}
        )








