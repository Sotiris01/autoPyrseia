#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status bar widget with progress bar for autoPyrseia
"""

import tkinter as tk
from tkinter import ttk


class StatusBar:
    """Status bar with progress indicator"""
    
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        """Δημιουργία της γραμμής κατάστασης με progress bar"""
        self.status_frame = tk.Frame(self.parent, relief='sunken', bd=1, bg='#f0f0f0')
        self.status_frame.pack(side='bottom', fill='x')
        
        # Top row με το μήνυμα και τον δημιουργό
        top_row = tk.Frame(self.status_frame, bg='#f0f0f0')
        top_row.pack(fill='x', padx=5, pady=2)
        
        self.status_label = tk.Label(top_row, text="Έτοιμο - Αναμονή για νέο σήμα...", 
                                    font=('Arial', 9), anchor='w', bg='#f0f0f0')
        self.status_label.pack(side='left')
        
        # Δημιουργός
        creator_label = tk.Label(top_row, text="Δημιουργός: Σωτήριος Μπαλατσιάς | Υποστήριξη: 6983733346", 
                                font=('Arial', 9), anchor='e', fg='#7f8c8d', bg='#f0f0f0')
        creator_label.pack(side='right')
        
        # Bottom row με το progress bar
        bottom_row = tk.Frame(self.status_frame, bg='#f0f0f0')
        bottom_row.pack(fill='x', padx=5, pady=(0, 2))
        
        # Progress bar που πάει από 0 έως 100%
        self.status_progress = ttk.Progressbar(bottom_row, mode='determinate', length=400)
        self.status_progress.pack(side='left', fill='x', expand=True)
        self.status_progress['value'] = 0  # Start at 0%
        
        # Percentage label
        self.percentage_label = tk.Label(bottom_row, text="0%", 
                                        font=('Arial', 8), fg='#666666', bg='#f0f0f0', width=5)
        self.percentage_label.pack(side='right', padx=(5, 0))
    
    def update_status(self, message, progress=None):
        """Ενημέρωση του status bar με μήνυμα και προαιρετικό progress"""
        self.status_label.config(text=message)
        if progress is not None:
            self.update_progress(progress)
        self.parent.update_idletasks()
    
    def update_progress(self, value):
        """Ενημέρωση του progress bar (0-100)"""
        self.status_progress['value'] = value
        self.percentage_label.config(text=f"{int(value)}%")
        self.parent.update_idletasks()
    
    def smooth_progress_to(self, target_value, duration_ms=300):
        """Ομαλή μετάβαση του progress bar σε μια τιμή"""
        current_value = self.status_progress['value']
        steps = 10  # Αριθμός βημάτων για την ομαλή μετάβαση
        step_size = (target_value - current_value) / steps
        step_delay = duration_ms // steps
        
        def animate_step(step):
            if step <= steps:
                new_value = current_value + (step_size * step)
                self.status_progress['value'] = new_value
                self.percentage_label.config(text=f"{int(new_value)}%")
                self.parent.update_idletasks()
                
                if step < steps:
                    self.parent.after(step_delay, lambda: animate_step(step + 1))
        
        animate_step(1)
    
    def reset_progress(self):
        """Επαναφορά του progress bar στο 0%"""
        self.status_progress['value'] = 0
        self.percentage_label.config(text="0%")
        self.parent.update_idletasks()
    
    def complete_progress(self):
        """Ολοκλήρωση του progress bar στο 100%"""
        self.smooth_progress_to(100, 200)  # Ομαλή μετάβαση στο 100%
