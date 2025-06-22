# Inventory Management System

A modern, modular inventory management application built with Python and Tkinter. Designed for small businesses to track, analyze, and manage inventory with a clean GUI and robust features.

## Features
- Inventory CRUD: Add, edit, delete, and search products
- Dashboard: Charts and analytics (matplotlib)
- Data persistence: All data stored in `datas/` (NoSQL-style, txt/json)
- File dialogs for import/export
- CSV export, low stock alerts
- Modular OOP codebase (SOLID principles)
- User-friendly error handling

## Folder Structure
```
InventoryManagement/
├── datas/              # All inventory and sales data files
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── src/                # Source code (managers, models, utils)
└── ...                 # Virtualenv, git, IDE files, etc.
```

## Requirements
- Python 3.13.5
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

## Usage Notes
- All data is saved in the `datas/` folder.
- Use the dashboard for analytics and low stock alerts.
- For best results, use Python 3.13.5 or newer.

## Support
For issues or questions, please open an issue or contact the maintainer. 