"""Sensor platform for Supply Manager."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_IS_CYCLICAL,
    CONF_LAST_REPLACEMENT_DATE,
    CONF_PRODUCT_ID,
    CONF_PRODUCT_NAME,
    CONF_REPLACEMENT_INTERVAL_DAYS,
    CONF_STOCK_QUANTITY,
    DOMAIN,
    ICON_CALENDAR,
    ICON_PACKAGE,
    SENSOR_TYPE_DAYS_UNTIL_REPLACEMENT,
    SENSOR_TYPE_STOCK,
)
from .coordinator import SupplyManagerCoordinator
from .entity import SupplyManagerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Supply Manager sensors based on a config entry."""
    coordinator: SupplyManagerCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SupplyManagerSensor] = []

    # Create sensors for each product
    # Create sensors for each product
    for product_id in coordinator.data:
        product_data = coordinator.data[product_id]
        is_cyclical = product_data.get(CONF_IS_CYCLICAL, True)
        
        sensors = [SupplyManagerStockSensor(coordinator, product_id)]
        
        if is_cyclical:
            sensors.append(SupplyManagerDaysUntilReplacementSensor(coordinator, product_id))
            
        entities.extend(sensors)

    async_add_entities(entities)


class SupplyManagerSensor(SupplyManagerEntity, SensorEntity):
    """Base class for Supply Manager sensors."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, product_id)
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{product_id}_{sensor_type}"


class SupplyManagerDaysUntilReplacementSensor(SupplyManagerSensor):
    """Sensor for days until next replacement."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, product_id, SENSOR_TYPE_DAYS_UNTIL_REPLACEMENT)
        
        product = coordinator.data.get(product_id, {})
        product_name = product.get(CONF_PRODUCT_NAME, product_id)
        
        self._attr_name = f"{product_name} Days Until Replacement"
        self._attr_icon = ICON_CALENDAR
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.calculate_days_until_replacement(self.product_id)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        product = self.product_data
        last_replacement_str = product.get(CONF_LAST_REPLACEMENT_DATE)
        replacement_interval = product.get(CONF_REPLACEMENT_INTERVAL_DAYS)

        attributes = {
            "product_id": self.product_id,
            "last_replacement_date": last_replacement_str,
            "replacement_interval_days": replacement_interval,
        }

        if last_replacement_str and replacement_interval:
            try:
                last_replacement = datetime.fromisoformat(last_replacement_str).date()
                next_replacement = last_replacement + timedelta(days=replacement_interval)
                attributes["next_replacement_date"] = next_replacement.isoformat()
            except (ValueError, TypeError):
                pass

        return attributes


class SupplyManagerStockSensor(SupplyManagerSensor):
    """Sensor for current stock quantity."""

    def __init__(
        self,
        coordinator: SupplyManagerCoordinator,
        product_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, product_id, SENSOR_TYPE_STOCK)
        
        product = coordinator.data.get(product_id, {})
        product_name = product.get(CONF_PRODUCT_NAME, product_id)
        
        self._attr_name = f"{product_name} Stock"
        self._attr_icon = ICON_PACKAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.product_data.get(CONF_STOCK_QUANTITY, 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        product = self.product_data
        
        return {
            "product_id": self.product_id,
            "product_name": product.get(CONF_PRODUCT_NAME),
            "replacement_interval_days": product.get(CONF_REPLACEMENT_INTERVAL_DAYS),
            "last_replacement_date": product.get(CONF_LAST_REPLACEMENT_DATE),
            "out_of_stock": self.native_value <= 0,
        }



