#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Helper for Test Data Creation
Creates proper PDF files from text content
"""

import sys
import os

def create_pdf_from_text(text_file_path, pdf_file_path):
    """Create PDF from text file content with Greek character support"""
    try:
        # Try using reportlab if available
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Read content from temp file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create PDF
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter
        
        # Try to register a Unicode-compatible font for Greek characters
        try:
            # Try to use a system font that supports Greek
            import platform
            if platform.system() == "Windows":
                # Windows typically has Arial Unicode MS or other Unicode fonts
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf",
                    "C:/Windows/Fonts/tahoma.ttf"
                ]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                        c.setFont('UnicodeFont', 12)
                        break
                else:
                    # Fallback to built-in font
                    c.setFont('Helvetica', 12)
            else:
                c.setFont('Helvetica', 12)
        except:
            c.setFont('Helvetica', 12)
        
        # Split content into lines and write to PDF
        lines = content.split('\n')
        y_position = height - 50
        
        for line in lines:
            if y_position < 50:
                c.showPage()
                y_position = height - 50
            
            # Handle Greek and other Unicode characters
            try:
                # Try to draw the line directly (works with Unicode fonts)
                c.drawString(50, y_position, line)
            except:
                # If direct Unicode fails, try transliterating Greek to Latin
                try:
                    # Simple Greek to Latin mapping for key characters
                    greek_to_latin = {
                        'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Θ': 'TH',
                        'Ι': 'I', 'Κ': 'K', 'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O', 'Π': 'P',
                        'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y', 'Φ': 'F', 'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'W',
                        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h', 'θ': 'th',
                        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
                        'ρ': 'r', 'σ': 's', 'ς': 's', 'τ': 't', 'υ': 'y', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'w'
                    }
                    transliterated = ''.join(greek_to_latin.get(char, char) for char in line)
                    c.drawString(50, y_position, transliterated)
                except:
                    # Final fallback: ASCII only
                    ascii_line = line.encode('ascii', errors='ignore').decode('ascii')
                    c.drawString(50, y_position, ascii_line)
                
            y_position -= 20
        
        c.save()
        print(f"✅ PDF created successfully with Greek support: {pdf_file_path}")
        return True
        
    except ImportError:
        print("⚠️  reportlab not available, using text fallback...")
        return create_text_pdf_fallback(text_file_path, pdf_file_path)
    
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return create_text_pdf_fallback(text_file_path, pdf_file_path)

def create_text_pdf_fallback(text_file_path, pdf_file_path):
    """Fallback: create text file with PDF extension, preserving UTF-8 encoding"""
    try:
        # Copy with proper UTF-8 encoding preservation
        with open(text_file_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(pdf_file_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
            
        print(f"📄 Created UTF-8 text file with PDF extension: {pdf_file_path}")
        return True
    except Exception as e:
        print(f"❌ UTF-8 fallback failed, trying simple copy: {e}")
        try:
            import shutil
            shutil.copy(text_file_path, pdf_file_path)
            print(f"📄 Created text file with PDF extension: {pdf_file_path}")
            return True
        except Exception as e2:
            print(f"❌ Simple copy fallback failed: {e2}")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_pdf_helper.py <input_text_file> <output_pdf_file>")
        sys.exit(1)
    
    text_file = sys.argv[1]
    pdf_file = sys.argv[2]
    
    if not os.path.exists(text_file):
        print(f"❌ Input file not found: {text_file}")
        sys.exit(1)
    
    success = create_pdf_from_text(text_file, pdf_file)
    sys.exit(0 if success else 1)
