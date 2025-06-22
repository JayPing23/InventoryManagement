"""
UI utility functions for Inventory Management System.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from datetime import datetime, timedelta


class UIUtils:
    """Utility class for UI components and styling."""
    
    # Color scheme
    COLORS = {
        'primary': '#2c3e50',
        'secondary': '#34495e',
        'accent': '#3498db',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'light': '#ecf0f1',
        'dark': '#2c3e50',
        'white': '#ffffff',
        'gray': '#95a5a6'
    }
    
    @staticmethod
    def create_styled_button(parent: tk.Widget, text: str, command: Optional[Callable] = None, 
                           style: str = 'primary') -> tk.Button:
        """
        Create a styled button with consistent appearance.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Command function
            style: Button style ('primary', 'secondary', 'success', 'warning', 'danger')
            
        Returns:
            tk.Button: Styled button widget
        """
        colors = {
            'primary': (UIUtils.COLORS['primary'], UIUtils.COLORS['white']),
            'secondary': (UIUtils.COLORS['secondary'], UIUtils.COLORS['white']),
            'success': (UIUtils.COLORS['success'], UIUtils.COLORS['white']),
            'warning': (UIUtils.COLORS['warning'], UIUtils.COLORS['dark']),
            'danger': (UIUtils.COLORS['danger'], UIUtils.COLORS['white'])
        }
        
        bg_color, fg_color = colors.get(style, colors['primary'])
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            button['bg'] = UIUtils.lighten_color(bg_color, 0.1)
        
        def on_leave(e):
            button['bg'] = bg_color
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    @staticmethod
    def create_styled_entry(parent: tk.Widget, placeholder: str = "", width: int = 20) -> tk.Entry:
        """
        Create a styled entry widget.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            width: Entry width
            
        Returns:
            tk.Entry: Styled entry widget
        """
        entry = tk.Entry(
            parent,
            font=('Arial', 10),
            relief='solid',
            bd=1,
            width=width
        )
        
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=UIUtils.COLORS['gray'])
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=UIUtils.COLORS['dark'])
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=UIUtils.COLORS['gray'])
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        return entry
    
    @staticmethod
    def create_styled_label(parent: tk.Widget, text: str, style: str = 'normal') -> tk.Label:
        """
        Create a styled label widget.
        
        Args:
            parent: Parent widget
            text: Label text
            style: Label style ('normal', 'title', 'subtitle', 'error')
            
        Returns:
            tk.Label: Styled label widget
        """
        styles = {
            'normal': ('Arial', 10),
            'title': ('Arial', 16, 'bold'),
            'subtitle': ('Arial', 12, 'bold'),
            'error': ('Arial', 10)
        }
        
        font = styles.get(style, styles['normal'])
        fg = UIUtils.COLORS['danger'] if style == 'error' else UIUtils.COLORS['dark']
        
        return tk.Label(
            parent,
            text=text,
            font=font,
            fg=fg,
            bg=UIUtils.COLORS['white']
        )
    
    @staticmethod
    def create_styled_treeview(parent: tk.Widget, columns: list, height: int = 10) -> ttk.Treeview:
        """
        Create a styled treeview widget.
        
        Args:
            parent: Parent widget
            columns: List of column names
            height: Treeview height
            
        Returns:
            ttk.Treeview: Styled treeview widget
        """
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=height)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, width=100, anchor='center')
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', 
                       background=UIUtils.COLORS['light'],
                       foreground=UIUtils.COLORS['dark'],
                       rowheight=25,
                       fieldbackground=UIUtils.COLORS['light'])
        style.configure('Treeview.Heading', 
                       background=UIUtils.COLORS['primary'],
                       foreground=UIUtils.COLORS['white'],
                       font=('Arial', 10, 'bold'))
        
        return tree
    
    @staticmethod
    def show_message(title: str, message: str, message_type: str = 'info'):
        """
        Show a message box with consistent styling.
        
        Args:
            title: Message title
            message: Message content
            message_type: Type of message ('info', 'warning', 'error', 'question')
        """
        if message_type == 'info':
            messagebox.showinfo(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        elif message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'question':
            return messagebox.askyesno(title, message)
    
    @staticmethod
    def create_chart_frame(parent: tk.Widget, title: str) -> tuple:
        """
        Create a frame for matplotlib charts.
        
        Args:
            parent: Parent widget
            title: Chart title
            
        Returns:
            tuple: (frame, figure, canvas)
        """
        frame = tk.Frame(parent, bg=UIUtils.COLORS['white'])
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(UIUtils.COLORS['white'])
        ax.set_facecolor(UIUtils.COLORS['light'])
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        return frame, fig, canvas
    
    @staticmethod
    def lighten_color(color: str, factor: float) -> str:
        """
        Lighten a hex color by a factor.
        
        Args:
            color: Hex color string
            factor: Lightening factor (0-1)
            
        Returns:
            str: Lightened hex color
        """
        # Remove # if present
        color = color.lstrip('#')
        
        # Convert to RGB
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        
        # Convert back to hex
        return f'#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}'
    
    @staticmethod
    def create_scrollable_frame(parent: tk.Widget) -> tuple:
        """
        Create a scrollable frame.
        
        Args:
            parent: Parent widget
            
        Returns:
            tuple: (canvas, scrollable_frame)
        """
        canvas = tk.Canvas(parent, bg=UIUtils.COLORS['white'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UIUtils.COLORS['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        return canvas, scrollable_frame
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """
        Format amount as currency.
        
        Args:
            amount: Amount to format
            
        Returns:
            str: Formatted currency string
        """
        return f"${amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj: datetime) -> str:
        """
        Format date object as string.
        
        Args:
            date_obj: Date object
            
        Returns:
            str: Formatted date string
        """
        return date_obj.strftime("%Y-%m-%d %H:%M") 