#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autoPyrseia - Main Entry Point
Δημιουργός: Σωτήριος Μπαλατσιάς
Τηλέφωνο υποστήριξης: 6983733346

Εφαρμογή για την αυτοματοποίηση της διαχείρισης σημάτων από το σύστημα Pyrseia
"""

import sys
import os

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core import AutoPyrseiaApp

if __name__ == "__main__":
    app = AutoPyrseiaApp()
    app.run()
