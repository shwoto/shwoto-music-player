"""
AudioEngine for Astra Music Player.
Wraps python-mpv for robust, gapless audio decoding, volume control,
time-pos property observation, and seeking.
"""
import ctypes
import ctypes.util
import os
import sys
from typing import Callable, Optional


def _ensure_libmpv_available():
    """
    Ensures libmpv can be discovered by python-mpv.
    Checks system library paths, and falls back to project local ./lib directory.
    """
    if os.name == "nt":
        # On Windows, add local lib to PATH
        local_lib = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lib"))
        if os.path.isdir(local_lib):
            os.environ["PATH"] = local_lib + os.pathsep + os.environ.get("PATH", "")
        return

    # On Linux/Unix: check if find_library already finds mpv
    found = ctypes.util.find_library("mpv")
    if not found:
        # Check project root ./lib
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        local_lib_dir = os.path.join(project_root, "lib")
        candidate_paths = [
            os.path.join(local_lib_dir, "libmpv.so.2"),
            os.path.join(local_lib_dir, "libmpv.so.1"),
            os.path.join(local_lib_dir, "libmpv.so"),
        ]
        target_lib = next((p for p in candidate_paths if os.path.exists(p)), None)
        if target_lib:
            # Preload local shared dependencies if present
            for dep in ["liblua5.2.so.0", "libsixel.so.1"]:
                dep_path = os.path.join(local_lib_dir, dep)
                if os.path.exists(dep_path):
                    try:
                        ctypes.CDLL(dep_path)
                    except Exception:
                        pass
            try:
                ctypes.CDLL(target_lib)
                orig_find = ctypes.util.find_library

                def _custom_find_library(name):
                    if name == "mpv":
                        return target_lib
                    return orig_find(name)

                ctypes.util.find_library = _custom_find_library
            except Exception as ex:
                print(f"[AudioEngine] Failed to preload local libmpv: {ex}")


# Attempt library configuration before importing mpv
_ensure_libmpv_available()

try:
    import mpv
    MPV_AVAILABLE = True
    MPV_IMPORT_ERROR = None
except Exception as e:
    MPV_AVAILABLE = False
    MPV_IMPORT_ERROR = str(e)


class AudioEngine:
    """
    High-level controller for MPV media playback.
    Dispatches UI callback events for real-time progress & status synchronization.
    """

    def __init__(
        self,
        on_time_update: Optional[Callable[[float, float], None]] = None,
        on_state_change: Optional[Callable[[bool], None]] = None,
        on_track_end: Optional[Callable[[], None]] = None,
    ):
        self.on_time_update = on_time_update
        self.on_state_change = on_state_change
        self.on_track_end = on_track_end

        self._player: Optional["mpv.MPV"] = None
        self._current_file: Optional[str] = None
        self._duration: float = 0.0
        self._time_pos: float = 0.0
        self._is_playing: bool = False
        self._is_loaded: bool = False
        self.available: bool = MPV_AVAILABLE
        self.error_message: Optional[str] = MPV_IMPORT_ERROR

        if self.available:
            self._init_mpv()

    def _init_mpv(self):
        """Initializes the MPV player instance and registers property observers."""
        try:
            self._player = mpv.MPV(
                ytdl=False,
                video=False,
                audio_client_name="AstraPlayer",
                volume=80,
            )

            # Observe playback time position
            @self._player.property_observer("time-pos")
            def _time_observer(_name, value):
                if value is not None:
                    self._time_pos = float(value)
                    if self.on_time_update:
                        self.on_time_update(self._time_pos, self._duration)

            # Observe track duration
            @self._player.property_observer("duration")
            def _duration_observer(_name, value):
                if value is not None:
                    self._duration = float(value)
                    if self.on_time_update:
                        self.on_time_update(self._time_pos, self._duration)

            # Observe pause status
            @self._player.property_observer("pause")
            def _pause_observer(_name, value):
                is_paused = bool(value)
                self._is_playing = not is_paused and self._is_loaded
                if self.on_state_change:
                    self.on_state_change(self._is_playing)

            # Observe end of file
            @self._player.property_observer("eof-reached")
            def _eof_observer(_name, value):
                if value:
                    self._is_playing = False
                    self._time_pos = 0.0
                    if self.on_state_change:
                        self.on_state_change(False)
                    if self.on_track_end:
                        self.on_track_end()

        except Exception as e:
            self.available = False
            self.error_message = f"Failed to initialize MPV: {e}"
            print(f"[AudioEngine Error] {self.error_message}")

    def load(self, filepath: str, autoplay: bool = False) -> bool:
        """Loads an audio file into the player."""
        if not self.available or not self._player:
            print(f"[AudioEngine] Cannot load file: MPV unavailable ({self.error_message})")
            return False

        if not os.path.exists(filepath):
            print(f"[AudioEngine] File not found: {filepath}")
            return False

        self._current_file = filepath
        self._player.loadfile(filepath, mode="replace")
        self._player.pause = not autoplay
        self._is_loaded = True
        self._is_playing = autoplay
        self._time_pos = 0.0

        if self.on_state_change:
            self.on_state_change(self._is_playing)
        return True

    def play(self) -> bool:
        """Starts or resumes playback."""
        if not self.available or not self._player:
            return False

        if not self._is_loaded and self._current_file:
            return self.load(self._current_file, autoplay=True)

        if self._is_loaded:
            self._player.pause = False
            self._is_playing = True
            if self.on_state_change:
                self.on_state_change(True)
            return True
        return False

    def pause(self) -> bool:
        """Pauses audio playback."""
        if not self.available or not self._player:
            return False

        if self._is_loaded:
            self._player.pause = True
            self._is_playing = False
            if self.on_state_change:
                self.on_state_change(False)
            return True
        return False

    def toggle_play_pause(self) -> bool:
        """Toggles between play and pause states."""
        if self._is_playing:
            return self.pause()
        else:
            return self.play()

    def seek(self, position_seconds: float):
        """Seeks to an absolute timestamp in seconds."""
        if not self.available or not self._player or not self._is_loaded:
            return
        target = max(0.0, min(position_seconds, self._duration if self._duration > 0 else position_seconds))
        try:
            self._player.seek(target, reference="absolute")
            self._time_pos = target
            if self.on_time_update:
                self.on_time_update(self._time_pos, self._duration)
        except Exception as e:
            print(f"[AudioEngine] Seek error: {e}")

    def jump(self, offset_seconds: float):
        """Relative seek forward or backward."""
        if not self.available or not self._player or not self._is_loaded:
            return
        new_pos = max(0.0, self._time_pos + offset_seconds)
        self.seek(new_pos)

    def set_volume(self, volume: int):
        """Sets playback volume (0 to 100)."""
        if not self.available or not self._player:
            return
        clamped = max(0, min(100, int(volume)))
        self._player.volume = clamped

    def get_volume(self) -> int:
        """Returns current volume percentage."""
        if not self.available or not self._player:
            return 80
        return int(self._player.volume or 80)

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def time_pos(self) -> float:
        return self._time_pos

    def terminate(self):
        """Cleanly terminates the MPV instance."""
        if self._player:
            try:
                self._player.terminate()
            except Exception:
                pass
            self._player = None
            self._is_loaded = False
            self._is_playing = False
