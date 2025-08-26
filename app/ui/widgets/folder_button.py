#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Folder icon button widget for autoPyrseia
"""

import tkinter as tk
import os
from pathlib import Path
from tkinter import messagebox
from ..utils.tooltips import create_tooltip
from ...utils.path_manager import get_path_manager


class FolderIconButton:
    """A reusable folder icon button widget"""
    
    @staticmethod
    def create(parent, recipient_name, status_callback=None):
        """
        Create a folder icon button for a recipient
        
        Args:
            parent: Parent widget
            recipient_name: Name of the recipient folder to open
            status_callback: Optional callback function to update status
        
        Returns:
            tkinter.Button: The created folder button
        """
        def open_folder():
            try:
                path_manager = get_path_manager()
                folder_path = path_manager.get_recipient_folder(recipient_name)
                
                if folder_path.exists() and folder_path.is_dir():
                    # Use os.startfile on Windows to open folder in File Explorer
                    os.startfile(str(folder_path))
                    if status_callback:
                        status_callback(f"Άνοιξε ο φάκελος: {recipient_name}")
                else:
                    messagebox.showwarning("Φάκελος Δεν Βρέθηκε", 
                                         f"Ο φάκελος '{recipient_name}' δεν βρέθηκε στο DATA/")
                    if status_callback:
                        status_callback(f"Ο φάκελος {recipient_name} δεν υπάρχει")
            except Exception as e:
                messagebox.showerror("Σφάλμα", f"Αδυναμία ανοίγματος φακέλου: {str(e)}")
                if status_callback:
                    status_callback(f"Σφάλμα ανοίγματος φακέλου: {recipient_name}")
        
        button = tk.Button(parent, 
                          text="📁", 
                          font=('Arial', 12),
                          width=3,
                          height=1,
                          relief='flat',
                          bg='#ecf0f1',
                          fg='#2c3e50',
                          cursor='hand2',
                          command=open_folder)
        
        # Hover effects
        def on_enter(event):
            button.config(bg='#d5dbdb', relief='raised')
        
        def on_leave(event):
            button.config(bg='#ecf0f1', relief='flat')
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        # Tooltip
        create_tooltip(button, "Άνοιγμα φακέλου")
        
        return button
