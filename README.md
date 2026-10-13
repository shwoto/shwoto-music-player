# ✦ Astra Music Player

A sleek, modern, dark-mode desktop music player inspired by **Astra**. Built from scratch in Python using **CustomTkinter** for contemporary aesthetics, **python-mpv** for low-latency media decoding, and **mutagen** for extracting rich audio metadata and embedded album art.

---

## ✨ Features (Phase 1 MVP)

- **Astra Dark Aesthetic**: Glassmorphic slate dark mode with glowing Electric Violet (`#8b5cf6`) and Cosmic Cyan (`#06b6d4`) accents.
- **Embedded Album Art Display**: Automatic ID3 APIC & Vorbis picture extraction via Mutagen with high-res Lanczos rendering.
- **Central Play / Pause Control**: Prominent, responsive playback button with hover effects and state indication.
- **Robust MPV Playback**: Low-latency playback powered by `libmpv` with real-time `time-pos` observers.
- **Interactive Scrubber**: Seek to any timestamp smoothly by dragging the progress slider.
- **Volume & Jump Controls**: Volume slider (0-100%) and quick 5-second jump forward/backward buttons.
- **Modular Architecture**: Clean separation between Audio Engine, Metadata Extractor, Design System, and GUI.
- **Python 3 Talisman**: Features `import antigravity`!

---

## 🏗 Project Architecture

```
Music player/
├── core/
│   ├── __init__.py
│   ├── audio_engine.py       # High-level wrapper over python-mpv (seeking, volume, observers)
│   └── metadata.py           # Mutagen-based ID3/Vorbis tag & album art parser
├── gui/
│   ├── __init__.py
│   ├── theme.py              # Astra color palette & design tokens
│   └── main_window.py        # CustomTkinter GUI components & state binding
├── assets/
│   ├── sample.mp3            # Default demo MP3 with embedded tags & cover
│   └── default_cover.jpg     # Fallback cosmic album cover
├── lib/                      # Bundled shared libraries for zero-config Linux run
├── main.py                   # Application entrypoint (boots GUI & handles CLI arguments)
├── requirements.txt          # Python package requirements
├── .gitignore                # Clean repository rules
└── README.md                 # Project documentation
```

---

## 🚀 Installation & Setup

### 1. System Dependencies (`libmpv`)

`python-mpv` uses native `libmpv` for audio decoding. Ensure `libmpv` is available on your operating system:

#### **Linux (Debian / Ubuntu / Kali)**
```bash
sudo apt update
sudo apt install -y libmpv-dev libmpv2 mpv
```

#### **Linux (Arch / Fedora)**
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
Download the `mpv-dev` build from [mpv.io](https://mpv.io/installation/) or SourceForge, and place `mpv-2.dll` (or `libmpv-2.dll`) either in your system `PATH` or directly in the project directory.

---

### 2. Python Environment Setup

Create an isolated virtual environment and install the required Python packages:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On Linux / macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Upgrade pip & install dependencies
pip install -r requirements.txt
```

---

## 🎵 Running the Player

Launch the player using the bundled sample track:

```bash
python main.py
```

Or pass any audio file directly from the command line:

```bash
python main.py ~/Music/favorite_song.mp3
```

You can also click the **"📂 Open File"** button inside the app to load any `.mp3`, `.flac`, `.wav`, `.ogg`, or `.m4a` file.

### ⌨ Keyboard Shortcuts
- `Space`: Toggle Play / Pause
- `Left Arrow`: Jump backward 5 seconds
- `Right Arrow`: Jump forward 5 seconds

---

## 🗺 Roadmap (Upcoming Phases)

- [ ] **Phase 2**: Playlist & Queue management (drag-and-drop support, shuffle, repeat modes).
- [ ] **Phase 3**: Real-time frequency spectrum visualizer (FFT-based animated audio wave).
- [ ] **Phase 4**: 10-band Graphic Equalizer & Bass Boost presets.
- [ ] **Phase 5**: Mini-player overlay mode with system media notifications (`mpris` / Windows SMTC).
