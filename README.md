# autoPyrseia

**Εφαρμογή για την αυτοματοποίηση της διαχείρισης σημάτων από το σύστημα Pyrseia**

## 📋 Περιγραφή

Το autoPyrseia είναι μια Python εφαρμογή που αυτοματοποιεί τη διαχείριση και επεξεργασία σημάτων από το σύστημα Pyrseia. Η εφαρμογή παρέχει:

- 📄 **Επεξεργασία PDF**: Αυτόματη ανάλυση και εξαγωγή δεδομένων από PDF σήματα
- 👥 **Διαχείριση Παραληπτών**: Φιλτράρισμα και οργάνωση παραληπτών σημάτων
- 📁 **Οργάνωση Αρχείων**: Αυτόματη κατηγοριοποίηση και αρχειοθέτηση
- 📊 **Ιστορικό Δραστηριότητας**: Παρακολούθηση και καταγραφή επεξεργασμένων σημάτων
- 🔄 **USB Integration**: Αυτόματη εξαγωγή δεδομένων σε USB συσκευές

## 🚀 Γρήγορη Εκκίνηση

### 📖 Οδηγίες Χρήσης

Για αναλυτικές οδηγίες χρήσης της εφαρμογής, δείτε το [**USER_GUIDE.md**](USER_GUIDE.md)

### Προαπαιτούμενα

- Python 3.8+
- Windows 10/11

### Εγκατάσταση

1. **Clone το repository:**

   ```bash
   git clone https://github.com/yourusername/autoPyrseia.git
   cd autoPyrseia
   ```
2. **Εγκατάσταση dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Εκτέλεση εφαρμογής:**

   ```bash
   python main.py
   ```

### Δημιουργία Executable

Για δημιουργία standalone εκτελέσιμου αρχείου:

```bash
create_exe.bat
```

## 📁 Δομή Έργου

```
autoPyrseia/
├── 📂 app/                          # Κύριος κώδικας εφαρμογής
│   ├── 📄 core.py                   # Κεντρική λογική εφαρμογής & UI coordination
│   ├── 📄 __init__.py               # Package initialization
│   │
│   ├── 📂 controllers/              # Controllers για UI και business logic
│   │   ├── 📄 file_watcher.py       # Παρακολούθηση φακέλου downloads
│   │   ├── 📄 signal_controller.py  # Έλεγχος ροής επεξεργασίας σημάτων
│   │   └── 📄 __init__.py
│   │
│   ├── 📂 services/                 # Business logic υπηρεσίες
│   │   ├── 📄 config_manager.py     # Διαχείριση ρυθμίσεων & configuration
│   │   ├── 📄 daily_history.py      # Ημερήσιο ιστορικό δραστηριότητας
│   │   ├── 📄 duplicate_manager.py  # Ανίχνευση διπλότυπων & versioning
│   │   ├── 📄 pdf_processor.py      # Επεξεργασία & ανάλυση PDF σημάτων
│   │   ├── 📄 recipients_manager.py # Διαχείριση λίστας παραληπτών
│   │   ├── 📄 signal_manager.py     # Κεντρική διαχείριση σημάτων
│   │   ├── 📄 usb_extractor.py      # USB εξαγωγή & Excel generation
│   │   └── 📄 __init__.py
│   │
│   ├── 📂 ui/                       # Γραφικό περιβάλλον χρήστη
│   │   ├── 📂 dialogs/              # Dialog windows
│   │   │   ├── 📄 manual_input.py   # Manual signal input dialog
│   │   │   └── 📄 __init__.py
│   │   │
│   │   ├── 📂 tabs/                 # Καρτέλες κύριας εφαρμογής
│   │   │   ├── 📄 signal_processing.py  # Επεξεργασία σημάτων tab
│   │   │   ├── 📄 usb_extraction.py     # USB εξαγωγή tab
│   │   │   ├── 📄 recipients_mgmt.py    # Διαχείριση παραληπτών tab
│   │   │   ├── 📄 daily_history.py      # Ημερήσιο ιστορικό tab
│   │   │   ├── 📄 history.py            # Legacy history implementation
│   │   │   ├── 📄 simple_history.py     # Απλοποιημένο ιστορικό
│   │   │   └── 📄 __init__.py
│   │   │
│   │   ├── 📂 utils/                # UI utilities & helpers
│   │   │   ├── 📄 keyboard_handlers.py  # Keyboard shortcuts & navigation
│   │   │   ├── 📄 tooltips.py           # Tooltip functionality
│   │   │   └── 📄 __init__.py
│   │   │
│   │   ├── 📂 widgets/              # Custom UI components
│   │   │   ├── 📄 folder_button.py      # Folder access button widget
│   │   │   ├── 📄 status_bar.py         # Status bar component
│   │   │   └── 📄 __init__.py
│   │   │
│   │   └── 📄 __init__.py
│   │
│   └── 📂 utils/                    # Βοηθητικά εργαλεία & utilities
│       ├── 📄 file_operations.py    # File handling & operations
│       ├── 📄 path_manager.py       # Centralized path management
│       ├── 📄 progress_manager.py   # Progress tracking & UI updates
│       ├── 📄 string_utils.py       # String manipulation utilities
│       └── 📄 __init__.py
│
├── 📂 DATA/                         # Αποθηκευμένα σήματα (runtime)
│   └── 📂 [Παραλήπτης]/
│       └── 📂 [Signal ID]/
│           ├── 📄 [Signal ID].pdf
│           ├── 📄 signal_info.json
│           └── 📎 [συνημμένα...]
│
├── 📂 BACK UP DATA/                 # Backup αρχεία μετά από USB extraction
│   └── 📂 [Παραλήπτης]/
│       └── 📂 [Α.Φ. Number]/
│           └── 📂 [Signal Folders]...
│
├── 📂 downloads/                    # Εισερχόμενα σήματα από Pyrseia
│   ├── 📄 pyrseia_server.pdf        # Κύριο PDF σήμα (temporary)
│   └── 📎 [συνημμένα...]           # Συνημμένα αρχεία (temporary)
│
├── 📂 templates/                    # Excel templates & resources
│   └── 📄 print.xlsx               # Template για USB extraction
│
├── 📂 temp/                         # Προσωρινά αρχεία εργασίας
│
├── 📄 main.py                       # 🚀 Κύριο αρχείο εκκίνησης
├── 📄 config.json                   # ⚙️ Ρυθμίσεις εφαρμογής
├── 📄 recipients.json               # 👥 Λίστα εγκεκριμένων παραληπτών
├── 📄 history.json                  # 📊 Ιστορικό επεξεργασμένων σημάτων
├── 📄 requirements.txt              # 📦 Python dependencies
├── 📄 autopyrseia.spec             # 🔧 PyInstaller configuration
├── 📄 icon.png                      # 🎨 Application icon
├── 📄 start_autopyrseia.bat        # 🚀 Windows startup script
├── 📄 create_exe.bat               # 📦 Executable build script
├── 📄 README.md                     # 📖 Τεκμηρίωση έργου
├── 📄 LICENSE                       # ⚖️ Άδεια χρήσης
│
├── 📂 signal_tester.py             # 🧪 Development testing tool
├── 📄 signal_tester_config.json    # ⚙️ Signal tester configuration
├── 📄 start_signal_tester.bat      # 🧪 Signal tester launcher
├── 📄 create_test_data.bat         # 🧪 Test data generator
└── 📄 create_pdf_helper.py         # 🧪 PDF creation utility
```

### 🏗️ Αρχιτεκτονική Οργάνωση

#### **📊 Core Layer** (`app/core.py`)
- **Application Orchestration**: Κεντρική συντονιστική λογική
- **Manager Initialization**: Αρχικοποίηση όλων των services
- **UI Coordination**: Συντονισμός tabs και UI components

#### **🎮 Controllers Layer** (`app/controllers/`)
- **File Watcher**: Real-time monitoring φακέλου downloads
- **Signal Controller**: Ενορχήστρωση ροής επεξεργασίας σημάτων

#### **⚙️ Services Layer** (`app/services/`)
- **PDF Processing**: Ανάλυση και εξαγωγή δεδομένων από PDF
- **Signal Management**: Αποθήκευση και οργάνωση σημάτων
- **Duplicate Detection**: Έξυπνη ανίχνευση διπλότυπων με versioning
- **USB Extraction**: Excel generation και backup operations
- **Configuration**: Διαχείριση ρυθμίσεων και αποθήκευση state

#### **🎨 UI Layer** (`app/ui/`)
- **Tabs**: Κύρια interface με πολλαπλές καρτέλες
- **Dialogs**: Modal windows για ειδικές λειτουργίες
- **Widgets**: Custom UI components και controls
- **Utils**: UI helpers, tooltips, keyboard handlers

#### **🔧 Utils Layer** (`app/utils/`)
- **File Operations**: Χαμηλού επιπέδου file handling
- **Path Management**: Κεντρική διαχείριση διαδρομών
- **Progress Management**: Thread-safe progress tracking
- **String Utilities**: Text processing και manipulation

### 📁 Runtime Directory Structure

#### **DATA/** - Κύρια Αποθήκευση Σημάτων
```
DATA/ΛΑΦ ΙΩΑΝΝΙΝΩΝ/R 240846Z JUN 25/
├── R 240846Z JUN 25.pdf      # Κύριο PDF σήμα
├── signal_info.json          # Metadata & processing info
├── attachment1.docx          # Συνημμένο 1
└── attachment2.xlsx          # Συνημμένο 2
```

#### **BACK UP DATA/** - Archive Μετά από USB Extraction
```
BACK UP DATA/ΛΑΦ ΙΩΑΝΝΙΝΩΝ/Α.Φ. 8635/
├── R 240846Z JUN 25/         # Moved signal folder
└── P 021615Z JUL 25/         # Another signal folder
```

## ⚙️ Ρυθμίσεις

Επεξεργαστείτε το αρχείο `config.json` για προσαρμογή:

```json
{
  "pdf_processing": {
    "auto_process": true,
    "backup_enabled": true
  },
  "ui": {
    "theme": "light",
    "language": "el"
  }
}
```

## 🧪 Δοκιμές

Για δημιουργία δεδομένων δοκιμής:

```bash
create_test_data.bat
```

Για εκτέλεση signal tester:

```bash
start_signal_tester.bat
```

## � Πώς Λειτουργεί

### 🚀 Αρχιτεκτονική Συστήματος

Το autoPyrseia χρησιμοποιεί μια **πολυστρωματική αρχιτεκτονική** με σαφή διαχωρισμό αρμοδιοτήτων:

```
📁 downloads/pyrseia_server.pdf → 📊 PDF Ανάλυση → 👥 Επιλογή Παραληπτών → 📂 Αποθήκευση → 💾 Backup
```

### 🔄 Πλήρης Ροή Επεξεργασίας

#### **1. Ανίχνευση & Παρακολούθηση Σημάτων**
- **File Watcher** παρακολουθεί συνεχώς τον φάκελο `downloads/`
- Όταν εμφανιστεί το `pyrseia_server.pdf` → ξεκινά αυτόματα η επεξεργασία
- **Background scanning** για απουσιάζοντα JSON αρχεία κατά την εκκίνηση
- **Real-time monitoring** για συνημμένα και αλλαγές αρχείων

#### **2. Επεξεργασία & Ανάλυση PDF**
**PDFProcessor** εκτελεί τη διαδικασία:

```python
# Κεντρική διαδικασία εξαγωγής:
1. Εξαγωγή Κειμένου → Αφαίρεση headers/footers → Καθαρισμός περιεχομένου
2. Signal ID → Γραμμή πάνω από "FM"
3. FM Extract → "FM [περιεχόμενο]" χωρίς παρενθέσεις
4. Παραλήπτες → Ανάλυση TO/INFO τμημάτων, φιλτράρισμα με λίστα χρήστη
5. Θέμα → Εξαγωγή "ΘΕΜΑ:" περιεχομένου μέχρι "ΣΧΕΤ.:"
6. Συνημμένα → Ανάλυση αριθμημένων λιστών και τμημάτων συνημμένων
7. Serial Number → MD5 hash ολόκληρου του περιεχομένου PDF
```

**Έξυπνα Χαρακτηριστικά:**
- **Αφαίρεση Header/Footer**: Φιλτράρει timestamps, URLs, αριθμούς σελίδων
- **Ανίχνευση Αρχικού Μηνύματος**: Αφαιρεί ενσωματωμένα προηγούμενα σήματα
- **Manual Input Fallback**: Ανοίγει PDF αν αποτύχει η εξαγωγή κειμένου
- **Fuzzy File Matching**: Βρίσκει παρόμοια ονόματα συνημμένων

#### **3. Ανίχνευση Διπλότυπων & Εκδόσεων**
**DuplicateManager** διαχειρίζεται:

- **Παρακολούθηση Serial Number**: Χρήση MD5 hash πλήρους περιεχομένου PDF
- **Διαχείριση Εκδόσεων**: Δημιουργία `R 240846Z JUN 25(2)` για διπλότυπα
- **Recipient-Specific Versioning**: Διαφορετικές εκδόσεις ανά παραλήπτη
- **Επίλυση Συγκρούσεων Φακέλων**: Χειρισμός ίδιου ID, διαφορετικού FM

#### **4. Σύστημα Αποθήκευσης Σημάτων**
**SignalManager** οργανώνει:

```
📁 DATA/
├── 📂 ΛΑΦ ΙΩΑΝΝΙΝΩΝ/
│   ├── 📂 R 240846Z JUN 25/
│   │   ├── 📄 R 240846Z JUN 25.pdf
│   │   ├── 📄 signal_info.json
│   │   └── 📎 συνημμένα...
│   └── 📂 R 240846Z JUN 25(2)/  # Έκδοση διπλότυπου
└── 📂 ΣΠ ΙΩΑΝΝΙΝΩΝ/
    └── 📂 P 021615Z JUL 25/
```

**Χαρακτηριστικά Αποθήκευσης:**
- **JSON Metadata**: Πλήρη στοιχεία σήματος με ημερομηνία επεξεργασίας
- **Αυτόματη Δημιουργία Φακέλων**: Δομή Παραλήπτης → Signal ID
- **Αντιγραφή Συνημμένων**: Έξυπνη αντιστοίχιση και αντιγραφή αρχείων
- **Προσωρινοί Παραλήπτες**: Άμεση επιλογή φακέλου χωρίς συμμετοχή DATA

#### **5. Ροή Γραφικού Περιβάλλοντος**
**Signal Processing Tab** παρέχει:

1. **Real-time Display**: Εμφανίζει εξαγμένα στοιχεία σήματος άμεσα
2. **Επιλογή Παραληπτών**: Checkboxes για επεξεργασμένους παραλήπτες
3. **Δείκτες Συνημμένων**: Εμφανίζει κατάσταση απουσιάζοντων/βρεθέντων συνημμένων
4. **Manual Input Dialog**: Fallback για προβληματικά PDF
5. **Αποτελέσματα Επεξεργασίας**: Λεπτομερή reporting επιτυχίας/αποτυχίας

#### **6. Σύστημα Backup & USB Εξαγωγής**
**USB Extraction System**:
- **Δημιουργία Excel**: Δημιουργία συνοπτικών φύλλων εργασίας
- **Δομημένο Backup**: Μετακίνηση σημάτων σε `BACK UP DATA/` με αρίθμηση φακέλων
- **Λειτουργία Αναίρεσης**: Πλήρης αντιστροφή λειτουργιών εξαγωγής
- **Official/Unofficial Modes**: Έλεγχος συμπεριφοράς αρίθμησης φακέλων

### 🎯 Κύρια Σενάρια Επεξεργασίας

#### **Σενάριο A: Στάνταρ Επεξεργασία Σήματος**
```
1. PDF εμφανίζεται στο downloads/
2. File watcher ενεργοποιεί επεξεργασία
3. PDF αναλύεται → στοιχεία εξάγονται → παραλήπτες εμφανίζονται
4. Χρήστης επιλέγει παραλήπτες → κάνει κλικ "Επεξεργασία"
5. Σήμα αντιγράφεται σε DATA/[παραλήπτης]/[signal_id]/
6. JSON metadata δημιουργείται → downloads καθαρίζεται
```

#### **Σενάριο B: Χειρισμός Διπλότυπων Σημάτων**
```
1. Ίδιο σήμα ανιχνεύεται (ίδιος serial number)
2. Duplicate manager δημιουργεί versioned ID
3. Σήμα αποθηκεύεται ως "R 240846Z JUN 25(2)"
4. Αρχικό σήμα παραμένει άθικτο
5. Αμφότερες εκδόσεις συνυπάρχουν ανεξάρτητα
```

#### **Σενάριο C: Απαιτείται Manual Input**
```
1. Εξαγωγή κειμένου PDF αποτυγχάνει (σαρωμένο/κρυπτογραφημένο)
2. PDF ανοίγει αυτόματα για αναφορά χρήστη
3. Manual input dialog εμφανίζεται
4. Χρήστης εισάγει: Signal ID, FM, Θέμα, επιλέγει συνημμένα
5. Επεξεργασία συνεχίζεται με manual δεδομένα
```

#### **Σενάριο D: Επεξεργασία Προσωρινού Παραλήπτη**
```
1. Χρήστης επιλέγει "Προσωρινός Παραλήπτης"
2. Dialog επιλογής custom φακέλου
3. Σήμα αποθηκεύεται άμεσα στην επιλεγμένη τοποθεσία
4. ΧΩΡΙΣ συμμετοχή δομής φακέλων DATA/
5. ΧΩΡΙΣ δημιουργία JSON αρχείου (προσωρινή επεξεργασία)
```

### 🚀 Χαρακτηριστικά Απόδοσης & Αξιοπιστίας

#### **Threading & Concurrency**
- **Background Processing**: Όλες οι βαριές λειτουργίες εκτελούνται σε ξεχωριστά threads
- **UI Responsiveness**: Progress bars με ομαλές ενημερώσεις
- **Safe UI Updates**: `safe_schedule_ui_update()` αποτρέπει crashes

#### **Διαχείριση Σφαλμάτων**
- **Graceful Degradation**: Manual input όταν η αυτοματοποίηση αποτυγχάνει
- **File Recovery**: Attachment fuzzy matching για μετονομασμένα αρχεία
- **Progress Recovery**: Λειτουργίες μπορούν να ακυρωθούν/επανεκκινηθούν

#### **Διαχείριση Μνήμης**
- **Περιορισμοί Ιστορικού Αρχείων**: Αποτρέπει memory leaks στο file watcher
- **Λειτουργίες Καθαρισμού**: Αυτόματος καθαρισμός φακέλου downloads
- **Αποδοτική Σάρωση**: Επεξεργάζεται μόνο αλλαγμένα αρχεία

## �📝 Χαρακτηριστικά

### Επεξεργασία PDF

- Αυτόματη ανάλυση στρατιωτικών σημάτων
- Εξαγωγή FM, παραληπτών και θέματος
- Υποστήριξη ελληνικών χαρακτήρων
- Έξυπνο φιλτράρισμα παραληπτών

### Διαχείριση Ιστορικού

- 30-ημέρα διατήρηση ιστορικού
- Αυτόματος καθαρισμός παλαιών εγγραφών
- Πολλαπλών ημερών προβολή
- Λεπτομερή στατιστικά

### Γραφικό Περιβάλλον

- Σύγχρονο και φιλικό UI
- Πολλαπλές καρτέλες οργάνωσης
- Real-time ενημερώσεις
- Προγραμματιζόμενες λειτουργίες

### 🔧 Διαμόρφωση & Αποθήκευση
- **Auto-save Ρυθμίσεις**: Όνομα χρήστη, αριθμοί φακέλων αποθηκεύονται αυτόματα
- **JSON-based Storage**: Όλα τα metadata σημάτων σε δομημένη μορφή
- **Path Management**: Κεντρική διαχείριση καταλόγων
- **Migration Support**: Αυτόματες αναβαθμίσεις διαμόρφωσης

### 📈 Παρακολούθηση & Feedback
- **Real-time Progress**: Λεπτομερή progress bars για όλες τις λειτουργίες
- **Status Messages**: Σαφή feedback χρήστη για κάθε ενέργεια
- **History Tracking**: Πλήρη ιχνηλασιμότητα όλων των λειτουργιών
- **Error Reporting**: Λεπτομερή μηνύματα σφαλμάτων με προτάσεις αποκατάστασης

Το σύστημα έχει σχεδιαστεί για **στρατιωτικές ροές επεξεργασίας σημάτων** με έμφαση στην **αξιοπιστία, ιχνηλασιμότητα και ευκολία χρήσης**. Χειρίζεται πολύπλοκα σενάρια όπως διπλότυπα, απουσιάζοντα αρχεία και διάφορες μορφές PDF διατηρώντας ένα απλό, διαισθητικό περιβάλλον χρήστη.

## 🛠️ Ανάπτυξη

### Δομή Κώδικα

- **MVC Architecture**: Διαχωρισμός Model-View-Controller
- **Service Layer**: Επιχειρησιακή λογική σε υπηρεσίες
- **Modular Design**: Χωρισμένες λειτουργικότητες
- **Error Handling**: Ολοκληρωμένη διαχείριση σφαλμάτων

### Βασικές Τεχνολογίες

- **tkinter**: Γραφικό περιβάλλον
- **PyMuPDF (fitz)**: Επεξεργασία PDF
- **pathlib**: Διαχείριση διαδρομών
- **json**: Ρυθμίσεις και δεδομένα
- **datetime**: Χρονικά στοιχεία
- **hashlib**: MD5 serial number generation
- **threading**: Concurrency και background processing

### Αρχιτεκτονικά Patterns

- **Observer Pattern**: File watcher για monitoring
- **Strategy Pattern**: Διαφορετικές στρατηγικές επεξεργασίας
- **Factory Pattern**: Δημιουργία UI components
- **Singleton Pattern**: Configuration management
- **Command Pattern**: Undo/Redo λειτουργικότητα

## 🧪 Δοκιμές & Development Tools

### Test Infrastructure

- **Signal Tester**: Εργαλείο για δοκιμή σημάτων από φάκελο
- **Test Data Generator**: Δημιουργία διαφόρων σεναρίων δοκιμής
- **Duplicate Testing**: Εξειδικευμένες δοκιμές για ανίχνευση διπλότυπων
- **Manual Input Testing**: Δοκιμή fallback μηχανισμών

### Development Utilities

Για δημιουργία δεδομένων δοκιμής:

```bash
create_test_data.bat
```

Για εκτέλεση signal tester:

```bash
start_signal_tester.bat
```

## 📞 Υποστήριξη

- **Δημιουργός**: Σωτήριος Μπαλατσιάς
- **Τηλέφωνο**: 6983733346
- **Email**: [sotiris.mp@gmail.com]

## 📄 Άδεια

Αυτό το έργο διατίθεται υπό άδεια [MIT License](LICENSE).

## 🔄 Ενημερώσεις

### v2.0.0 (2025-09-04) - Current

- **🔄 Πλήρης αναδομή αρχιτεκτονικής**: Modular MVC design
- **🧠 Έξυπνη ανίχνευση διπλότυπων**: MD5-based serial numbers με versioning
- **👥 Βελτιωμένη διαχείριση παραληπτών**: Dropdown history με auto-cleanup
- **📊 Προηγμένο PDF processing**: Header/footer removal, fuzzy matching
- **🔧 USB extraction enhancements**: Excel generation, undo functionality
- **⚡ Performance optimizations**: Background processing, memory management
- **🎨 Enhanced UI/UX**: Visual feedback, progress indicators
- **🛡️ Robust error handling**: Graceful degradation, recovery mechanisms

### v1.1.0 (2025-08-25)

- Βελτιωμένη υποστήριξη ελληνικών
- 30-ημέρα όριο ιστορικού
- Βελτιωμένο PDF parsing
- Comprehensive test suite

### v1.0.0 (2025-08-18)

- Αρχική έκδοση
- Βασική λειτουργικότητα PDF επεξεργασίας
- Διαχείριση παραληπτών
- Γραφικό περιβάλλον tkinter

---

**⚠️ Σημείωση**: Η εφαρμογή αναπτύχθηκε για στρατιωτική χρήση. Όλα τα δεδομένα δοκιμής είναι φανταστικά και δεν περιέχουν πραγματικές πληροφορίες.
