"""
A modern inventory management application built with Python and the Tkinter library.

This application provides a graphical user interface (GUI) for users to manage
an inventory of items. It allows for adding, editing, deleting, searching, and
filtering items. The inventory can be saved to and loaded from a JSON file,
making it persistent across sessions.

The UI is designed to be sleek and modern, using a tabbed interface to keep
controls organized and compact, while maximizing space for the inventory table.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import json
import os
from datetime import datetime

# Import modular components
from models import Product
from managers.inventory_manager import InventoryManager
from utils.file_utils import FileUtils
from utils.ui_utils import UIUtils

# --- Color Scheme ---
# A centralized dictionary for a modern and consistent color palette.
COLORS = {
    'primary': '#2563eb', 'primary_dark': '#1d4ed8',      # Blue tones
    'secondary': '#64748b', 'secondary_dark': '#475569',  # Slate tones
    'success': '#059669', 'success_dark': '#047857',      # Green tones
    'warning': '#d97706', 'warning_dark': '#b45309',      # Orange tones
    'danger': '#dc2626', 'danger_dark': '#b91c1c',       # Red tones
    'light': '#f1f5f9',                                   # Light background
    'dark': '#1e293b',                                    # Dark text
    'white': '#ffffff',                                   # Card background
    'border': '#e2e8f0'                                   # Border for cards
}

# --- Two-Level Category Tree ---
CATEGORY_TREE = {
    # Main categories as keys, each with a list of subcategories
    "Raw Materials": ["Metals", "Plastics", "Chemicals", "Other"],
    "Components": ["Electronics", "Mechanical", "Optical", "Other"],
    "Finished Goods": ["Electronics", "Furniture", "Apparel", "Other"],
    "Consumables": ["Food", "Beverage", "Office Supplies", "Other"],
    "Perishables": ["Produce", "Dairy", "Meat", "Other"],
    "Equipment": ["IT", "Manufacturing", "Office", "Other"],
    "Supplies": ["Cleaning", "Packaging", "Safety", "Other"],
    "Packaging": ["Boxes", "Bottles", "Wrapping", "Other"],
    "Service": ["Repair", "Installation", "Delivery", "Consulting", "Other"],
    "Digital": ["Software", "eBook", "Media", "License", "Other"],
    "Subscription": ["SaaS", "Maintenance", "Membership", "Other"],
    "Booking": ["Event", "Rental", "Appointment", "Other"],
    "Training": ["Staff", "Customer", "Other"],
    "Maintenance": ["Equipment", "IT", "Other"],
    "Other": ["Other"]
}

# File where user-defined custom categories are stored
CUSTOM_CATEGORIES_FILE = os.path.join('datas', 'custom_categories.json')

# On startup, load custom categories and merge with CATEGORY_TREE
# This allows users to extend the category system without losing defaults

def load_custom_categories():
    # Loads user-defined categories from a JSON file if it exists
    if os.path.exists(CUSTOM_CATEGORIES_FILE):
        with open(CUSTOM_CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_custom_categories(custom_tree):
    # Saves the current custom category tree to disk
    with open(CUSTOM_CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_tree, f, indent=2)

# Merge default and custom trees
def get_full_category_tree():
    # Start with a copy of the default tree
    tree = {k: v[:] for k, v in CATEGORY_TREE.items()}
    custom = load_custom_categories()
    for main, subs in custom.items():
        if main not in tree:
            tree[main] = []
        for sub in subs:
            if sub not in tree[main]:
                tree[main].append(sub)
    return tree

CATEGORY_TREE = get_full_category_tree()

CATEGORY_DEFAULTS = {
    "Raw Materials": {"icon": "🪨", "color": "#8D5524"},
    "Components": {"icon": "🧩", "color": "#3B83BD"},
    "Finished Goods": {"icon": "📦", "color": "#F4A300"},
    "Consumables": {"icon": "🍎", "color": "#A3C644"},
    "Perishables": {"icon": "🥦", "color": "#6FCF97"},
    "Equipment": {"icon": "🛠️", "color": "#B5651D"},
    "Supplies": {"icon": "📑", "color": "#E67E22"},
    "Packaging": {"icon": "🎁", "color": "#E84393"},
    "Service": {"icon": "🛎️", "color": "#00B894"},
    "Digital": {"icon": "💾", "color": "#636EFA"},
    "Subscription": {"icon": "🔄", "color": "#00B8D9"},
    "Booking": {"icon": "📅", "color": "#FDCB6E"},
    "Training": {"icon": "🎓", "color": "#6D214F"},
    "Maintenance": {"icon": "🧰", "color": "#636E72"},
    "Other": {"icon": "🗂️", "color": "#B2BEC3"}
}

class ModernButton(ttk.Button):
    """A custom ttk.Button that uses a pre-defined modern style."""
    def __init__(self, parent, **kwargs):
        # The specific style (e.g., 'Success.TButton') is passed in kwargs.
        super().__init__(parent, **kwargs)

class EditItemDialog:
    """
    A modal dialog window for editing the details of an existing inventory item.
    
    This dialog is created when a user double-clicks an item or uses the 'Edit'
    button. It comes pre-filled with the item's current data and provides
    fields to modify the name, quantity, and category.
    """
    def __init__(self, parent, item_data, categories):
        """
        Initializes the EditItemDialog.

        Args:
            parent: The parent widget (the main application window).
            item_data (dict): A dictionary containing the data of the item to be edited.
            categories (list): A list of available categories for the dropdown.
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Item")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Keeps the dialog on top of the parent.
        self.dialog.grab_set()         # Makes the dialog modal.
        self.dialog.configure(bg=UIUtils.COLORS['white'])
        
        # Center the dialog relative to the parent window.
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.item_data = item_data
        self.categories = categories if categories else list(CATEGORY_TREE.keys())
        self.result = None  # Stores the edited data if the user saves.
        
        self.create_widgets()

    def create_widgets(self):
        """Creates and arranges all widgets within the dialog."""
        main_frame = ttk.Frame(self.dialog, padding="30", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = UIUtils.create_styled_label(main_frame, "✏️ Edit Item", 'title')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))

        # --- Input Fields ---
        # Name
        UIUtils.create_styled_label(main_frame, "Name:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.name_entry = UIUtils.create_styled_entry(main_frame, width=35)
        self.name_entry.grid(row=1, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.name_entry.insert(0, self.item_data['name']) # Pre-fill with existing data.

        # Quantity
        UIUtils.create_styled_label(main_frame, "Quantity:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.quantity_entry = UIUtils.create_styled_entry(main_frame, width=15)
        self.quantity_entry.grid(row=2, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.quantity_entry.insert(0, str(self.item_data['quantity'])) # Pre-fill

        # Main Category
        UIUtils.create_styled_label(main_frame, "Main Category:").grid(row=3, column=0, sticky=tk.W, pady=8)
        # Dropdown for main category, populated from CATEGORY_TREE keys
        self.main_category_combo = ttk.Combobox(main_frame, values=list(CATEGORY_TREE.keys()), width=32, state="normal", font=("Segoe UI", 10))
        self.main_category_combo.grid(row=3, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.main_category_combo.set(self.item_data['category_main']) # Pre-fill

        # Sub Category
        UIUtils.create_styled_label(main_frame, "Sub Category:").grid(row=4, column=0, sticky=tk.W, pady=8)
        # Dropdown for subcategory, dynamically populated based on main category
        self.sub_category_combo = ttk.Combobox(main_frame, values=CATEGORY_TREE.get(self.item_data['category_main'], []), width=32, state="normal", font=("Segoe UI", 10))
        self.sub_category_combo.grid(row=4, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.sub_category_combo.set(self.item_data['category_sub']) # Pre-fill

        # Description
        description_label = ttk.Label(main_frame, text="Description:")
        description_label.grid(row=5, column=0, sticky=tk.W, pady=8)
        self.description_entry = ttk.Entry(main_frame, width=35)
        self.description_entry.grid(row=5, column=1, padx=(15, 0), pady=8, sticky=tk.W)
        self.description_entry.insert(0, self.item_data.get('description', ''))

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(30, 0))

        save_button = UIUtils.create_styled_button(button_frame, "💾 Save Changes", self.save_changes, 'success')
        save_button.pack(side=tk.LEFT, padx=(0, 15))
        cancel_button = UIUtils.create_styled_button(button_frame, "❌ Cancel", self.cancel, 'secondary')
        cancel_button.pack(side=tk.LEFT)

        # --- Bindings and Focus ---
        self.dialog.bind('<Return>', lambda e: self.save_changes()) # Enter key to save.
        self.dialog.bind('<Escape>', lambda e: self.cancel())       # Escape key to cancel.
        self.name_entry.focus_set() # Set initial focus to the name field.

    def save_changes(self):
        """Validates the input data and, if valid, stores it and closes the dialog."""
        # Retrieve and strip whitespace from inputs.
        name = self.name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        main_category = self.main_category_combo.get()
        sub_category = self.sub_category_combo.get()
        description = self.description_entry.get().strip()
        
        # Basic validation.
        if not name or not quantity_str or not main_category:
            UIUtils.show_message("Error", "All fields are required.", 'error')
            return
            
        # Quantity validation.
        try:
            quantity = int(quantity_str)
            if quantity < 0: raise ValueError("Quantity cannot be negative")
        except ValueError:
            UIUtils.show_message("Error", "Quantity must be a positive integer.", 'error')
            return
            
        # Add new category to the session list if not present
        if main_category and main_category not in self.categories:
            self.categories.append(main_category)
            self.main_category_combo['values'] = self.categories
        
        # If validation passes, store the result.
        self.result = {'name': name, 'quantity': quantity, 'category_main': main_category, 'category_sub': sub_category, 'description': description}
        self.dialog.destroy() # Close the dialog.
        
    def cancel(self):
        """Closes the dialog without saving any changes."""
        self.dialog.destroy()

class InventoryApp:
    """
    The main class for the Inventory Management application.
    
    This class sets up the main window, defines all the UI styles and widgets,
    and contains all the logic for inventory operations like adding, editing,
    deleting, saving, and loading items.
    """
    def __init__(self, root):
        """
        Initializes the main application.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.title("📦 Sleek Inventory Manager")
        self.root.geometry("900x650")
        self.root.configure(bg=UIUtils.COLORS['light'])
        
        # Initialize inventory manager and file utilities
        self.inventory_manager = InventoryManager()
        self.file_utils = FileUtils()
        
        # Initialize styles, inventory list, and widgets.
        self.setup_styles()
        self.current_file = None # To track the path of the currently loaded file.
        
        self.create_widgets()

    def setup_styles(self):
        """Configures all the custom ttk styles for the application's modern look."""
        style = ttk.Style(self.root)
        # 'clam' theme is used because it's more customizable than the default theme.
        style.theme_use('clam')

        # General styles for frames and labels.
        style.configure('TFrame', background=UIUtils.COLORS['white'])
        style.configure('TLabel', background=UIUtils.COLORS['white'], foreground=UIUtils.COLORS['dark'], font=('Segoe UI', 9))
        style.configure('Card.TFrame', background=UIUtils.COLORS['white'], relief='solid', borderwidth=1, bordercolor=UIUtils.COLORS['gray'])
        style.configure('light.TFrame', background=UIUtils.COLORS['light']) # For the main background.

        # --- Button Styling ---
        # Defines a base style for all buttons and maps colors for different states.
        button_font = ('Segoe UI', 9, 'bold')
        button_padding = (10, 6)
        style.configure('TButton', font=button_font, padding=button_padding, borderwidth=0)
        # Ensures button text is always white.
        style.map('TButton', foreground=[('!active', UIUtils.COLORS['white'])])

        # Style for each button type (Primary, Success, etc.)
        style.configure('Primary.TButton', background=UIUtils.COLORS['primary'])
        style.map('Primary.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['primary'], 0.1))])
        
        style.configure('Success.TButton', background=UIUtils.COLORS['success'])
        style.map('Success.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['success'], 0.1))])
        
        style.configure('Warning.TButton', background=UIUtils.COLORS['warning'])
        style.map('Warning.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['warning'], 0.1))])
        
        style.configure('Danger.TButton', background=UIUtils.COLORS['danger'])
        style.map('Danger.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['danger'], 0.1))])
        
        style.configure('Secondary.TButton', background=UIUtils.COLORS['secondary'])
        style.map('Secondary.TButton', background=[('active', UIUtils.lighten_color(UIUtils.COLORS['secondary'], 0.1))])

        # --- Entry Styling ---
        style.configure('TEntry', fieldbackground=UIUtils.COLORS['white'], borderwidth=1, relief='solid')
        style.map('TEntry', bordercolor=[('focus', UIUtils.COLORS['accent'])])

        # --- Combobox Styling ---
        style.configure('TCombobox', fieldbackground=UIUtils.COLORS['white'], borderwidth=1, relief='solid')
        style.map('TCombobox', bordercolor=[('focus', UIUtils.COLORS['accent'])])

        # --- Treeview Styling ---
        style.configure('Treeview', 
                       background=UIUtils.COLORS['light'],
                       foreground=UIUtils.COLORS['dark'],
                       rowheight=25,
                       fieldbackground=UIUtils.COLORS['light'])
        style.configure('Treeview.Heading', 
                       background=UIUtils.COLORS['primary'],
                       foreground=UIUtils.COLORS['white'],
                       font=('Segoe UI', 9, 'bold'))

    def create_widgets(self):
        # Main vertical layout
        main_frame = ttk.Frame(self.root, style='light.TFrame', padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Compact summary label at the top ---
        self.summary_label = ttk.Label(main_frame, text="", style='TLabel', font=("Segoe UI", 9))
        self.summary_label.pack(fill=tk.X, padx=5, pady=(0, 2))

        # --- Notebook for tabs ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.create_add_tab(self.notebook)
        self.create_search_tab(self.notebook)
        self.create_actions_tab(self.notebook)

        # --- Inventory Table (main content, below tabs) ---
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        columns = ("ID", "Name", "Category", "Quantity", "Price", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=18)
        self._sort_orders = {col: False for col in columns}
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100 if col != "Description" else 180, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.update_table()

    def create_add_tab(self, notebook):
        add_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(add_frame, text="➕ Add Item")
        input_frame = ttk.Frame(add_frame)
        input_frame.pack(pady=5)
        UIUtils.create_styled_label(input_frame, "Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter item name", width=20)
        self.name_entry.grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Quantity:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.quantity_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter quantity", width=10)
        self.quantity_entry.grid(row=1, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Price:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.price_entry = UIUtils.create_styled_entry(input_frame, placeholder="Enter price", width=10)
        self.price_entry.grid(row=2, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Main Category:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.main_category_combo = ttk.Combobox(input_frame, values=list(CATEGORY_TREE.keys()), width=18, state="normal", font=("Segoe UI", 9))
        self.main_category_combo.grid(row=3, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        UIUtils.create_styled_label(input_frame, "Sub Category:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.sub_category_combo = ttk.Combobox(input_frame, values=CATEGORY_TREE.get(self.main_category_combo.get(), []), width=18, state="normal", font=("Segoe UI", 9))
        self.sub_category_combo.grid(row=4, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        # Add description label and entry
        description_label = ttk.Label(input_frame, text="Description:")
        description_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.description_entry = ttk.Entry(input_frame)
        self.description_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        add_button = UIUtils.create_styled_button(add_frame, "Add Item", self.add_item, 'success')
        add_button.pack(pady=5)

    def create_search_tab(self, notebook):
        search_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(search_frame, text="🔍 Search & Filter")
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(pady=5)
        UIUtils.create_styled_label(search_controls, "Search:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.search_entry = UIUtils.create_styled_entry(search_controls, placeholder="Search items...", width=18)
        self.search_entry.grid(row=0, column=1, padx=(5, 5), pady=2, sticky=tk.W)
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        UIUtils.create_styled_label(search_controls, "Main Category:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.filter_main_category = ttk.Combobox(search_controls, values=['All'] + list(CATEGORY_TREE.keys()), width=15, state="readonly", font=("Segoe UI", 9))
        self.filter_main_category.grid(row=0, column=3, padx=(5, 0), pady=2, sticky=tk.W)
        self.filter_main_category.set('All')
        self.filter_main_category.bind('<<ComboboxSelected>>', self.filter_items)
        UIUtils.create_styled_label(search_controls, "Sub Category:").grid(row=0, column=4, sticky=tk.W, pady=2)
        self.filter_sub_category = ttk.Combobox(search_controls, values=['All'] + list(CATEGORY_TREE.keys()), width=15, state="readonly", font=("Segoe UI", 9))
        self.filter_sub_category.grid(row=0, column=5, padx=(5, 0), pady=2, sticky=tk.W)
        self.filter_sub_category.set('All')
        self.filter_sub_category.bind('<<ComboboxSelected>>', self.filter_items)
        clear_button = UIUtils.create_styled_button(search_frame, "Clear Filters", self.clear_filters, 'secondary')
        clear_button.pack(pady=5)

    def create_actions_tab(self, notebook):
        actions_frame = ttk.Frame(notebook, style='Card.TFrame', padding=5)
        notebook.add(actions_frame, text="⚙️ Actions")
        file_frame = ttk.Frame(actions_frame)
        file_frame.pack(pady=5)
        save_button = UIUtils.create_styled_button(file_frame, "Save", self.save_inventory, 'primary')
        save_button.pack(side=tk.LEFT, padx=2, pady=2)
        load_button = UIUtils.create_styled_button(file_frame, "Load", self.load_inventory, 'secondary')
        load_button.pack(side=tk.LEFT, padx=2, pady=2)
        export_button = UIUtils.create_styled_button(file_frame, "Export for POS", self.export_for_pos, 'primary')
        export_button.pack(side=tk.LEFT, padx=2, pady=2)
        item_frame = ttk.Frame(actions_frame)
        item_frame.pack(pady=5)
        edit_button = UIUtils.create_styled_button(item_frame, "Edit Selected", self.edit_selected_item, 'primary')
        edit_button.pack(side=tk.LEFT, padx=2, pady=2)
        delete_button = UIUtils.create_styled_button(item_frame, "Delete Selected", self.delete_item, 'danger')
        delete_button.pack(side=tk.LEFT, padx=2, pady=2)
        clear_button = UIUtils.create_styled_button(item_frame, "Clear All", self.clear_entries, 'secondary')
        clear_button.pack(side=tk.LEFT, padx=2, pady=2)

    def add_item(self):
        """Adds a new item to the inventory."""
        name = self.name_entry.get().strip()
        quantity_str = self.quantity_entry.get().strip()
        price_str = self.price_entry.get().strip()
        main_category = self.main_category_combo.get()
        sub_category = self.sub_category_combo.get()
        description = self.description_entry.get().strip()

        # Validation
        if not name or not quantity_str or not price_str or not main_category:
            UIUtils.show_message("Error", "All fields are required.", 'error')
            return

        try:
            quantity = int(quantity_str)
            price = float(price_str)
            if quantity < 0 or price < 0:
                raise ValueError("Values cannot be negative")
        except ValueError:
            UIUtils.show_message("Error", "Quantity and price must be valid positive numbers.", 'error')
            return

        # Create product using the model
        product = Product(
            name=name,
            category_main=main_category,
            category_sub=sub_category,
            price=price,
            quantity=quantity,
            description=description
        )

        # Add to inventory manager
        success = self.inventory_manager.add_product(product)
        if success:
            self.update_table()
            self.clear_entries()
            UIUtils.show_message("Success", f"Item '{name}' added successfully!", 'info')
        else:
            UIUtils.show_message("Error", "Failed to add item. Please try again.", 'error')

    def update_table(self):
        """Updates the inventory table with current data."""
        self.tree.delete(*self.tree.get_children())
        total_items = 0
        total_value = 0.0
        for p in self.inventory_manager.get_all_products():
            total_items += 1
            total_value += (p.price or 0.0) * (p.quantity or 0)
            # Display both main and subcategory in the Category column for clarity
            self.tree.insert('', 'end', values=(p.product_id, p.name, f"{getattr(p, 'category_main', getattr(p, 'category', 'Uncategorized'))} - {getattr(p, 'category_sub', '')}", p.quantity, p.price, p.description))
        self.summary_label.config(text=f"Total Items: {total_items} | Total Value: ${total_value:.2f}")

    def filter_items(self, event=None):
        """Filters the inventory table based on search criteria."""
        search_term = self.search_entry.get().lower()
        main_category_filter = self.filter_main_category.get()
        sub_category_filter = self.filter_sub_category.get()

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filtered products
        products = self.inventory_manager.get_all_products()
        filtered_products = []

        for product in products:
            # Check search term
            if search_term and search_term not in product.name.lower():
                continue
            
            # Check main category filter (matches category_main, falls back to legacy category if needed)
            if main_category_filter != 'All' and getattr(product, 'category_main', getattr(product, 'category', 'Uncategorized')) != main_category_filter:
                continue
            
            # Check sub category filter (matches category_sub)
            if sub_category_filter != 'All' and getattr(product, 'category_sub', '') != sub_category_filter:
                continue
            
            filtered_products.append(product)

        # Add filtered items to table
        for product in filtered_products:
            total_value = product.price * product.quantity
            self.tree.insert('', 'end', values=(
                product.product_id,
                product.name,
                f"{getattr(product, 'category_main', getattr(product, 'category', 'Uncategorized'))} - {getattr(product, 'category_sub', '')}",
                product.quantity,
                UIUtils.format_currency(product.price),
                UIUtils.format_currency(total_value),
                UIUtils.format_date(getattr(product, 'last_updated', ''))
            ))

    def clear_filters(self):
        """Clears all search and filter criteria."""
        self.search_entry.delete(0, tk.END)
        self.filter_main_category.set('All')
        self.filter_sub_category.set('All')
        self.update_table()

    def clear_entries(self):
        """Clears all input fields in the add tab."""
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.main_category_combo.set('')
        self.sub_category_combo.set('')
        self.description_entry.delete(0, tk.END)

    def save_inventory(self):
        """Saves the current inventory to the current file."""
        if self.current_file:
            success = self.inventory_manager.save_to_json(self.current_file)
            if success:
                UIUtils.show_message("Success", "Inventory saved successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to save inventory.", 'error')
        else:
            self.save_inventory_as()

    def save_inventory_as(self):
        """Saves the inventory to a new file."""
        filename = self.file_utils.get_save_filename(
            "Save Inventory",
            [("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            success = self.inventory_manager.save_to_json(filename)
            if success:
                self.current_file = filename
                UIUtils.show_message("Success", "Inventory saved successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to save inventory.", 'error')

    def load_inventory(self):
        """Loads inventory from a file, auto-detecting format."""
        filename = self.file_utils.get_open_filename(
            "Load Inventory",
            [("All Supported", "*.json *.txt *.csv *.yaml *.yml"),
             ("JSON files", "*.json"),
             ("Text files", "*.txt"),
             ("CSV files", "*.csv"),
             ("YAML files", "*.yaml;*.yml"),
             ("All files", "*.*")]
        )
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext == ".json":
                success = self.inventory_manager.load_from_json(filename)
            elif ext == ".txt":
                success = self.inventory_manager.load_from_txt(filename)
            elif ext == ".csv":
                success = self.inventory_manager.load_from_csv(filename)
            elif ext in (".yaml", ".yml"):
                success = self.inventory_manager.load_from_yaml(filename)
            else:
                UIUtils.show_message("Error", "Unsupported file format.", 'error')
                return
            if success:
                self.current_file = filename
                self.update_table()
                UIUtils.show_message("Success", "Inventory loaded successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to load inventory.", 'error')

    def get_selected_item_data(self):
        """Gets the data of the currently selected item."""
        selection = self.tree.selection()
        if not selection:
            UIUtils.show_message("Warning", "Please select an item first.", 'warning')
            return None
        
        item_id = self.tree.item(selection[0])['values'][0]
        product = self.inventory_manager.get_product_by_id(item_id)
        
        if product:
            return {
                'id': product.product_id,
                'name': product.name,
                'category_main': getattr(product, 'category_main', getattr(product, 'category', 'Uncategorized')),
                'category_sub': getattr(product, 'category_sub', ''),
                'quantity': product.quantity,
                'price': product.price
            }
        return None

    def edit_selected_item(self):
        """Opens the edit dialog for the selected item."""
        item_data = self.get_selected_item_data()
        if item_data:
            self.edit_item(item_data, item_data['id'])

    def edit_item(self, item_data, item_id):
        """Opens the edit dialog and handles the editing process."""
        dialog = EditItemDialog(self.root, item_data, list(CATEGORY_TREE.keys()))
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Update the product
            product = Product(
                product_id=item_id,
                name=dialog.result['name'],
                category_main=dialog.result['category_main'],
                category_sub=dialog.result['category_sub'],
                price=item_data['price'],
                quantity=dialog.result['quantity'],
                description=dialog.result.get('description', '')
            )
            
            success = self.inventory_manager.update_product(product)
            if success:
                self.update_table()
                UIUtils.show_message("Success", "Item updated successfully!", 'info')
            else:
                UIUtils.show_message("Error", "Failed to update item.", 'error')

    def delete_item(self):
        """Deletes the selected item from the inventory."""
        item_data = self.get_selected_item_data()
        if item_data:
            confirm = UIUtils.show_message(
                "Confirm Delete",
                f"Are you sure you want to delete '{item_data['name']}'?",
                'question'
            )
            
            if confirm:
                success = self.inventory_manager.delete_product(item_data['id'])
                if success:
                    self.update_table()
                    UIUtils.show_message("Success", "Item deleted successfully!", 'info')
                else:
                    UIUtils.show_message("Error", "Failed to delete item.", 'error')

    def on_double_click(self, event):
        """Handles double-click events on the inventory table."""
        self.edit_selected_item()

    def export_for_pos(self):
        file_path = filedialog.asksaveasfilename(
            title="Export for POS",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            initialdir="datas/"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for p in self.inventory_manager.get_all_products():
                    # Use product_id or generate one if missing
                    pid = p.product_id or f"prod_{hash(p.name) % 10000}"
                    name = p.name or "Unknown"
                    price = p.price if hasattr(p, 'price') else 0.0
                    stock = p.quantity if hasattr(p, 'quantity') else 0
                    f.write(f"{pid}|{name}|{price}|{stock}\n")
            messagebox.showinfo("Export Complete", f"Exported products for POS import to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # Try to convert to float for numeric columns
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] != '' else float('-inf'), reverse=self._sort_orders[col])
        except ValueError:
            data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0], reverse=self._sort_orders[col])
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)
        self._sort_orders[col] = not self._sort_orders[col]

class CategoryManagerDialog(tk.Toplevel):
    def __init__(self, parent, category_tree, on_save):
        super().__init__(parent)
        self.title('Manage Categories')
        self.geometry('500x400')
        self.category_tree = category_tree
        self.on_save = on_save
        self.tree = ttk.Treeview(self, columns=('Color', 'Icon'))
        self.tree.heading('#0', text='Main Category')
        self.tree.heading('Color', text='Color')
        self.tree.heading('Icon', text='Icon')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.populate_tree()
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text='Add Main', command=self.add_main).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Add Sub', command=self.add_sub).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Rename', command=self.rename_cat).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Delete', command=self.delete_cat).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Set Color', command=self.set_color).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Set Icon', command=self.set_icon).pack(side='left', padx=5)
        ttk.Button(btn_frame, text='Save', command=self.save).pack(side='right', padx=5)
    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for main, subs in self.category_tree.items():
            main_id = self.tree.insert('', 'end', text=main, values=(self.get_color(main), self.get_icon(main)))
            for sub in subs:
                self.tree.insert(main_id, 'end', text=sub, values=(self.get_color(main, sub), self.get_icon(main, sub)))
    def get_color(self, main, sub=None):
        # Placeholder: return color from category data
        return ''
    def get_icon(self, main, sub=None):
        # Placeholder: return icon from category data
        return ''
    def add_main(self): pass
    def add_sub(self): pass
    def rename_cat(self): pass
    def delete_cat(self): pass
    def set_color(self): pass
    def set_icon(self): pass
    def save(self):
        self.on_save(self.category_tree)
        self.destroy()

def main():
    """Main function to run the application."""
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 