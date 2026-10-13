"""
Modern CustomTkinter desktop interface for Astra Music Player.
Features dark-mode aesthetics, glowing accents, real-time audio progress sync,
and seamless mutagen metadata display.
"""
import os
import queue
import tkinter as tk
from tkinter import filedialog
from typing import Optional
from PIL import Image
import customtkinter as ctk

from core.audio_engine import AudioEngine
from core.metadata import extract_metadata, TrackMetadata
from . import theme


class AstraPlayerApp(ctk.CTk):
    """Main Application Window for Astra Music Player."""

    def __init__(self, initial_track_path: Optional[str] = None):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Window settings
        self.title("Astra Music Player")
        self.geometry("450 x 720")
        self.minsize(420, 680)
        self.configure(fg_color=theme.BG_DARK)

        # Asset paths
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.default_cover_path = os.path.join(self.project_dir, "assets", "default_cover.jpg")
        self.hardcoded_track_path = initial_track_path or os.path.join(self.project_dir, "assets", "sample.mp3")

        # State
        self.current_metadata: Optional[TrackMetadata] = None
        self.is_seeking = False
        self.total_duration = 0.0
        self._event_queue = queue.Queue()

        # Audio Engine Initialization
        self.engine = AudioEngine(
            on_time_update=lambda cur, tot: self._event_queue.put(("time", (cur, tot))),
            on_state_change=lambda is_play: self._event_queue.put(("state", is_play)),
            on_track_end=lambda: self._event_queue.put(("end", None)),
        )

        # Build UI Components
        self._build_ui()

        # Start event queue polling loop
        self._poll_event_queue()

        # Keyboard shortcuts
        self.bind("<space>", lambda event: self._toggle_play_pause())
        self.bind("<Left>", lambda event: self.engine.jump(-5.0))
        self.bind("<Right>", lambda event: self.engine.jump(5.0))

        # Protocol for clean exit
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Load initial track
        if os.path.exists(self.hardcoded_track_path):
            self._load_track(self.hardcoded_track_path, autoplay=False)
        else:
            self._set_placeholder_state()

    def _build_ui(self):
        """Builds all UI frames and widgets."""
        # Main Outer Container
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=theme.PANEL_BG,
            corner_radius=20,
            border_width=1,
            border_color=theme.PANEL_BORDER,
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Top Header Bar
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(18, 12))

        self.brand_label = ctk.CTkLabel(
            self.header_frame,
            text="✦ ASTRA PLAYER",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
        )
        self.brand_label.pack(side="left")

        self.badge_label = ctk.CTkLabel(
            self.header_frame,
            text="MVP v0.1",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.CARD_BG,
            text_color=theme.ACCENT_CYAN,
            corner_radius=8,
            padx=8,
            pady=2,
        )
        self.badge_label.pack(side="left", padx=10)

        self.btn_browse = ctk.CTkButton(
            self.header_frame,
            text="📂 Open File",
            width=90,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=theme.CARD_BG,
            hover_color=theme.CARD_BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=10,
            border_width=1,
            border_color=theme.CARD_BORDER,
            command=self._open_file_dialog,
        )
        self.btn_browse.pack(side="right")

        # 2. Album Cover Showcase Card
        self.cover_container = ctk.CTkFrame(
            self.main_container,
            width=250,
            height=250,
            fg_color=theme.CARD_BG,
            corner_radius=16,
            border_width=2,
            border_color=theme.CARD_BORDER,
        )
        self.cover_container.pack(pady=(10, 18))
        self.cover_container.pack_propagate(False)

        self.cover_label = ctk.CTkLabel(self.cover_container, text="")
        self.cover_label.place(relx=0.5, rely=0.5, anchor="center")

        # 3. Track Info (Title, Artist, Album)
        self.info_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=24, pady=(0, 15))

        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text="No Track Loaded",
            font=ctk.CTkFont(family="Inter", size=19, weight="bold"),
            text_color=theme.TEXT_PRIMARY,
            anchor="center",
        )
        self.title_label.pack(fill="x")

        self.artist_label = ctk.CTkLabel(
            self.info_frame,
            text="Select an audio file or press Play",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color=theme.TEXT_SECONDARY,
            anchor="center",
        )
        self.artist_label.pack(fill="x", pady=(3, 0))

        # 4. Progress Bar & Timestamp Row
        self.progress_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=24, pady=(5, 10))

        self.time_elapsed_label = ctk.CTkLabel(
            self.progress_frame,
            text="00:00",
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color=theme.TEXT_MUTED,
            width=40,
        )
        self.time_elapsed_label.pack(side="left")

        self.progress_slider = ctk.CTkSlider(
            self.progress_frame,
            from_=0,
            to=100,
            fg_color=theme.SLIDER_BG,
            progress_color=theme.SLIDER_PROGRESS,
            button_color=theme.SLIDER_BUTTON,
            button_hover_color=theme.SLIDER_BUTTON_HOVER,
            height=14,
            command=self._on_slider_interaction,
        )
        self.progress_slider.set(0)
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=8)

        # Release event to seek when user drops slider thumb
        self.progress_slider.bind("<ButtonRelease-1>", self._on_slider_release)

        self.time_total_label = ctk.CTkLabel(
            self.progress_frame,
            text="00:00",
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color=theme.TEXT_MUTED,
            width=40,
        )
        self.time_total_label.pack(side="right")

        # 5. Playback Controls Row
        self.controls_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.controls_frame.pack(pady=(10, 15))

        # Replay / Jump -5s
        self.btn_prev = ctk.CTkButton(
            self.controls_frame,
            text="⏮",
            width=46,
            height=46,
            font=ctk.CTkFont(size=16),
            fg_color=theme.CARD_BG,
            hover_color=theme.CARD_BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=23,
            border_width=1,
            border_color=theme.CARD_BORDER,
            command=lambda: self.engine.jump(-5.0),
        )
        self.btn_prev.pack(side="left", padx=14)

        # Central Play / Pause Button
        self.btn_play_pause = ctk.CTkButton(
            self.controls_frame,
            text="▶",
            width=64,
            height=64,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color=theme.ACCENT_PRIMARY,
            hover_color=theme.ACCENT_PRIMARY_HOVER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=32,
            border_width=2,
            border_color=theme.ACCENT_CYAN,
            command=self._toggle_play_pause,
        )
        self.btn_play_pause.pack(side="left", padx=14)

        # Jump +5s / Forward
        self.btn_next = ctk.CTkButton(
            self.controls_frame,
            text="⏭",
            width=46,
            height=46,
            font=ctk.CTkFont(size=16),
            fg_color=theme.CARD_BG,
            hover_color=theme.CARD_BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=23,
            border_width=1,
            border_color=theme.CARD_BORDER,
            command=lambda: self.engine.jump(5.0),
        )
        self.btn_next.pack(side="left", padx=14)

        # 6. Bottom Volume & Status Bar
        self.bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=24, pady=(10, 15))

        self.vol_icon_label = ctk.CTkLabel(
            self.bottom_frame,
            text="🔊",
            font=ctk.CTkFont(size=14),
            text_color=theme.TEXT_SECONDARY,
            width=24,
        )
        self.vol_icon_label.pack(side="left")

        self.volume_slider = ctk.CTkSlider(
            self.bottom_frame,
            from_=0,
            to=100,
            fg_color=theme.SLIDER_BG,
            progress_color=theme.ACCENT_CYAN,
            button_color=theme.TEXT_PRIMARY,
            button_hover_color=theme.ACCENT_CYAN,
            height=12,
            command=self._on_volume_change,
        )
        self.volume_slider.set(80)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=(8, 12))

        self.vol_percent_label = ctk.CTkLabel(
            self.bottom_frame,
            text="80%",
            font=ctk.CTkFont(size=11, family="Courier"),
            text_color=theme.TEXT_MUTED,
            width=35,
        )
        self.vol_percent_label.pack(side="left")

        # Status Badge Indicator
        status_text = "● MPV Ready" if self.engine.available else "⚠ MPV Unavailable"
        status_color = theme.ACCENT_CYAN if self.engine.available else theme.ACCENT_DANGER
        self.status_label = ctk.CTkLabel(
            self.main_container,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color=status_color,
        )
        self.status_label.pack(side="bottom", pady=(0, 8))

    def _load_track(self, filepath: str, autoplay: bool = False):
        """Extracts metadata via mutagen and loads track into AudioEngine."""
        self.hardcoded_track_path = filepath
        self.current_metadata = extract_metadata(filepath, default_cover_path=self.default_cover_path)

        # Update metadata display
        self.title_label.configure(text=self.current_metadata.title)
        artist_album_text = f"{self.current_metadata.artist} • {self.current_metadata.album}"
        self.artist_label.configure(text=artist_album_text)
        self.total_duration = self.current_metadata.duration
        self.time_total_label.configure(text=self.current_metadata.formatted_duration)

        # Update cover art
        if self.current_metadata.cover_image:
            self._update_cover_image(self.current_metadata.cover_image)
        elif os.path.exists(self.default_cover_path):
            img = Image.open(self.default_cover_path).convert("RGB")
            self._update_cover_image(img)

        # Load into engine
        self.engine.load(filepath, autoplay=autoplay)

    def _update_cover_image(self, pil_image: Image.Image):
        """Resizes and sets the cover art in the UI."""
        try:
            resized = pil_image.resize((240, 240), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(240, 240))
            self.cover_label.configure(image=ctk_img)
            self.cover_label.image = ctk_img
        except Exception as e:
            print(f"[UI] Error rendering album cover: {e}")

    def _set_placeholder_state(self):
        """Sets UI placeholder when no file is loaded yet."""
        if os.path.exists(self.default_cover_path):
            img = Image.open(self.default_cover_path).convert("RGB")
            self._update_cover_image(img)

    def _toggle_play_pause(self):
        """Invoked when the central Play/Pause button or Spacebar is pressed."""
        if not self.engine.is_loaded and os.path.exists(self.hardcoded_track_path):
            self._load_track(self.hardcoded_track_path, autoplay=True)
            return

        self.engine.toggle_play_pause()

    def _on_slider_interaction(self, value):
        """Fires while dragging the progress slider."""
        self.is_seeking = True
        curr_secs = (float(value) / 100.0) * self.total_duration
        self.time_elapsed_label.configure(text=self._format_seconds(curr_secs))

    def _on_slider_release(self, _event):
        """Fires when the user releases the mouse button on the slider."""
        if self.total_duration > 0:
            target_secs = (self.progress_slider.get() / 100.0) * self.total_duration
            self.engine.seek(target_secs)
        self.is_seeking = False

    def _on_volume_change(self, value):
        """Updates player volume from slider."""
        vol = int(value)
        self.engine.set_volume(vol)
        self.vol_percent_label.configure(text=f"{vol}%")
        if vol == 0:
            self.vol_icon_label.configure(text="🔇")
        elif vol < 50:
            self.vol_icon_label.configure(text="🔉")
        else:
            self.vol_icon_label.configure(text="🔊")

    def _open_file_dialog(self):
        """Allows opening any custom local audio file."""
        chosen = filedialog.askopenfilename(
            title="Open Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac"),
                ("All Files", "*.*"),
            ],
        )
        if chosen and os.path.exists(chosen):
            self._load_track(chosen, autoplay=True)

    # Event queue polling loop (ensures 100% thread safety for GUI updates)
    def _poll_event_queue(self):
        try:
            while not self._event_queue.empty():
                event_type, payload = self._event_queue.get_nowait()
                if event_type == "time":
                    cur_time, total_dur = payload
                    self._apply_time_update(cur_time, total_dur)
                elif event_type == "state":
                    self._apply_state_change(payload)
                elif event_type == "end":
                    self._apply_track_end()
        except queue.Empty:
            pass
        except Exception as e:
            print(f"[UI Event Error] {e}")
        finally:
            self.after(40, self._poll_event_queue)

    def _apply_time_update(self, current_time: float, total_duration: float):
        if total_duration > 0 and self.total_duration != total_duration:
            self.total_duration = total_duration
            self.time_total_label.configure(text=self._format_seconds(total_duration))

        if not self.is_seeking:
            self.time_elapsed_label.configure(text=self._format_seconds(current_time))
            if self.total_duration > 0:
                pct = (current_time / self.total_duration) * 100.0
                self.progress_slider.set(pct)

    def _apply_state_change(self, is_playing: bool):
        if is_playing:
            self.btn_play_pause.configure(text="⏸", fg_color=theme.ACCENT_CYAN, hover_color=theme.ACCENT_CYAN_HOVER)
        else:
            self.btn_play_pause.configure(text="▶", fg_color=theme.ACCENT_PRIMARY, hover_color=theme.ACCENT_PRIMARY_HOVER)

    def _apply_track_end(self):
        self.progress_slider.set(0)
        self.time_elapsed_label.configure(text="00:00")
        self.btn_play_pause.configure(text="▶", fg_color=theme.ACCENT_PRIMARY)

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        s = max(0, int(seconds))
        return f"{s // 60:02d}:{s % 60:02d}"

    def _on_closing(self):
        """Cleanup upon window closing."""
        self.engine.terminate()
        self.destroy()
