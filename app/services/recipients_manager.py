#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recipients Manager για autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Διαχειρίζεται τη λίστα των παραληπτών
"""

import json
from pathlib import Path
from app.utils.path_manager import get_path_manager

class RecipientsManager:
    def __init__(self):
        # Use the centralized path manager instead of calculating paths manually
        self.path_manager = get_path_manager()
        self.recipients_file = self.path_manager.project_root / "recipients.json"
        
        print(f"RecipientsManager using project root: {self.path_manager.project_root}")
        
        self.load_recipients()
    
    def load_recipients(self):
        """Φόρτωση της λίστας παραληπτών"""
        try:
            if self.recipients_file.exists():
                with open(self.recipients_file, 'r', encoding='utf-8') as f:
                    self.recipients = json.load(f)
            else:
                # Προεπιλεγμένη λίστα παραληπτών - μόνο χρήσιμοι παραλήπτες
                self.recipients = [
                    "ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ",
                    "ΣΤΡΑΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ", 
                    "ΛΑΦ ΙΩΑΝΝΙΝΩΝ",
                    "ΣΠ ΙΩΑΝΝΙΝΩΝ",
                    "ΣΥ ΗΠΕΙΡΟΥ",
                    "4501 ΠΜΥ",
                    "ΝΑΥΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ",
                    "ΑΕΡΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ"
                ]
                self.save_recipients()
        except Exception as e:
            print(f"Σφάλμα στη φόρτωση παραληπτών: {e}")
            self.recipients = []
    
    def save_recipients(self):
        """Αποθήκευση της λίστας παραληπτών"""
        try:
            with open(self.recipients_file, 'w', encoding='utf-8') as f:
                json.dump(self.recipients, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Σφάλμα στην αποθήκευση παραληπτών: {e}")
    
    def add_recipient(self, recipient):
        """Προσθήκη νέου παραλήπτη"""
        recipient = recipient.strip()
        if recipient and recipient not in self.recipients:
            self.recipients.append(recipient)
            self.recipients.sort()
            self.save_recipients()
            return True
        return False
    
    def remove_recipient(self, recipient):
        """Αφαίρεση παραλήπτη"""
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self.save_recipients()
            return True
        return False
    
    def get_all_recipients(self):
        """Λήψη όλων των παραληπτών"""
        return self.recipients.copy()
    
    def filter_recipients(self, detected_recipients):
        """Φιλτράρισμα των ανιχνευμένων παραληπτών με βάση τη λίστα χρήσιμων παραληπτών"""
        filtered = []
        
        for detected in detected_recipients:
            # Έλεγχος για ακριβή ταύτιση
            if detected in self.recipients:
                filtered.append(detected)
            # Έλεγχος για μερική ταύτιση (για περιπτώσεις με μικρές διαφορές)
            else:
                for known_recipient in self.recipients:
                    # Αν το 80% του ονόματος ταυτίζεται, το δεχόμαστε
                    if (detected in known_recipient or known_recipient in detected) and \
                       len(detected) > 3:  # Αποφυγή πολύ μικρών ταυτίσεων
                        filtered.append(detected)
                        break
        
        return filtered
    
    def is_useful_recipient(self, recipient_name):
        """Έλεγχος αν ο παραλήπτης είναι χρήσιμος"""
        # Φιλτράρουμε αριθμούς, URLs, και μη χρήσιμες καταχωρήσεις
        if not recipient_name or len(recipient_name) < 3:
            return False
        
        # Αποκλείουμε αριθμούς μόνο
        if recipient_name.isdigit():
            return False
        
        # Αποκλείουμε URLs και τεχνικές γραμμές
        if any(term in recipient_name.lower() for term in ['http', 'www', '/', 'pyrseia', 'texchn']):
            return False
        
        # Αποκλείουμε γραμμές με πολλά ειδικά σύμβολα
        special_chars = sum(1 for c in recipient_name if not (c.isalnum() or c.isspace() or c in 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω/-'))
        if special_chars > len(recipient_name) * 0.3:  # Περισσότερο από 30% ειδικοί χαρακτήρες
            return False
        
        return True
    
    def search_recipients(self, search_term):
        """Αναζήτηση παραληπτών"""
        search_term = search_term.lower()
        results = []
        for recipient in self.recipients:
            if search_term in recipient.lower():
                results.append(recipient)
        return results
