#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File operations utilities for autoPyrseia
"""

import os
from pathlib import Path
from .string_utils import clean_filename_for_matching, calculate_filename_similarity
from .path_manager import get_path_manager


def get_download_folder():
    """Επιστρέφει το downloads folder"""
    path_manager = get_path_manager()
    return path_manager.downloads_folder


def ensure_directory_exists(path):
    """Δημιουργεί τον φάκελο αν δεν υπάρχει"""
    Path(path).mkdir(parents=True, exist_ok=True)


def check_attachment_exists(attachment_name):
    """Έλεγχος αν υπάρχει το συνημμένο αρχείο"""
    path_manager = get_path_manager()
    downloads_path = path_manager.downloads_folder
    
    # Έλεγχος ακριβούς ονόματος
    if (downloads_path / attachment_name).exists():
        return True
    
    # Έλεγχος για παρόμοια ονόματα
    for file in downloads_path.glob("*"):
        if file.name.lower() == attachment_name.lower():
            return True
    
    # Fuzzy matching για παρόμοια ονόματα
    similar_file = find_similar_filename(attachment_name, downloads_path)
    if similar_file:
        return True
    
    return False


def find_similar_filename(target_name, search_path):
    """Αναζήτηση παρόμοιου ονόματος αρχείου με fuzzy matching"""
    if not search_path.exists():
        return None
    
    # Καθαρισμός του target name από διάφορα προβλήματα
    cleaned_target = clean_filename_for_matching(target_name)
    
    best_match = None
    best_score = 0
    
    for file in search_path.glob("*"):
        if file.is_file():
            # Καθαρισμός του πραγματικού ονόματος αρχείου
            cleaned_filename = clean_filename_for_matching(file.name)
            
            # Υπολογισμός similarity score
            score = calculate_filename_similarity(cleaned_target, cleaned_filename)
            
            # Θεωρούμε match αν το score είναι πάνω από 0.8 (80% similarity)
            if score > 0.8 and score > best_score:
                best_score = score
                best_match = file.name
    
    return best_match


def clear_downloads_folder():
    """Καθαρισμός του φακέλου downloads"""
    try:
        path_manager = get_path_manager()
        downloads_path = path_manager.downloads_folder
        
        if downloads_path.exists():
            for file in downloads_path.glob("*"):
                if file.is_file():
                    file.unlink()
    except Exception as e:
        print(f"Σφάλμα κατά τον καθαρισμό του φακέλου downloads: {str(e)}")
