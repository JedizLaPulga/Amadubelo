<p align="center">
  <img src="img/amadubelo.png" alt="Amadubelo Logo" width="600">
</p>

<h1 align="center">⚡ Amadubelo</h1>

<p align="center">
  <strong>All-in-One Offline Utility Toolkit for Windows</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#building">Building</a> •
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-blue" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.10+-purple" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

---

## ✨ Overview

**Amadubelo** is a beautiful, user-friendly utility toolkit designed for regular Windows users. It combines powerful file conversion tools and system utilities in one sleek, modern application — all working completely **offline** with no internet required.

🔒 **Secure** — All processing happens locally on your machine  
⚡ **Fast** — No network latency, instant results  
🎨 **Beautiful** — Modern dark theme with purple accents  
📦 **Portable** — Single `.exe` file, no installation needed  

---

## 🚀 Features

### 📂 File Utilities

| Tool | Description |
|------|-------------|
| 📄 **PDF → Images** | Convert PDF pages to PNG or JPG |
| 📝 **DOCX → PDF** | Convert Word documents to PDF |
| 🖼️ **Images → PDF** | Combine multiple images into a single PDF |
| ✍️ **Text → PDF** | Create formatted PDFs from text files |
| 📉 **Compress** | Reduce image and PDF file sizes |
| 🔗 **Merge PDFs** | Combine multiple PDFs into one |
| ✂️ **Split PDF** | Extract specific pages from a PDF |

### 🖥️ System Utilities

| Tool | Description |
|------|-------------|
| 🧹 **Disk Cleanup** | Delete temp files, cache, and junk |
| 📊 **System Info** | View CPU, RAM, disk, and OS information |
| 🚀 **Startup Manager** | Manage programs that run at startup |
| 🔒 **Secure Shredder** | Permanently delete files (unrecoverable) |
| 📁 **Duplicate Finder** | Find and remove duplicate files |
| 🔋 **Battery Health** | Check battery status and remaining time |
| 📶 **Network Info** | View IP address and network details |
| 🗑️ **Recycle Bin** | Quick empty recycle bin |
| 💾 **Drive Analyzer** | Visual breakdown of disk space usage |

---

## 📥 Installation

### Option 1: Download (Recommended)
1. Go to [Releases](../../releases)
2. Download `Amadubelo.exe`
3. Double-click to run — that's it! ✨

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/JedizLaPulga/Amadubelo.git
cd Amadubelo

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

---

## 🎯 Usage

1. **Launch** Amadubelo by double-clicking the `.exe` file
2. **Choose a tab**: File Utilities or System Utilities
3. **Select a tool** by clicking its card
4. **Follow the on-screen instructions** — drag and drop files, select options, and click the action button
5. **Done!** Your files are processed locally and securely

### 💡 Tips
- Drag and drop files directly onto the drop zones
- Use the "Back" button to return to the tool selection
- Progress bars show real-time status for long operations

---

## 🔨 Building

To build the standalone `.exe` yourself:

```bash
# Install dependencies
pip install -r requirements.txt

# Run build script
python build.py
```

The executable will be created at `app/app.exe` (~50-80MB)

### Build Requirements
- Python 3.10+
- PyInstaller
- All dependencies from `requirements.txt`

### PDF to Images Note
The PDF → Images feature requires Poppler. For the standalone build, you may need to:
1. Download Poppler for Windows
2. Add it to PATH or include it in the build

---

## 🛠️ Tech Stack

- **GUI**: CustomTkinter (modern themed Tkinter)
- **PDF Processing**: pypdf, pdf2image, reportlab
- **Image Processing**: Pillow
- **System Info**: psutil
- **Build**: PyInstaller

---

## 📁 Project Structure

```
Amadubelo/
├── src/
│   ├── main.py              # Application entry point
│   ├── app.py               # Main window with tabs
│   ├── ui/
│   │   ├── components/      # Reusable UI components
│   │   ├── file_utilities/  # File utility views
│   │   └── system_utilities/ # System utility views
│   └── core/                # Business logic
├── img/
│   └── amadubelo.png        # Application logo
├── requirements.txt
├── build.py                 # Build script
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with 💜 by <a href="https://github.com/JedizLaPulga">JedizLaPulga</a>
</p>
