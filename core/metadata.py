"""
Metadata extraction service for Astra Music Player.
Leverages mutagen to read tags and embedded cover artwork.
"""
import io
import os
from dataclasses import dataclass
from typing import Optional
from PIL import Image
import mutagen
from mutagen.id3 import ID3, APIC


@dataclass
class TrackMetadata:
    filepath: str
    title: str
    artist: str
    album: str
    duration: float
    cover_image: Optional[Image.Image] = None

    @property
    def formatted_duration(self) -> str:
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"


def extract_metadata(filepath: str, default_cover_path: Optional[str] = None) -> TrackMetadata:
    """
    Extracts tags, duration, and embedded cover art from an audio file.
    Falls back gracefully if tags or cover art are missing.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Audio file not found: {filepath}")

    basename = os.path.splitext(os.path.basename(filepath))[0]
    title = basename
    artist = "Unknown Artist"
    album = "Unknown Album"
    duration = 0.0
    cover_image: Optional[Image.Image] = None

    try:
        audio = mutagen.File(filepath)
        if audio is not None:
            if hasattr(audio, "info") and hasattr(audio.info, "length"):
                duration = float(audio.info.length)

            # 1. Try reading standard ID3 (MP3) tags
            if hasattr(audio, "tags") and audio.tags:
                tags = audio.tags

                # Title
                if "TIT2" in tags:
                    title = str(tags["TIT2"])
                elif "title" in tags:
                    title = str(tags["title"][0])

                # Artist
                if "TPE1" in tags:
                    artist = str(tags["TPE1"])
                elif "artist" in tags:
                    artist = str(tags["artist"][0])

                # Album
                if "TALB" in tags:
                    album = str(tags["TALB"])
                elif "album" in tags:
                    album = str(tags["album"][0])

                # Artwork from ID3 APIC
                for tag_val in tags.values():
                    if isinstance(tag_val, APIC):
                        try:
                            cover_image = Image.open(io.BytesIO(tag_val.data)).convert("RGB")
                            break
                        except Exception:
                            pass

                # Artwork from FLAC / Vorbis Picture
                if cover_image is None and hasattr(audio, "pictures") and audio.pictures:
                    try:
                        pic = audio.pictures[0]
                        cover_image = Image.open(io.BytesIO(pic.data)).convert("RGB")
                    except Exception:
                        pass

                # Artwork from MP4 / M4A 'covr'
                if cover_image is None and "covr" in tags:
                    try:
                        covr_data = tags["covr"][0]
                        cover_image = Image.open(io.BytesIO(covr_data)).convert("RGB")
                    except Exception:
                        pass
    except Exception as e:
        print(f"[Metadata] Warning parsing {filepath}: {e}")

    # Fallback to default cover if no cover was embedded
    if cover_image is None and default_cover_path and os.path.exists(default_cover_path):
        try:
            cover_image = Image.open(default_cover_path).convert("RGB")
        except Exception:
            pass

    return TrackMetadata(
        filepath=filepath,
        title=title,
        artist=artist,
        album=album,
        duration=duration,
        cover_image=cover_image,
    )
