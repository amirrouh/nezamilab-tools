# Video Extractor

A minimal, standalone macOS application for extracting frames from video files at a custom interval. No installation required — just download and run.

**Developed by [Nezamilab](https://github.com/amirrouh/nezamilab-tools) · Harvard Medical School**

---

## Download

| Platform | Download |
|----------|----------|
| macOS (Apple Silicon + Intel) | [⬇ VideoExtractor.dmg](https://github.com/amirrouh/nezamilab-tools/releases/latest/download/VideoExtractor.dmg) |

> First launch: right-click → Open if macOS shows an "unidentified developer" warning (one-time only).

---

## Features

- Choose any video file (MP4, MOV, AVI, MKV, and more)
- Choose your output folder
- Set a frame interval — `1` = every frame, `2` = every other, `3` = every third, etc.
- Live preview: see how many frames will be extracted before you start
- Cancel extraction at any time
- Open output folder directly from the app when done
- 100% standalone — no Python, no dependencies needed on your machine

---

## Build from Source

Requirements: [uv](https://github.com/astral-sh/uv) (Python package manager)

```bash
git clone https://github.com/amirrouh/nezamilab-tools.git
cd nezamilab-tools/video-extractor
chmod +x build.sh
./build.sh
```

The app will be built at `dist/Video Extractor.app` and a distributable `dist/VideoExtractor.dmg` will be created automatically.

**Dependencies** (bundled automatically — not needed by end users):
- [OpenCV](https://opencv.org/) — video frame extraction
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI
- [PyInstaller](https://pyinstaller.org/) — standalone bundling

---

## Output

Frames are saved as JPEG files named sequentially:

```
frame_00001.jpg
frame_00002.jpg
frame_00003.jpg
...
```
