# 🏠 Home Supply Manager

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/syntax66/home-supply-manager.svg)](https://github.com/syntax66/home-supply-manager/releases)
[![License](https://img.shields.io/github/license/syntax66/home-supply-manager.svg)](LICENSE)

A Home Assistant integration for tracking and managing replaceable household items like filters, batteries, and other consumables. Never forget to replace your water filter or order new supplies again!

## ✨ Features

- 📦 **One Product per Entry** - Each product is its own integration entry (Device)
- ⏱️ **Smart Tracking** - Automatic calculation of days until replacement
- 📊 **Stock Management** - Monitor inventory levels with number entities
- 🔘 **Quick Actions** - One-click replacement button with automatic stock updates

## 🚀 Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/syntax66/home-supply-manager` as an Integration
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/supply_manager` directory to your `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via the UI

## 📝 Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for **"Home Supply Manager"**
4. Follow the configuration wizard to add your product

### Product Configuration

- **Product Name**: Descriptive name (e.g., "Water Filter")
- **Stock Quantity**: How many you have on hand
- **Replacement Interval**: Days between replacements
- **Last Replacement Date**: When it was last replaced

## 🎮 Usage

### Managing Products

Each product is a separate entry. To edit a product:
1. Go to **Settings** → **Devices & Services** → **Home Supply Manager**
2. Click the **CONFIGURE** (gear icon) button on the specific product entry
3. Update the settings in the dialog

### Entities Created

For each product, the integration creates:

#### Sensors
- `sensor.{product_name}_days_until_replacement` - Days until next replacement
- `sensor.{product_name}_stock` - Current stock quantity

#### Controls
- `button.{product_name}_replace_item` - Mark as replaced (decreases stock by 1)
- `number.{product_name}_stock_quantity` - Manually adjust stock

### Services

#### `supply_manager.replace_item`
Mark a product as replaced.

```yaml
service: supply_manager.replace_item
data:
  product_id: water_filter
```

#### `supply_manager.add_stock`
Add items to stock.

```yaml
service: supply_manager.add_stock
data:
  product_id: water_filter
  quantity: 3
```

#### `supply_manager.remove_stock`
Remove items from stock.

```yaml
service: supply_manager.remove_stock
data:
  product_id: water_filter
  quantity: 1
```

#### `supply_manager.update_product`
Update product configuration.

```yaml
service: supply_manager.update_product
data:
  product_id: water_filter
  product_name: "New Name"
  stock_quantity: 5
  replacement_interval_days: 90
  last_replacement_date: "2024-01-15"
```

## 🤖 Automation Examples

### Low Stock Alert

```yaml
automation:
  - alias: "Alert: Low Stock"
    trigger:
      - platform: numeric_state
        entity_id: sensor.water_filter_stock
        below: 2
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Low Stock Alert"
          message: "Water filter stock is low! Only {{ states('sensor.water_filter_stock') }} left."
```

### Replacement Reminder

```yaml
automation:
  - alias: "Reminder: Replace Water Filter"
    trigger:
      - platform: numeric_state
        entity_id: sensor.water_filter_days_until_replacement
        below: 1
    action:
      - service: notify.mobile_app
        data:
          title: "🔔 Time to Replace"
          message: "It's time to replace your water filter!"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ for the Home Assistant community
