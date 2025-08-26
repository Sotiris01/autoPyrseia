"""
Multi-Day Daily History Manager - Keeps history for all days
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class DailyHistoryManager:
    """Multi-day history manager - preserves all days' history"""
    
    def __init__(self):
        self.history_file = Path("history.json")
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.current_viewing_date = self.today
        
        # Load all history data
        self.all_history = self._load_all_history()
        
        # Clean up old history (keep only last 30 days)
        self._cleanup_old_history()
        
        # Ensure today's entry exists
        if self.today not in self.all_history:
            self.all_history[self.today] = []
    
    def _load_all_history(self):
        """Load all historical data from file"""
        if not self.history_file.exists():
            return {}
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this is old format (single day)
            if 'date' in data and 'entries' in data:
                # Convert old format to new multi-day format
                old_date = data['date']
                old_entries = data['entries']
                return {old_date: old_entries} if old_entries else {}
            
            # New format - return as is
            return data if isinstance(data, dict) else {}
            
        except Exception as e:
            print(f"Error loading history: {e}")
            return {}
    
    def _save_all_history(self):
        """Save all history data to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _cleanup_old_history(self):
        """Remove history entries older than 30 days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Get all dates in history
            dates_to_remove = []
            for date_str in self.all_history.keys():
                if date_str < cutoff_date:
                    dates_to_remove.append(date_str)
            
            # Remove old dates
            removed_count = 0
            for date_str in dates_to_remove:
                removed_entries = len(self.all_history[date_str])
                del self.all_history[date_str]
                removed_count += removed_entries
            
            # Save cleaned history if anything was removed
            if removed_count > 0:
                print(f"Cleaned up {removed_count} old history entries from {len(dates_to_remove)} days")
                self._save_all_history()
                
        except Exception as e:
            print(f"Error during history cleanup: {e}")
    
    def add_processed_signal(self, signal_id, fm, recipients):
        """Add a processed signal entry to today's history"""
        entry = {
            'type': 'processed',
            'date': self.today,
            'time': datetime.now().strftime("%H:%M:%S"),
            'signal_id': signal_id,
            'fm': fm,
            'recipients': recipients if isinstance(recipients, str) else ', '.join(recipients)
        }
        
        if self.today not in self.all_history:
            self.all_history[self.today] = []
        
        self.all_history[self.today].append(entry)
        self._save_all_history()
        
        # Periodically cleanup old history (every 10th entry to avoid performance impact)
        if len(self.all_history[self.today]) % 10 == 0:
            self._cleanup_old_history()
    
    def add_extracted_recipient(self, recipient, signal_count, file_number=None):
        """Add an extracted recipient entry to today's history"""
        entry = {
            'type': 'extracted',
            'date': self.today,
            'time': datetime.now().strftime("%H:%M:%S"),
            'recipient': recipient,
            'signal_count': signal_count,
            'file_number': file_number
        }
        
        if self.today not in self.all_history:
            self.all_history[self.today] = []
        
        self.all_history[self.today].append(entry)
        self._save_all_history()
    
    def get_processed_signals(self, date=None):
        """Get processed signals for specified date (default: current viewing date)"""
        target_date = date or self.current_viewing_date
        entries = self.all_history.get(target_date, [])
        return [entry for entry in entries if entry.get('type') == 'processed']
    
    def get_extracted_recipients(self, date=None):
        """Get extracted recipients for specified date (default: current viewing date)"""
        target_date = date or self.current_viewing_date
        entries = self.all_history.get(target_date, [])
        return [entry for entry in entries if entry.get('type') == 'extracted']
    
    def get_available_dates(self):
        """Get list of all available dates with history, sorted newest first"""
        dates = [date for date, entries in self.all_history.items() if entries]
        return sorted(dates, reverse=True)
    
    def set_viewing_date(self, date):
        """Set the date for which to view history"""
        self.current_viewing_date = date
    
    def get_current_viewing_date(self):
        """Get the currently selected viewing date"""
        return self.current_viewing_date
    
    def navigate_to_previous_day(self):
        """Navigate to previous available day with history"""
        available_dates = self.get_available_dates()
        if not available_dates:
            return False
        
        current_index = available_dates.index(self.current_viewing_date) if self.current_viewing_date in available_dates else -1
        
        if current_index < len(available_dates) - 1:
            self.current_viewing_date = available_dates[current_index + 1]
            return True
        return False
    
    def navigate_to_next_day(self):
        """Navigate to next available day with history"""
        available_dates = self.get_available_dates()
        if not available_dates:
            return False
        
        current_index = available_dates.index(self.current_viewing_date) if self.current_viewing_date in available_dates else -1
        
        if current_index > 0:
            self.current_viewing_date = available_dates[current_index - 1]
            return True
        return False
    
    def navigate_to_today(self):
        """Navigate to today's history"""
        self.current_viewing_date = self.today
        return True
