#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Processor για autoPyrseia
Δημιουργός: Σωτήριος Μπαλατσιάς

Επεξεργάζεται τα PDF σημάτων και εξάγει τις απαραίτητες πληροφορίες
"""

import fitz  # PyMuPDF
import re
import os
import hashlib
import subprocess
import platform
from pathlib import Path
from app.utils.path_manager import get_path_manager

class PDFProcessor:
    def __init__(self):
        # Use the centralized path manager instead of calculating paths manually
        self.path_manager = get_path_manager()
        self.downloads_path = self.path_manager.downloads_folder
        
        print(f"PDFProcessor using downloads folder: {self.downloads_path}")
    
    def process_pdf(self, pdf_path):
        """Επεξεργασία του PDF και εξαγωγή πληροφοριών"""
        try:
            # Προσπάθεια εξαγωγής κειμένου με την κλασική μέθοδο
            doc = fitz.open(pdf_path)
            full_text = ""
            
            # Εξαγωγή κειμένου από όλες τις σελίδες με αφαίρεση headers/footers
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Εξαγωγή κειμένου με πληροφορίες θέσης και γραμματοσειράς
                text_dict = page.get_text("dict")
                page_text = self.extract_text_without_headers_footers(text_dict, page.rect)
                
                full_text += page_text + "\n"
            
            doc.close()
            
            # Έλεγχος αν βρέθηκε κείμενο
            if len(full_text.strip()) > 50:  # Meaningful content threshold

                signal_data = self.extract_signal_info(full_text, pdf_path)
                return signal_data
            
            # Αν δεν βρέθηκε κείμενο, άνοιγμα PDF και αίτηση για manual input

            
            # Άνοιγμα του PDF ώστε ο χρήστης να μπορεί να το δει
            pdf_opened = self.open_pdf_with_default_program(pdf_path)
            if pdf_opened:
                pass

            else:
                pass
            # Λήψη όλων των αρχείων από downloads (εκτός από pyrseia_server.pdf)
            attachment_files = self.get_all_downloads_files()
            
            return {
                'id': 'MANUAL_INPUT_REQUIRED',
                'fm': 'MANUAL_INPUT_REQUIRED',
                'theme': 'Μη διαθέσιμο',
                'recipients': [],
                'attachments': attachment_files,
                'error': 'MANUAL_INPUT_REQUIRED',
                'manual_input': True
            }
            
        except Exception as e:
            raise Exception(f"Σφάλμα στην επεξεργασία του PDF: {str(e)}")
    
    def open_pdf_with_default_program(self, pdf_path):
        """Άνοιγμα του PDF με το προεπιλεγμένο πρόγραμμα"""
        try:
            # Μετατροπή σε απόλυτο path αν είναι σχετικό
            if not os.path.isabs(pdf_path):
                pdf_path = os.path.abspath(pdf_path)
            
            # Έλεγχος ύπαρξης αρχείου
            if not os.path.exists(pdf_path):
                return False
            
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
            
            return True
            
        except Exception as e:
            return False
    
    def get_all_downloads_files(self):
        """Λήψη όλων των αρχείων από το downloads folder (εκτός από pyrseia_server.pdf)"""
        try:
            if not self.downloads_path.exists():
                return []
            
            all_files = []
            for file_path in self.downloads_path.iterdir():
                if file_path.is_file() and file_path.name != 'pyrseia_server.pdf':
                    all_files.append(file_path.name)
            

            return sorted(all_files)
            
        except Exception as e:
            print(f"❌ Σφάλμα στη λήψη αρχείων: {e}")
            return []
    
    def create_manual_signal_data(self, signal_id, fm, pdf_path):
        """Δημιουργία signal data με manual input"""
        try:
            # Λήψη όλων των αρχείων από downloads (εκτός από pyrseia_server.pdf)
            attachment_files = self.get_all_downloads_files()
            
            signal_data = {
                'id': signal_id,
                'fm': fm,
                'theme': 'Manual Signal Entry',
                'recipients': [],
                'attachments': attachment_files,
                'serial_number': self.generate_serial_number(signal_id, fm)
            }
            
            return signal_data
            
        except Exception as e:
            raise Exception(f"Σφάλμα στη δημιουργία manual signal data: {str(e)}")
    
    
    
    def extract_text_without_headers_footers(self, text_dict, page_rect):
        """Εξαγωγή κειμένου με αφαίρεση headers και footers"""
        page_height = page_rect.height
        page_width = page_rect.width
        
        # Ορισμός ζωνών header (10% από πάνω) και footer (10% από κάτω)
        header_zone = page_height * 0.1
        footer_zone = page_height * 0.9
        
        clean_text = ""
        
        try:
            for block in text_dict["blocks"]:
                if "lines" in block:  # Text block
                    block_y = block["bbox"][1]  # y coordinate of block
                    
                    # Έλεγχος αν το block είναι στη ζώνη header ή footer
                    if block_y <= header_zone or block_y >= footer_zone:
                        # Έλεγχος αν περιέχει header/footer patterns
                        block_text = ""
                        for line in block["lines"]:
                            for span in line["spans"]:
                                block_text += span["text"]
                        
                        if self.is_header_or_footer_line(block_text):
                            continue  # Παραλείπουμε αυτό το block
                    
                    # Προσθήκη του καθαρού κειμένου
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += span["text"]
                        
                        # Τελικός έλεγχος για header/footer patterns σε κάθε γραμμή
                        if not self.is_header_or_footer_line(line_text):
                            clean_text += line_text + "\n"
        
        except Exception as e:
            # Fallback σε απλή εξαγωγή κειμένου αν αποτύχει η λεπτομερής ανάλυση
            print(f"Σφάλμα στην αφαίρεση headers/footers: {e}")
            clean_text = ""
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            clean_text += span["text"]
                        clean_text += "\n"
        
        return clean_text
    
    def is_header_or_footer_line(self, line_text):
        """Έλεγχος αν μια γραμμή είναι header ή footer"""
        line = line_text.strip()
        
        if not line:
            return False
        
        # Patterns για header detection
        # 1. Ημερομηνία (DD/M/YY ή DD/MM/YY format)
        date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'
        
        # 2. Ώρα (H:MM μ.μ. ή π.μ.)
        time_pattern = r'\d{1,2}:\d{2}\s*[πμ]\.[πμ]\.'
        
        # 3. URL patterns
        url_pattern = r'8mptexchn2\.army\.hndgs\.mil/pyrseia/pyrseia_server\.php'
        
        # 4. Page number pattern (number/number)
        page_pattern = r'\b\d+/\d+\b'
        
        # Header detection: περιέχει ημερομηνία ΚΑΙ ώρα ΚΑΙ URL
        has_date = bool(re.search(date_pattern, line))
        has_time = bool(re.search(time_pattern, line))
        has_url = bool(re.search(url_pattern, line))
        
        # Footer detection: περιέχει page number ΚΑΙ URL
        has_page_number = bool(re.search(page_pattern, line))
        
        # Είναι header αν περιέχει (ημερομηνία ή ώρα) ΚΑΙ URL
        is_header = has_url and (has_date or has_time)
        
        # Είναι footer αν περιέχει page number ΚΑΙ URL
        is_footer = has_url and has_page_number
        
        # Επιπλέον έλεγχος: αν η γραμμή περιέχει μόνο URL (χωρίς άλλο περιεχόμενο)
        url_only = has_url and len(line.replace(re.search(url_pattern, line).group() if has_url else "", "").strip()) < 20
        
        return is_header or is_footer or url_only
    
    def extract_signal_info(self, text, pdf_path):
        """Εξαγωγή πληροφοριών από το κείμενο του σήματος"""
        # Detect and remove original message section before processing
        cleaned_text = self.detect_and_remove_original_message(text)
        
        lines = cleaned_text.split('\n')
        signal_data = {}
        
        # 1. Εξαγωγή ID (γραμμή πάνω από FM)
        signal_data['id'] = self.extract_id(lines)
        
        # 2. Εξαγωγή FM (χωρίς το "FM ")
        signal_data['fm'] = self.extract_fm(cleaned_text)
        
        # 3. Εξαγωγή RECIPIENTS
        signal_data['recipients'] = self.extract_recipients(cleaned_text)
        
        # 4. Εξαγωγή ΘΕΜΑ
        signal_data['theme'] = self.extract_theme(cleaned_text)
        
        # 5. Εξαγωγή συνημμένων
        signal_data['attachments'] = self.extract_attachments(cleaned_text)
        
        # 6. Δημιουργία serial number
        signal_data['serial_number'] = self.generate_serial_number(signal_data['id'], signal_data['fm'])
        
        return signal_data
    
    def detect_and_remove_original_message(self, text):
        """Εντοπισμός και αφαίρεση αρχικού μηνύματος που περιέχεται στο σήμα"""
        start_pattern = "ΚΕΙΜΕΝΟ ΑΡΧΙΚΟΥ ΜΗΝΥΜΑΤΟΣ"
        end_pattern = "ΤΕΛΟΣ ΑΡΧΙΚΟΥ ΜΗΝΥΜΑΤΟΣ"
        
        # Search for the original message section
        start_pos = text.find(start_pattern)
        
        if start_pos != -1:
            # Find the end of the original message section
            end_pos = text.find(end_pattern, start_pos)
            
            if end_pos != -1:
                # Include the end pattern in the removal
                end_pos += len(end_pattern)
                
                # Extract the original message section for logging
                original_message_section = text[start_pos:end_pos]
                
                # Remove the section from the text
                cleaned_text = text[:start_pos] + text[end_pos:]
                
                # Clean up any extra whitespace left behind
                cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
                
                return cleaned_text.strip()
        
        # If no original message section is found, return the text as is
        return text
    
    def extract_id(self, lines):
        """Εξαγωγή ID - γραμμή πάνω από FM"""
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.upper().startswith('FM') and (len(line_stripped) == 2 or line_stripped[2] == ' '):
                if i > 0:
                    return lines[i-1].strip()
        return "Μη διαθέσιμο"
    
    def extract_fm(self, text):
        """Εξαγωγή FM (χωρίς το "FM ")"""
        fm_pattern = re.compile(r'^FM\s+(.*?)(?:\n|$)', re.IGNORECASE | re.MULTILINE)
        matches = fm_pattern.findall(text)
        if matches:
            # Αφαίρεση τυχόν παρενθέσεων στο τέλος
            fm = matches[0].strip()
            if '(' in fm:
                fm = fm.split('(')[0].strip()
            return fm
        return "Μη διαθέσιμο"
    
    def extract_recipients(self, text):
        """Εξαγωγή παραληπτών από τη γραμμή μετά το FM μέχρι το ΘΕΜΑ:"""
        recipients = set()
        
        # Βρίσκουμε το τμήμα από FM μέχρι ΘΕΜΑ: - FM και ΘΕΜΑ πρέπει να είναι στην αρχή γραμμής
        # Χρησιμοποιούμε greedy matching για να πάρουμε όλο το τμήμα
        fm_to_theme_match = re.search(r'^FM\s+.*?\n(.*)(?=^\s*ΘΕΜΑ\s*:|$)', text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if fm_to_theme_match:
            section = fm_to_theme_match.group(1)
            recipients.update(self.parse_recipients_section(section))
        else:
            # Alternative approach: find FM line and capture everything until ΘΕΜΑ
            fm_match = re.search(r'^FM\s+.*$', text, re.MULTILINE | re.IGNORECASE)
            theme_match = re.search(r'^\s*ΘΕΜΑ\s*:', text, re.MULTILINE | re.IGNORECASE)
            
            if fm_match and theme_match:
                fm_end = fm_match.end()
                theme_start = theme_match.start()
                section = text[fm_end:theme_start].strip()
                recipients.update(self.parse_recipients_section(section))
            elif fm_match:
                # Take everything after FM to end
                fm_end = fm_match.end()
                section = text[fm_end:].strip()
                recipients.update(self.parse_recipients_section(section))
        
        # Φιλτράρισμα των παραληπτών με βάση τη λίστα του χρήστη
        filtered_recipients = self.filter_recipients_by_user_list(list(recipients))
        
        return sorted(filtered_recipients)
    
    def filter_recipients_by_user_list(self, detected_recipients):
        """Φιλτράρισμα των ανιχνευμένων παραληπτών με βάση τη λίστα του χρήστη"""
        try:
            from app.services.recipients_manager import RecipientsManager
            recipients_manager = RecipientsManager()
            
            # Λήψη της λίστας των επιθυμητών παραληπτών
            user_recipients = recipients_manager.get_all_recipients()
            
            # Φιλτράρισμα - κρατάμε μόνο τους παραλήπτες που υπάρχουν στη λίστα του χρήστη
            filtered = []
            for detected in detected_recipients:
                if detected in user_recipients:
                    filtered.append(detected)
            
            return filtered
            
        except Exception as e:
            print(f"Σφάλμα στο φιλτράρισμα παραληπτών: {e}")
            # Σε περίπτωση σφάλματος, επιστρέφουμε όλους τους ανιχνευμένους παραλήπτες
            return detected_recipients
    

    def parse_recipients_section(self, section):
        """Ανάλυση τμήματος παραληπτών - κάθε γραμμή είναι παραλήπτης"""
        recipients = set()
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Αν η γραμμή είναι κενή, την αγνοούμε
            if not line:
                continue
                
            # Αν η γραμμή ξεκινάει με "TO ", αφαιρούμε το "TO " και κρατάμε το υπόλοιπο
            if line.upper().startswith('TO '):
                line = line[3:].strip()  # Αφαιρούμε τα πρώτα 3 χαρακτήρες "TO "
            
            # Αν η γραμμή ξεκινάει με "INFO ", αφαιρούμε το "INFO " και κρατάμε το υπόλοιπο
            elif line.upper().startswith('INFO '):
                line = line[5:].strip()  # Αφαιρούμε τα πρώτα 5 χαρακτήρες "INFO "
            
            # Φιλτράρισμα για URLs και άλλα ανεπιθύμητα
            if (line and
                not line.startswith('http') and
                not '=' in line and
                not 'texchn' in line.lower() and
                not 'pyrseia' in line.lower()):
                
                # Καθαρισμός από ειδικούς χαρακτήρες
                clean_line = re.sub(r'[^\w\s/.-]', '', line)
                if clean_line.strip():
                    recipients.add(clean_line.strip())
        
        return recipients
    
    def extract_theme(self, text):
        """Εξαγωγή ΘΕΜΑ"""
        # Αναζήτηση για "ΘΕΜΑ:" μόνο στην αρχή γραμμής - αν δεν βρεθεί "ΣΧΕΤ", σταματάμε στο τέλος της γραμμής
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Έλεγχος αν η γραμμή ξεκινάει με ΘΕΜΑ και έχει άνω και κάτω τελεία
            if re.search(r'^\s*ΘΕΜΑ\s*:', line.strip(), re.IGNORECASE):
                # Βρήκαμε τη γραμμή με ΘΕΜΑ
                theme_match = re.search(r'^\s*ΘΕΜΑ\s*:\s*(.*)', line.strip(), re.IGNORECASE)
                if theme_match:
                    theme = theme_match.group(1).strip()
                    
                    # Έλεγχος αν υπάρχει "ΣΧΕΤ. :" στο υπόλοιπο κείμενο
                    remaining_text = '\n'.join(lines[i:])
                    if re.search(r'^\s*ΣΧΕΤ\.\s*:', remaining_text, re.IGNORECASE | re.MULTILINE):
                        # Αν υπάρχει ΣΧΕΤ. :, παίρνουμε το κείμενο μέχρι το ΣΧΕΤ. :
                        theme_pattern = re.compile(r'^\s*ΘΕΜΑ\s*:\s*(.*?)(?=^\s*ΣΧΕΤ\.\s*:)', re.IGNORECASE | re.DOTALL | re.MULTILINE)
                        matches = theme_pattern.findall(text)
                        if matches:
                            theme = matches[0].strip()
                    else:
                        # Αν δεν υπάρχει ΣΧΕΤ. :, παίρνουμε μόνο την τρέχουσα γραμμή
                        theme = theme_match.group(1).strip()
                    
                    # Καθαρισμός από επιπλέον χαρακτήρες και URLs
                    theme = re.sub(r'http[s]?://\S+', '', theme)  # Αφαίρεση URLs
                    theme = re.sub(r'[^\w\s\.\-/]', '', theme)  # Αφαίρεση ειδικών χαρακτήρων (κρατάμε μόνο γράμματα, αριθμούς, κενά, τελείες, παύλες, κάθετες)
                    theme = re.sub(r'\s+', ' ', theme)  # Πολλαπλά κενά σε ένα
                    theme = theme.strip()
                    
                    return theme if theme else "Μη διαθέσιμο"
        
        return "Μη διαθέσιμο"
    
    def extract_attachments(self, text):
        """Εξαγωγή συνημμένων αρχείων"""
        attachments = []
        lines = text.split('\n')
        
        # Αναζήτηση για "συνημμένα αρχεία:" και τις επόμενες γραμμές με αρίθμηση
        found_attachment_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Εύρεση της γραμμής με "συνημμένα αρχεία"
            if re.search(r'συνημμένα αρχεία', line, re.IGNORECASE):
                found_attachment_section = True
                
                # Ελέγχω αν υπάρχει κάτι στην ίδια γραμμή μετά το ":"
                attachment_on_same_line = re.search(r'συνημμένα αρχεία[:\s]+(.*)', line, re.IGNORECASE)
                if attachment_on_same_line:
                    attachment_text = attachment_on_same_line.group(1).strip()
                    if attachment_text and not attachment_text.isdigit():
                        attachments.append(attachment_text)
                
                # Συνεχίζω να ψάχνω τις επόμενες γραμμές για αριθμημένα αρχεία
                for j in range(i + 1, min(i + 20, len(lines))):  # Ψάχνω τις επόμενες 20 γραμμές μέγιστο
                    next_line = lines[j].strip()
                    
                    # Αναζήτηση για αριθμημένα αρχεία (1. filename, 2. filename, κτλ)
                    numbered_attachment = re.search(r'^\d+\.\s*(.+)', next_line)
                    if numbered_attachment:
                        attachment_name = numbered_attachment.group(1).strip()
                        # Καθαρισμός από URLs και ειδικούς χαρακτήρες
                        attachment_name = re.sub(r'http[s]?://\S+', '', attachment_name)
                        attachment_name = attachment_name.strip()
                        if attachment_name:
                            attachments.append(attachment_name)
                    elif next_line and not re.search(r'^[A-Ζ\s]+:', next_line):
                        # Αν η γραμμή δεν είναι κενή και δεν είναι νέα ενότητα, μπορεί να είναι συνημμένο
                        # αλλά σταματάμε αν βρούμε νέα ενότητα (π.χ. "ΣΧΕΤ:", "ΘΕΜΑ:", κτλ)
                        break
                    elif re.search(r'^[Α-Ω]+\s*[:\.]', next_line):
                        # Νέα ενότητα, σταματάμε
                        break
                
                break
        
        # Εναλλακτική αναζήτηση για αριθμό συνημμένων αν δεν βρήκαμε την ενότητα
        if not found_attachment_section:
            count_pattern = re.compile(r'(\d+)\s*συνημμένα? αρχεί[οα]', re.IGNORECASE)
            count_matches = count_pattern.findall(text)
            
            if count_matches:
                count = int(count_matches[0])
                # Ψάχνω για αριθμημένα αρχεία σε όλο το κείμενο
                for line in lines:
                    numbered_attachment = re.search(r'^\d+\.\s*(.+)', line.strip())
                    if numbered_attachment:
                        attachment_name = numbered_attachment.group(1).strip()
                        # Καθαρισμός από URLs
                        attachment_name = re.sub(r'http[s]?://\S+', '', attachment_name)
                        attachment_name = attachment_name.strip()
                        if attachment_name and len(attachments) < count:
                            attachments.append(attachment_name)
                
                # Αν δεν βρήκαμε αρκετά, δημιουργούμε placeholder
                while len(attachments) < count:
                    attachments.append(f"Συνημμένο_{len(attachments)+1}")
        
        return attachments
    
    def generate_serial_number(self, signal_id, fm):
        """Δημιουργία μοναδικού serial number"""
        try:
            # Συνδυασμός ID και FM
            combined_string = f"{signal_id}_{fm}"
            hash_object = hashlib.md5(combined_string.encode())
            hex_dig = hash_object.hexdigest()
            
            # Μετατροπή σε αριθμό (παίρνουμε τα πρώτα 8 χαρακτήρες)
            serial_number = int(hex_dig[:8], 16)
            
            return serial_number
            
        except Exception:
            # Fallback σε τυχαίο αριθμό αν αποτύχει
            import random
            return random.randint(10000000, 99999999)
    
    def check_duplicate_by_serial(self, signal_data, recipient_path):
        """Έλεγχος για διπλότυπο με βάση το serial number"""
        try:
            recipient_folder = Path(recipient_path)
            if not recipient_folder.exists():
                return False
            
            # Αναζήτηση για JSON αρχεία στον φάκελο του παραλήπτη
            for subfolder in recipient_folder.iterdir():
                if subfolder.is_dir():
                    json_files = list(subfolder.glob("*.json"))
                    for json_file in json_files:
                        try:
                            import json
                            with open(json_file, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                                if existing_data.get('serial_number') == signal_data['serial_number']:
                                    return True
                        except Exception:
                            continue
            
            return False
            
        except Exception:
            return False
