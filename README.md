# 📦 Sleek Inventory Manager

A modern, feature-rich inventory management application built with Python and Tkinter. This tool provides a professional and user-friendly graphical interface to manage inventory, with a focus on a clean, compact, and efficient user experience.

![App Screenshot](https://i.imgur.com/YOUR_SCREENSHOT_URL.png) <!-- Replace with a real URL if you have one -->

## ✨ Features

-   **Modern & Sleek UI:** A professional and visually appealing interface built with a modern color scheme, clean fonts, and a compact layout.
-   **Tabbed Controls:** All actions are organized into a clean, tabbed panel (`Add Item`, `Search & Filter`, `File & Edit`) to save space and reduce clutter.
-   **Dynamic Inventory Table:** A large, expandable table that clearly displays all inventory items with columns for Name, Quantity, and Category.
-   **Add Items:** Easily add new items to the inventory with dedicated fields for name, quantity, and a comprehensive category dropdown.
-   **Edit Items:** Modify existing items by double-clicking an entry in the table or using the "Edit" button. This opens a clean, pre-filled dialog.
-   **Search & Filter:**
    -   **Live Search:** Instantly filter the inventory table by typing in the search bar.
    -   **Category Filter:** Narrow down the view by selecting a specific category from a dropdown.
-   **File Management:**
    -   **Load from File:** Use a file browser to open and load any `.json` or `.txt` inventory file.
    -   **Save & Save As:** Save changes to the current file or save the inventory to a new file anywhere on your system.
-   **Delete Items:** Securely delete one or more selected items with a confirmation dialog.
-   **Fully Documented Code:** The source code is extensively commented with docstrings and inline comments for easy readability and future modifications.

## 🚀 How to Run

1.  Ensure you have Python 3.10 or higher installed.
2.  Navigate to the project's root directory in your terminal.
3.  Run the application with the following command:
    ```bash
    python src/main.py
    ```
4.  The sample `inventory.txt` can be loaded to demonstrate functionality immediately.

## 📋 How to Use

-   **Adding an Item:**
    1.  Go to the **"➕ Add Item"** tab.
    2.  Fill in the `Name` and `Quantity` fields.
    3.  Select a `Category` from the dropdown list.
    4.  Click the **"Add Item"** button.

-   **Searching and Filtering:**
    1.  Go to the **"🔍 Search & Filter"** tab.
    2.  Type in the `Search by Name` box to see the table filter in real-time.
    3.  Select a category from the `Filter by Category` dropdown to further narrow the results.
    4.  Click **"Clear"** to reset all filters.

-   **File and Edit Actions:**
    1.  Go to the **"⚙️ File & Edit Actions"** tab.
    2.  **Load:** Click **"📂 Load"** to open a file browser and select an inventory file.
    3.  **Save:** Click **"💾 Save"** to save changes to the currently loaded file.
    4.  **Save As:** Click **"💾 Save As..."** to save the current inventory to a new file.
    5.  **Edit:** Select an item in the table and click **"✏️ Edit"**.
    6.  **Delete:** Select one or more items in the table and click **"🗑️ Delete"**. A confirmation will be required.

## 🛠️ Technology

-   **Language:** Python 3.10
-   **GUI:** Tkinter (with `ttk` for modern widgets)
-   **Data Storage:** JSON format (in `.json` or `.txt` files)
-   **Dependencies:** None! The application uses only Python's built-in libraries.

## 👤 Creator

-   **Danielle Aragon**
-   **Email:** jayparagon32@gmail.com 