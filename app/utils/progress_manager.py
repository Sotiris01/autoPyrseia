#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centralized progress management system for autoPyrseia
Prevents progress bar conflicts and provides smooth transitions
"""

import threading
import time
from queue import Queue, Empty
from dataclasses import dataclass
from typing import Optional, Callable


@dataclass
class ProgressUpdate:
    """Represents a progress update operation"""
    operation_id: str
    action: str  # 'update', 'message', 'reset', 'complete', 'smooth'
    value: Optional[float] = None
    message: Optional[str] = None
    duration_ms: Optional[int] = None


class ProgressManager:
    """Centralized manager for all progress bar operations"""
    
    def __init__(self, status_bar, root):
        self.status_bar = status_bar
        self.root = root
        self.queue = Queue()
        self.current_operation = None
        self.is_running = False
        self.lock = threading.Lock()
        
        # Animation state
        self.animation_timer = None
        self.is_animating = False
        
        # Start the progress processor
        self.start_processor()
    
    def start_processor(self):
        """Start the progress update processor"""
        self.is_running = True
        self.process_updates()
    
    def stop_processor(self):
        """Stop the progress update processor"""
        self.is_running = False
        if self.animation_timer:
            self.root.after_cancel(self.animation_timer)
    
    def process_updates(self):
        """Process queued progress updates"""
        if not self.is_running:
            return
            
        try:
            # Process all pending updates
            while True:
                try:
                    update = self.queue.get_nowait()
                    self._apply_update(update)
                except Empty:
                    break
        except Exception as e:
            print(f"Error processing progress updates: {e}")
        
        # Schedule next processing cycle
        self.root.after(50, self.process_updates)
    
    def _apply_update(self, update: ProgressUpdate):
        """Apply a single progress update"""
        with self.lock:
            # If another operation is active and this is a new operation, interrupt it
            if (self.current_operation and 
                update.operation_id != self.current_operation and 
                update.action in ['update', 'message', 'reset']):
                
                # Only interrupt if the new operation is not just a status message
                if update.action != 'message' or update.value is not None:
                    self.current_operation = update.operation_id
            
            # Set current operation if not set
            if not self.current_operation:
                self.current_operation = update.operation_id
            
            # Only process updates from current operation (except global messages)
            if (update.operation_id != self.current_operation and 
                update.action not in ['message'] or 
                (update.action == 'message' and update.value is not None)):
                return
            
            # Apply the update based on action type
            if update.action == 'update':
                self._update_progress(update.value, update.message)
                
            elif update.action == 'message':
                self._update_message(update.message, update.value)
                
            elif update.action == 'smooth':
                self._smooth_progress(update.value, update.duration_ms or 300)
                
            elif update.action == 'reset':
                self._reset_progress(update.message)
                self.current_operation = None
                
            elif update.action == 'complete':
                self._complete_progress(update.message)
                # Keep operation active briefly for completion message
                self.root.after(1000, self._clear_operation)
    
    def _update_progress(self, value: Optional[float], message: Optional[str]):
        """Update progress value and optionally message"""
        if value is not None:
            self.status_bar.update_progress(value)
        if message:
            self.status_bar.status_label.config(text=message)
            self.status_bar.parent.update_idletasks()
    
    def _update_message(self, message: str, progress: Optional[float]):
        """Update status message and optionally progress"""
        self.status_bar.status_label.config(text=message)
        if progress is not None:
            self.status_bar.update_progress(progress)
        self.status_bar.parent.update_idletasks()
    
    def _smooth_progress(self, target_value: float, duration_ms: int):
        """Smoothly animate progress to target value"""
        if self.is_animating:
            return  # Don't start new animation if one is running
            
        current_value = self.status_bar.status_progress['value']
        steps = max(10, int(duration_ms / 30))  # At least 10 steps, ~30ms per step
        step_size = (target_value - current_value) / steps
        step_delay = duration_ms // steps
        
        self.is_animating = True
        
        def animate_step(step):
            if not self.is_animating or step > steps:
                self.is_animating = False
                return
                
            new_value = current_value + (step_size * step)
            new_value = max(0, min(100, new_value))  # Clamp to 0-100
            
            self.status_bar.status_progress['value'] = new_value
            self.status_bar.percentage_label.config(text=f"{int(new_value)}%")
            self.status_bar.parent.update_idletasks()
            
            if step < steps:
                self.animation_timer = self.root.after(step_delay, lambda: animate_step(step + 1))
            else:
                self.is_animating = False
        
        animate_step(1)
    
    def _reset_progress(self, message: Optional[str]):
        """Reset progress bar to 0%"""
        if self.is_animating:
            self.is_animating = False
            if self.animation_timer:
                self.root.after_cancel(self.animation_timer)
        
        self.status_bar.status_progress['value'] = 0
        self.status_bar.percentage_label.config(text="0%")
        if message:
            self.status_bar.status_label.config(text=message)
        self.status_bar.parent.update_idletasks()
    
    def _complete_progress(self, message: Optional[str]):
        """Complete progress to 100%"""
        self._smooth_progress(100, 200)
        if message:
            # Delay message until animation completes
            self.root.after(200, lambda: self._update_message(message, None))
    
    def _clear_operation(self):
        """Clear current operation"""
        with self.lock:
            self.current_operation = None
    
    # Public API methods for other modules to use
    
    def start_operation(self, operation_id: str, message: str, initial_progress: float = 0):
        """Start a new progress operation"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='update',
            value=initial_progress,
            message=message
        )
        self.queue.put(update)
    
    def update_progress(self, operation_id: str, progress: float, message: Optional[str] = None):
        """Update progress for an operation"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='update',
            value=progress,
            message=message
        )
        self.queue.put(update)
    
    def smooth_progress(self, operation_id: str, target_progress: float, duration_ms: int = 300):
        """Smoothly animate progress to target value"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='smooth',
            value=target_progress,
            duration_ms=duration_ms
        )
        self.queue.put(update)
    
    def update_message(self, operation_id: str, message: str, progress: Optional[float] = None):
        """Update status message"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='message',
            message=message,
            value=progress
        )
        self.queue.put(update)
    
    def complete_operation(self, operation_id: str, message: str):
        """Complete an operation"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='complete',
            message=message
        )
        self.queue.put(update)
    
    def reset_progress(self, operation_id: str, message: Optional[str] = None):
        """Reset progress for an operation"""
        update = ProgressUpdate(
            operation_id=operation_id,
            action='reset',
            message=message
        )
        self.queue.put(update)
    
    def global_message(self, message: str):
        """Display a global message without changing current operation"""
        update = ProgressUpdate(
            operation_id='global',
            action='message',
            message=message
        )
        self.queue.put(update)
