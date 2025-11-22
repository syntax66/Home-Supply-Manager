"""The Supply Manager integration."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    CONF_PRODUCT_ID,
    DOMAIN,
    SERVICE_ADD_STOCK,
    SERVICE_REMOVE_STOCK,
    SERVICE_REPLACE_ITEM,
    SERVICE_UPDATE_PRODUCT,
    CONF_PRODUCT_NAME,
    CONF_STOCK_QUANTITY,
    CONF_REPLACEMENT_INTERVAL_DAYS,
    CONF_LAST_REPLACEMENT_DATE,
)
from .coordinator import SupplyManagerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON, Platform.NUMBER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Supply Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SupplyManagerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Supply Manager."""

    async def handle_replace_item(call: ServiceCall) -> None:
        """Handle the replace_item service call."""
        product_id = call.data[CONF_PRODUCT_ID]
        
        # Find the coordinator that contains this product
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, SupplyManagerCoordinator):
                if product_id in coord.data:
                    coordinator = coord
                    break
        
        if coordinator is None:
            _LOGGER.error("Product %s not found", product_id)
            return
        
        await coordinator.replace_item(product_id)

    async def handle_add_stock(call: ServiceCall) -> None:
        """Handle the add_stock service call."""
        product_id = call.data[CONF_PRODUCT_ID]
        quantity = call.data["quantity"]
        
        # Find the coordinator that contains this product
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, SupplyManagerCoordinator):
                if product_id in coord.data:
                    coordinator = coord
                    break
        
        if coordinator is None:
            _LOGGER.error("Product %s not found", product_id)
            return
        
        await coordinator.add_stock(product_id, quantity)

    async def handle_remove_stock(call: ServiceCall) -> None:
        """Handle the remove_stock service call."""
        product_id = call.data[CONF_PRODUCT_ID]
        quantity = call.data["quantity"]
        
        # Find the coordinator that contains this product
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, SupplyManagerCoordinator):
                if product_id in coord.data:
                    coordinator = coord
                    break
        
        if coordinator is None:
            _LOGGER.error("Product %s not found", product_id)
            return
        
        await coordinator.remove_stock(product_id, quantity)

    async def handle_update_product(call: ServiceCall) -> None:
        """Handle the update_product service call."""
        product_id = call.data[CONF_PRODUCT_ID]
        updates = {}
        
        if CONF_PRODUCT_NAME in call.data:
            updates[CONF_PRODUCT_NAME] = call.data[CONF_PRODUCT_NAME]
        if CONF_STOCK_QUANTITY in call.data:
            updates[CONF_STOCK_QUANTITY] = call.data[CONF_STOCK_QUANTITY]
        if CONF_REPLACEMENT_INTERVAL_DAYS in call.data:
            updates[CONF_REPLACEMENT_INTERVAL_DAYS] = call.data[CONF_REPLACEMENT_INTERVAL_DAYS]
        if CONF_LAST_REPLACEMENT_DATE in call.data:
            updates[CONF_LAST_REPLACEMENT_DATE] = call.data[CONF_LAST_REPLACEMENT_DATE]
        
        # Find the coordinator that contains this product
        coordinator = None
        for coord in hass.data[DOMAIN].values():
            if isinstance(coord, SupplyManagerCoordinator):
                if product_id in coord.data:
                    coordinator = coord
                    break
        
        if coordinator is None:
            _LOGGER.error("Product %s not found", product_id)
            return
        
        await coordinator.update_product(product_id, updates)

    # Register services only once
    if not hass.services.has_service(DOMAIN, SERVICE_REPLACE_ITEM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REPLACE_ITEM,
            handle_replace_item,
            schema=vol.Schema({
                vol.Required(CONF_PRODUCT_ID): cv.string,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_ADD_STOCK):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_STOCK,
            handle_add_stock,
            schema=vol.Schema({
                vol.Required(CONF_PRODUCT_ID): cv.string,
                vol.Required("quantity"): cv.positive_int,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REMOVE_STOCK):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REMOVE_STOCK,
            handle_remove_stock,
            schema=vol.Schema({
                vol.Required(CONF_PRODUCT_ID): cv.string,
                vol.Required("quantity"): cv.positive_int,
            }),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_PRODUCT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_UPDATE_PRODUCT,
            handle_update_product,
            schema=vol.Schema({
                vol.Required(CONF_PRODUCT_ID): cv.string,
                vol.Optional(CONF_PRODUCT_NAME): cv.string,
                vol.Optional(CONF_STOCK_QUANTITY): cv.positive_int,
                vol.Optional(CONF_REPLACEMENT_INTERVAL_DAYS): cv.positive_int,
                vol.Optional(CONF_LAST_REPLACEMENT_DATE): cv.string,
            }),
        )



