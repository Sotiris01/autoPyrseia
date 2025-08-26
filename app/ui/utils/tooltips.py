#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooltip utilities for autoPyrseia
"""

import tkinter as tk


class ToolTip:
    """Κλάση για τη δημιουργία tooltips"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)
    
    def on_enter(self, event):
        """Εμφάνιση tooltip"""
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        self.tooltip.configure(bg='#2c3e50')
        
        label = tk.Label(self.tooltip, text=self.text, bg='#2c3e50', fg='white', 
                       font=('Arial', 9), relief='solid', bd=1, padx=5, pady=2)
        label.pack()
    
    def on_leave(self, event):
        """Απόκρυψη tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


def create_tooltip(widget, text):
    """Δημιουργία tooltip για ένα widget"""
    return ToolTip(widget, text)
