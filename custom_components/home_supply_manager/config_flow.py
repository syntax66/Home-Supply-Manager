"""Config flow for Supply Manager integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

from .const import (
    CONF_ICON,
    CONF_LAST_REPLACEMENT_DATE,
    CONF_PRODUCT_ID,
    CONF_PRODUCT_NAME,
    CONF_REPLACEMENT_INTERVAL_DAYS,
    CONF_STOCK_QUANTITY,
    DEFAULT_ICON,
    DEFAULT_REPLACEMENT_INTERVAL_DAYS,
    DEFAULT_STOCK_QUANTITY,
    DOMAIN,
)
from .coordinator import SupplyManagerCoordinator

_LOGGER = logging.getLogger(__name__)


class SupplyManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Supply Manager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Generate product_id from product_name
            product_id = user_input[CONF_PRODUCT_NAME].lower().replace(" ", "_")
            product_id = "".join(c for c in product_id if c.isalnum() or c == "_")

            # Validate date format
            try:
                datetime.fromisoformat(user_input[CONF_LAST_REPLACEMENT_DATE])
            except ValueError:
                errors[CONF_LAST_REPLACEMENT_DATE] = "invalid_date"

            if not errors:
                # Set unique_id based on product_id to prevent duplicates
                await self.async_set_unique_id(product_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=user_input[CONF_PRODUCT_NAME],
                    data={
                        CONF_PRODUCT_ID: product_id,
                        CONF_PRODUCT_NAME: user_input[CONF_PRODUCT_NAME],
                        CONF_STOCK_QUANTITY: user_input[CONF_STOCK_QUANTITY],
                        CONF_REPLACEMENT_INTERVAL_DAYS: user_input[
                            CONF_REPLACEMENT_INTERVAL_DAYS
                        ],
                        CONF_LAST_REPLACEMENT_DATE: user_input[
                            CONF_LAST_REPLACEMENT_DATE
                        ],
                        CONF_LAST_REPLACEMENT_DATE: user_input[
                            CONF_LAST_REPLACEMENT_DATE
                        ],
                    },
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_PRODUCT_NAME): cv.string,
                # Icon selection removed
                vol.Required(
                    CONF_STOCK_QUANTITY, default=DEFAULT_STOCK_QUANTITY
                ): cv.positive_int,
                vol.Required(
                    CONF_REPLACEMENT_INTERVAL_DAYS,
                    default=DEFAULT_REPLACEMENT_INTERVAL_DAYS,
                ): cv.positive_int,
                vol.Required(
                    CONF_LAST_REPLACEMENT_DATE,
                    default=datetime.now().date().isoformat(),
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SupplyManagerOptionsFlow:
        """Get the options flow for this handler."""
        return SupplyManagerOptionsFlow(config_entry)


class SupplyManagerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Supply Manager."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - edit product."""
        coordinator: SupplyManagerCoordinator = self.hass.data[DOMAIN][
            self.config_entry.entry_id
        ]
        
        # Get the single product ID for this entry
        product_id = self.config_entry.data.get(CONF_PRODUCT_ID)
        if not product_id:
            return self.async_abort(reason="no_product_id")

        product_data = coordinator.data.get(product_id, {})
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate date format
            try:
                datetime.fromisoformat(user_input[CONF_LAST_REPLACEMENT_DATE])
            except ValueError:
                errors[CONF_LAST_REPLACEMENT_DATE] = "invalid_date"
            
            if not errors:
                # Update product
                await coordinator.update_product(
                    product_id,
                    {
                        CONF_PRODUCT_NAME: user_input[CONF_PRODUCT_NAME],
                        CONF_STOCK_QUANTITY: user_input[CONF_STOCK_QUANTITY],
                        CONF_REPLACEMENT_INTERVAL_DAYS: user_input[
                            CONF_REPLACEMENT_INTERVAL_DAYS
                        ],
                        CONF_LAST_REPLACEMENT_DATE: user_input[
                            CONF_LAST_REPLACEMENT_DATE
                        ],
                        CONF_LAST_REPLACEMENT_DATE: user_input[
                            CONF_LAST_REPLACEMENT_DATE
                        ],
                    },
                )
                
                return self.async_create_entry(title="", data={})
        
        # Show form with current values
        data_schema = vol.Schema({
            vol.Required(
                CONF_PRODUCT_NAME,
                default=product_data.get(CONF_PRODUCT_NAME, ""),
            ): cv.string,
            # Icon selection removed
            vol.Required(
                CONF_STOCK_QUANTITY,
                default=product_data.get(CONF_STOCK_QUANTITY, DEFAULT_STOCK_QUANTITY),
            ): cv.positive_int,
            vol.Required(
                CONF_REPLACEMENT_INTERVAL_DAYS,
                default=product_data.get(
                    CONF_REPLACEMENT_INTERVAL_DAYS,
                    DEFAULT_REPLACEMENT_INTERVAL_DAYS,
                ),
            ): cv.positive_int,
            vol.Required(
                CONF_LAST_REPLACEMENT_DATE,
                default=product_data.get(
                    CONF_LAST_REPLACEMENT_DATE,
                    datetime.now().date().isoformat(),
                ),
            ): cv.string,
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )



