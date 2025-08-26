#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
String utilities for autoPyrseia
"""

import re
import unicodedata
from datetime import datetime


def safe_filename(filename):
    """Δημιουργία ασφαλούς ονόματος αρχείου"""
    # Αφαίρεση ή αντικατάσταση μη επιτρεπτών χαρακτήρων
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Αφαίρεση κενών από αρχή και τέλος
    safe_name = safe_name.strip()
    # Αντικατάσταση πολλαπλών underscores με ένα
    safe_name = re.sub(r'_+', '_', safe_name)
    return safe_name


def format_datetime_greek(dt):
    """Μορφοποίηση ημερομηνίας σε ελληνικό format"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    # Ελληνικά ονόματα μηνών
    greek_months = {
        1: 'Ιαν', 2: 'Φεβ', 3: 'Μαρ', 4: 'Απρ', 5: 'Μαϊ', 6: 'Ιουν',
        7: 'Ιουλ', 8: 'Αυγ', 9: 'Σεπ', 10: 'Οκτ', 11: 'Νοε', 12: 'Δεκ'
    }
    
    return f"{dt.day:02d} {greek_months[dt.month]} {dt.year}"


def clean_filename_for_matching(filename):
    """Καθαρισμός ονόματος αρχείου για καλύτερο matching"""
    # Αφαίρεση extension για καλύτερη σύγκριση
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Κανονικοποίηση Unicode (NFD) για χειρισμό ειδικών χαρακτήρων
    normalized = unicodedata.normalize('NFD', name_without_ext)
    
    # Αφαίρεση diacritics (τόνων) από ελληνικά γράμματα
    without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Αντικατάσταση πολλαπλών whitespace με ένα κενό
    cleaned = re.sub(r'\s+', ' ', without_accents)
    
    # Αφαίρεση ειδικών χαρακτήρων και κενών από την αρχή/τέλος
    cleaned = re.sub(r'[^\w\s\-_.]', '', cleaned).strip()
    
    # Μετατροπή σε πεζά για case-insensitive σύγκριση
    return cleaned.lower()


def calculate_filename_similarity(name1, name2):
    """Υπολογισμός ομοιότητας μεταξύ δύο ονομάτων αρχείων"""
    if not name1 or not name2:
        return 0.0
    
    # Exact match after cleaning
    if name1 == name2:
        return 1.0
    
    # Levenshtein distance για similarity
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    # Υπολογισμός distance
    distance = levenshtein_distance(name1, name2)
    max_length = max(len(name1), len(name2))
    
    # Μετατροπή distance σε similarity score (0-1)
    similarity = 1.0 - (distance / max_length) if max_length > 0 else 0.0
    
    # Bonus για substring matches
    if name1 in name2 or name2 in name1:
        similarity = min(1.0, similarity + 0.1)
    
    # Bonus για κοινά tokens (λέξεις)
    tokens1 = set(name1.split())
    tokens2 = set(name2.split())
    if tokens1 and tokens2:
        common_tokens = len(tokens1.intersection(tokens2))
        total_tokens = len(tokens1.union(tokens2))
        token_similarity = common_tokens / total_tokens
        similarity = max(similarity, token_similarity)
    
    return similarity
