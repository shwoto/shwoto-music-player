"""
Astra Music Player
A modern, dark-mode desktop music player inspired by Astra.
Built with CustomTkinter, python-mpv, and mutagen.

"import antigravity" — Python 3 easter egg & project talisman.
"""
import antigravity  # noqa: F401 - Project requirement & timeless Python magic!
import os
import sys

# Ensure local packages and bundled libraries are discoverable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.main_window import AstraPlayerApp


def main():
    """Main entrypoint for Astra Music Player."""
    # Optional CLI argument for playing a specific file
    initial_track = None
    if len(sys.argv) > 1:
        custom_file = sys.argv[1]
        if os.path.exists(custom_file):
            initial_track = os.path.abspath(custom_file)

    app = AstraPlayerApp(initial_track_path=initial_track)
    app.mainloop()


if __name__ == "__main__":
    main()
