#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyboard handling utilities for autoPyrseia
"""

import tkinter as tk


def bind_ctrl_a_select_all(widget, callback):
    """Bind Ctrl+A to select all functionality"""
    widget.bind('<Control-a>', callback)
    widget.bind('<Control-A>', callback)


class KeyboardHandlerMixin:
    """Mixin class for keyboard event handling"""
    
    def setup_keyboard_bindings(self):
        """Ρύθμιση πληκτρολογίου και συντομεύσεων"""
        # Global keyboard shortcuts
        self.root.bind('<Control-Key-1>', lambda e: self.notebook.select(0))  # Ctrl+1: Signal Processing
        self.root.bind('<Control-Key-2>', lambda e: self.notebook.select(1))  # Ctrl+2: USB Extraction
        self.root.bind('<Control-Key-3>', lambda e: self.notebook.select(2))  # Ctrl+3: Recipients Management
        
        # Tab switching with Ctrl+Tab
        self.root.bind('<Control-Tab>', self.next_tab)
        self.root.bind('<Control-Shift-Tab>', self.previous_tab)
        
        # Enter key for main action buttons
        self.root.bind('<Return>', self.handle_enter_key)
        self.root.bind('<KP_Enter>', self.handle_enter_key)  # Numeric keypad Enter
        
        # Escape key for canceling operations
        self.root.bind('<Escape>', self.handle_escape_key)
        
        # Ctrl+A for selecting all checkboxes
        self.root.bind('<Control-a>', self.select_all_checkboxes)
        self.root.bind('<Control-A>', self.select_all_checkboxes)
        
        # F5 for refresh operations
        self.root.bind('<F5>', self.handle_refresh_key)
        
        # Alt+A for adding recipient (Signal Processing tab)
        self.root.bind('<Alt-a>', self.handle_alt_a_key)
        self.root.bind('<Alt-A>', self.handle_alt_a_key)
        
        # Mouse wheel scrolling for canvas areas
        self.setup_mouse_wheel_scrolling()
    
    def next_tab(self, event=None):
        """Μετάβαση στην επόμενη καρτέλα"""
        current = self.notebook.index(self.notebook.select())
        next_tab = (current + 1) % self.notebook.index('end')
        self.notebook.select(next_tab)
        return 'break'
    
    def previous_tab(self, event=None):
        """Μετάβαση στην προηγούμενη καρτέλα"""
        current = self.notebook.index(self.notebook.select())
        prev_tab = (current - 1) % self.notebook.index('end')
        self.notebook.select(prev_tab)
        return 'break'
    
    def handle_enter_key(self, event=None):
        """Χειρισμός πλήκτρου Enter"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Signal Processing tab
            if hasattr(self, 'process_button') and self.process_button['state'] == 'normal':
                self.process_signal()
                return 'break'
        elif current_tab == 1:  # USB Extraction tab
            if hasattr(self, 'extract_button') and self.extract_button['state'] == 'normal':
                self.extract_to_usb()
                return 'break'
        
        # If focus is on an Entry widget, don't consume the event
        focused = self.root.focus_get()
        if isinstance(focused, tk.Entry):
            return None
        
        return 'break'
    
    def handle_escape_key(self, event=None):
        """Χειρισμός πλήκτρου Escape"""
        # Close any open dialogs (this will be handled by individual dialogs)
        # For now, just clear focus from current widget
        self.root.focus_set()
        return 'break'
    
    def select_all_checkboxes(self, event=None):
        """Επιλογή/αποεπιλογή όλων των checkboxes στην ενεργή καρτέλα"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Signal Processing tab
            checkboxes = getattr(self, 'recipients_checkboxes', [])
        elif current_tab == 1:  # USB Extraction tab
            checkboxes = getattr(self, 'extraction_checkboxes', [])
        elif current_tab == 2:  # Recipients Management tab
            checkboxes = getattr(self, 'manage_checkboxes', [])
        else:
            return 'break'
        
        if not checkboxes:
            return 'break'
        
        # Check if all are selected - if so, deselect all, otherwise select all
        all_selected = all(cb['var'].get() for cb in checkboxes)
        new_state = not all_selected
        
        for checkbox_data in checkboxes:
            checkbox_data['var'].set(new_state)
        
        return 'break'
    
    def handle_alt_a_key(self, event=None):
        """Handle Alt+A key for adding recipient in Signal Processing tab"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 0:  # Signal Processing tab
            if hasattr(self, 'signal_tab') and hasattr(self.signal_tab, 'add_recipient'):
                self.signal_tab.add_recipient()
                return 'break'
        
        return 'break'
    
    def handle_refresh_key(self, event=None):
        """Χειρισμός πλήκτρου F5 για ανανέωση"""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 1:  # USB Extraction tab
            if hasattr(self, 'refresh_extraction_list'):
                self.refresh_extraction_list()
        elif current_tab == 2:  # Recipients Management tab
            if hasattr(self, 'refresh_recipients_list'):
                self.refresh_recipients_list()
        
        return 'break'
    
    def setup_mouse_wheel_scrolling(self):
        """Ρύθμιση mouse wheel scrolling για canvas areas"""
        def bind_mousewheel(widget):
            """Bind mouse wheel events to a widget"""
            def _on_mousewheel(event):
                if hasattr(widget, 'yview_scroll'):
                    widget.yview_scroll(int(-1*(event.delta/120)), "units")
                return 'break'
            
            def _on_mousewheel_linux(event):
                if hasattr(widget, 'yview_scroll'):
                    if event.num == 4:
                        widget.yview_scroll(-1, "units")
                    elif event.num == 5:
                        widget.yview_scroll(1, "units")
                return 'break'
            
            # Windows and MacOS
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_mousewheel_linux)
            widget.bind("<Button-5>", _on_mousewheel_linux)
        
        # This will be called after canvas widgets are created
        if hasattr(self, 'root'):
            self.root.after(100, self.bind_wheel_to_canvas_widgets)
    
    def bind_wheel_to_canvas_widgets(self):
        """Bind mouse wheel scrolling to all canvas widgets"""
        def bind_mousewheel_to_canvas(canvas):
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                return 'break'
            
            def _on_mousewheel_linux(event):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
                return 'break'
            
            canvas.bind("<MouseWheel>", _on_mousewheel)
            canvas.bind("<Button-4>", _on_mousewheel_linux)
            canvas.bind("<Button-5>", _on_mousewheel_linux)
            
            # Also bind to the frame inside the canvas
            frame = canvas.winfo_children()[0] if canvas.winfo_children() else None
            if frame:
                frame.bind("<MouseWheel>", _on_mousewheel)
                frame.bind("<Button-4>", _on_mousewheel_linux)
                frame.bind("<Button-5>", _on_mousewheel_linux)
        
        # Find and bind all canvas widgets
        for widget_name in ['recipients_canvas', 'extraction_canvas', 'manage_canvas']:
            if hasattr(self, widget_name):
                canvas = getattr(self, widget_name)
                bind_mousewheel_to_canvas(canvas)
