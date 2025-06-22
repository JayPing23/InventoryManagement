# Inventory Management System (IMS)

A modern, modular inventory management application built with Python and Tkinter. Designed for small businesses to track, analyze, and manage inventory with a clean GUI and robust features.

## Features
- **Inventory Management:** Add, edit, delete, and search products/items with automatic product ID generation and description fields
- **Two-Level Category System:** Main and subcategories for all items, with persistent custom categories, color-coding, and icons
- **Dashboard:** Tabbed analytics and charts (matplotlib)
- **Data Persistence:** All data stored in `datas/` (NoSQL-style: JSON, TXT, CSV, YAML supported)
- **Multi-Format Import/Export:** Load and save data in JSON, TXT, CSV, YAML; auto-detect file type; export/import for POS
- **POS Sync:** Import/export tangible items to/from Point of Sale system
- **Category Manager:** Hierarchical UI for managing categories, colors, and icons
- **Robust File Handling:** User-friendly error handling, auto-backup, and format conversion
- **Modern OOP Codebase:** SOLID principles, modular structure, easy to extend

## Folder Structure
```
InventoryManagement/
├── datas/              # All inventory and sales data files (JSON, demo data, etc.)
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── src/                # Source code (managers, models, utils)
└── ...                 # Virtualenv, git, IDE files, etc.
```

## Requirements
- Python 3.13.5 or newer
- pip (Python package manager)
- See `requirements.txt` for pip-installable dependencies:
  - matplotlib>=3.8.0
  - (Tkinter is included with Python)

## Installation
1. Clone or download this repository.
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
From the `InventoryManagement` directory, run:
```bash
python main.py
```

## Usage Guide
- All data is saved in the `datas/` folder. Demo data for various business types is included.
- Use the **Add Item** and **Edit Item** dialogs to manage inventory. Items support main/subcategory, color, and icon.
- Use the **Category Manager** (in item dialogs) to add/rename/delete categories, set colors/icons, and manage custom categories.
- Use the **Dashboard** tab for analytics and low stock alerts.
- Use the **Actions** tab to import/export inventory, including POS sync.
- Data files can be loaded/saved in JSON, TXT, CSV, or YAML. The system auto-detects file type.
- All demo data files are available in JSON format for easy import/export.

## Data Format
- Inventory items are stored as JSON objects with fields: `product_id`, `name`, `category_main`, `category_sub`, `quantity`, `price`, `description`, etc.
- Example:
```json
{
  "product_id": "GROC-0001",
  "name": "Apple",
  "category_main": "Consumables",
  "category_sub": "Food",
  "quantity": 120,
  "price": 0.50,
  "description": "Fresh red apples"
}
```

## Extensibility
- Add new business types by creating new demo data files in `datas/`.
- Extend categories, colors, and icons via the Category Manager UI or by editing `custom_categories.json`.
- Modular codebase: add new features or integrations in the `src/` directory.

## Troubleshooting
- If you encounter file format errors, ensure your data files match the expected JSON structure.
- For import/export issues, check file permissions and supported formats.
- For UI or category issues, reset custom categories via the Category Manager.

## Support
For issues or questions, please open an issue or contact the maintainer. 