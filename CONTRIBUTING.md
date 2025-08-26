# Contributing to autoPyrseia

Ευχαριστούμε για το ενδιαφέρον σας να συνεισφέρετε στο autoPyrseia!

## 🚀 Πώς να Συνεισφέρετε

### 1. Fork το Repository
```bash
git fork https://github.com/yourusername/autoPyrseia.git
git clone https://github.com/yourusername/autoPyrseia.git
cd autoPyrseia
```

### 2. Δημιουργήστε Feature Branch
```bash
git checkout -b feature/my-new-feature
```

### 3. Κάντε τις Αλλαγές σας
- Βεβαιωθείτε ότι ο κώδικας ακολουθεί τα υπάρχοντα standards
- Προσθέστε σχόλια στα ελληνικά για καλύτερη κατανόηση
- Δοκιμάστε τις αλλαγές σας με `create_test_data.bat`

### 4. Commit και Push
```bash
git add .
git commit -m "feat: περιγραφή της νέας λειτουργίας"
git push origin feature/my-new-feature
```

### 5. Δημιουργήστε Pull Request
Περιγράψτε τις αλλαγές σας και γιατί είναι χρήσιμες.

## 📝 Coding Standards

### Python Code
- **Encoding**: Χρησιμοποιήστε `# -*- coding: utf-8 -*-`
- **Docstrings**: Γράψτε τα σε ελληνικά για συνέπεια
- **Comments**: Ελληνικά για business logic, αγγλικά για technical
- **Naming**: Χρησιμοποιήστε descriptive ονόματα

### File Organization
```
app/
├── controllers/    # UI controllers
├── services/       # Business logic
├── ui/            # GUI components
└── utils/         # Helper functions
```

## 🐛 Bug Reports

Όταν αναφέρετε bug:
1. **Περιγραφή**: Τι συμβαίνει;
2. **Βήματα**: Πώς να αναπαράγουμε το πρόβλημα;
3. **Περιβάλλον**: Windows version, Python version
4. **Σφάλματα**: Screenshots ή error messages

## 🆕 Feature Requests

Για νέες λειτουργίες:
1. **Περιγραφή**: Τι θέλετε να προστεθεί;
2. **Use Case**: Γιατί είναι χρήσιμο;
3. **Implementation**: Έχετε ιδέες υλοποίησης;

## 🧪 Testing

Πριν το commit:
```bash
# Δοκιμή test data generation
create_test_data.bat

# Δοκιμή εφαρμογής
python main.py

# Δοκιμή signal tester
start_signal_tester.bat
```

## 📚 Development Setup

### Prerequisites
- Python 3.8+
- Windows 10/11
- Git

### Installation
```bash
git clone https://github.com/yourusername/autoPyrseia.git
cd autoPyrseia
pip install -r requirements.txt
```

### Development Dependencies
```bash
pip install reportlab  # For PDF creation
pip install pyinstaller  # For building executable
```

## 🎯 Priority Areas

Τομείς που χρειάζονται βελτίωση:
1. **PDF Processing**: Βελτίωση αλγορίθμων εξαγωγής
2. **UI/UX**: Μοντέρνο γραφικό περιβάλλον
3. **Testing**: Automated test suite
4. **Documentation**: Περισσότερη τεκμηρίωση
5. **Performance**: Βελτιστοποίηση ταχύτητας

## 📞 Επικοινωνία

- **Maintainer**: Σωτήριος Μπαλατσιάς
- **Phone**: 6983733346
- **GitHub Issues**: Για technical questions

## 📄 Code of Conduct

- Σεβαστείτε άλλους contributors
- Κρατήστε τη συζήτηση constructive
- Βοηθήστε newcomers
- Ακολουθήστε τα project standards

---

**Ευχαριστούμε για τη συμβολή σας!** 🙏
