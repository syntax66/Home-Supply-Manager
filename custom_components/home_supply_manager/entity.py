"""Base entity for Supply Manager."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ICON, DEFAULT_ICON, DOMAIN
from .coordinator import SupplyManagerCoordinator


class SupplyManagerEntity(CoordinatorEntity[SupplyManagerCoordinator]):
    """Base entity for Supply Manager."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.product_id = product_id
        
        product = coordinator.data.get(product_id, {})
        product_name = product.get("product_name", product_id)
        product_icon = product.get(CONF_ICON, DEFAULT_ICON)
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, product_id)},
            name=product_name,
            manufacturer="Home Supply Manager",
            entry_type=DeviceEntryType.SERVICE,
        )



    @property
    def product_data(self) -> dict:
        """Return product data."""
        return self.coordinator.data.get(self.product_id, {})



