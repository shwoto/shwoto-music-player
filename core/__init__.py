"""
Astra Music Player - Core Modules
"""
from .audio_engine import AudioEngine
from .metadata import extract_metadata, TrackMetadata

__all__ = ["AudioEngine", "extract_metadata", "TrackMetadata"]
