# ✦ Astra Music Player

A sleek, modern, dark-mode desktop music player inspired by **Astra**. Built from scratch in Python by **Shivam Kumar Sinha**, featuring contemporary glassmorphic aesthetics, low-latency audio playback, and rich ID3 metadata extraction.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI: CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-7c3aed.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Engine: python--mpv](https://img.shields.io/badge/Audio-python--mpv-06b6d4.svg)](https://github.com/jaseg/python-mpv)

---

## 👨‍💻 Author & Attribution

**Astra Music Player** is custom-designed and developed by **Shivam Kumar Sinha**.

---

## ✨ Features (Phase 1 MVP)

- **Sleek Astra Dark Aesthetic**: Deep obsidian theme (`#090d16`) with electric violet (`#8b5cf6`) and cosmic cyan (`#06b6d4`) glowing accents.
- **Embedded Album Art Renderer**: Extracts ID3 APIC frames, MP4 covr, and Vorbis picture blocks via Mutagen and displays them in a high-res rounded showcase card.
- **Central Play / Pause Control**: Prominent, animated playback button with state toggling (`▶` / `⏸`) and hover effects.
- **Robust MPV Decoding**: Hardware-accelerated, gapless media playback powered by `python-mpv` and native `libmpv`.
- **Interactive Scrubber**: Real-time progress bar with live timestamp tracking and drag-and-drop seek support.
- **Volume & Navigation Controls**: 0–100% volume slider with dynamic icons (`🔊`, `🔉`, `🔇`) and 5-second jump controls (`⏮`, `⏭`).
- **Thread-Safe Architecture**: Uses a decoupled `queue.Queue` event polling pipeline to keep the GUI responsive and prevent Tkinter thread deadlocks.
- **Keyboard Shortcuts**: Native hotkey support for seamless desktop playback.
- **Python 3 Magic**: Includes `import antigravity`!

---

## 🏗 Architecture & Codebase Layout

```
Music player/
├── core/
│   ├── __init__.py           # Core module interfaces
│   ├── audio_engine.py       # MPV audio controller (events, seeking, volume, observers)
│   └── metadata.py           # Mutagen ID3, FLAC, and APIC album art extractor
├── gui/
│   ├── __init__.py           # GUI package exports
│   ├── theme.py              # Astra design tokens & color palette
│   └── main_window.py        # CustomTkinter interface with thread-safe event queue
├── assets/
│   ├── sample.mp3            # Bundled demo audio file with embedded metadata
│   └── default_cover.jpg     # Sleek cosmic fallback cover art
├── main.py                   # Main entrypoint (boots GUI & parses CLI args)
├── requirements.txt          # Python library dependencies
├── .gitignore                # Comprehensive Python repository ignore rules
├── LICENSE                   # MIT License (Shivam Kumar Sinha)
└── README.md                 # Complete documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites (Native `libmpv`)

`python-mpv` interfaces with the native `libmpv` shared library. Install it using your operating system's package manager:

#### **Linux (Debian / Ubuntu / Kali)**
```bash
sudo apt update
sudo apt install -y libmpv-dev libmpv2 mpv
```

#### **Linux (Arch Linux / Fedora)**
```bash
# Arch Linux
sudo pacman -S mpv

# Fedora
sudo dnf install mpv-libs-devel
```

#### **macOS**
```bash
brew install mpv
```

#### **Windows**
1. Download a precompiled `mpv-dev` Windows build from [mpv.io](https://mpv.io/installation/).
2. Extract and place `mpv-2.dll` (or `libmpv-2.dll`) either in your Windows `PATH` or directly inside the `Music player/` directory.

---

### 2. Virtual Environment & Dependencies

Clone the repository and set up a virtual environment:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/music-player.git
cd "music-player"

# 2. Create a virtual environment
python3 -m venv .venv

# 3. Activate the virtual environment
# On Linux / macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

---

## 🎵 Running the Music Player

### Launch with Default Demo Track
```bash
python main.py
```
This loads the bundled sample track (*"Astra Horizon" by Antigravity Synth*) with embedded cover art.

### Launch with Any Local Audio File
You can pass any audio file path directly through the command line:
```bash
python main.py /path/to/your_song.mp3
```

### Loading Music Inside the App
Click the **"📂 Open File"** button in the top header to browse and open `.mp3`, `.flac`, `.wav`, `.ogg`, or `.m4a` files.

---

## ⌨ Desktop Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Space` | Toggle Play / Pause |
| `Left Arrow` (`←`) | Jump Backward 5 seconds |
| `Right Arrow` (`→`) | Jump Forward 5 seconds |

---

## 🛠 Technology Stack

- **Language**: Python 3.10+
- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Audio Engine**: [python-mpv](https://github.com/jaseg/python-mpv) / `libmpv`
- **Metadata & Tags**: [Mutagen](https://github.com/quodlibet/mutagen)
- **Image Processing**: [Pillow](https://python-pillow.org/)

---

## 🗺 Roadmap

- [ ] **Phase 2**: Playlist and queue manager with drag-and-drop song import.
- [ ] **Phase 3**: Real-time FFT audio visualizer (neon frequency wave).
- [ ] **Phase 4**: 10-band equalizer presets (Bass Boost, Acoustic, Rock, Vocal).
- [ ] **Phase 5**: Compact floating mini-player mode & system tray integration.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

Developed with ❤️ by **Shivam Kumar Sinha**.
