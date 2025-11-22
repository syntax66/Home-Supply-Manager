"""Button platform for Supply Manager."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
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
    """Set up Supply Manager buttons based on a config entry."""
    coordinator: SupplyManagerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SupplyManagerButton] = []

    # Create replace button for each product
    for product_id in coordinator.data:
        entities.append(SupplyManagerReplaceButton(coordinator, product_id))

    async_add_entities(entities)


class SupplyManagerButton(SupplyManagerEntity, ButtonEntity):
    """Base class for Supply Manager buttons."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, product_id)


class SupplyManagerReplaceButton(SupplyManagerButton):
    """Button to replace a product and update stock."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the replace button."""
        super().__init__(coordinator, product_id)
        
        product = coordinator.data.get(product_id, {})
        product_name = product.get(CONF_PRODUCT_NAME, product_id)
        
        self._attr_unique_id = f"{product_id}_replace_button"
        self._attr_name = f"{product_name} Replace Item"
        self._attr_icon = "mdi:refresh"
        self._attr_device_class = ButtonDeviceClass.RESTART

    async def async_press(self) -> None:
        """Handle the button press."""
        product = self.product_data
        stock = product.get(CONF_STOCK_QUANTITY, 0)
        
        if stock <= 0:
            _LOGGER.warning(
                "Cannot replace item %s: stock is 0. Please add stock first.",
                self.product_id
            )
            return
        
        # Replace the item (this will decrease stock by 1 and update replacement date)
        await self.coordinator.replace_item(self.product_id)
        
        _LOGGER.info("Replaced item %s, new stock: %d", self.product_id, stock - 1)



