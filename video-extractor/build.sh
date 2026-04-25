#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Installing dependencies with uv..."
uv sync

echo "==> Building standalone .app with PyInstaller..."
uv run pyinstaller \
  --windowed \
  --name "Video Extractor" \
  --collect-all cv2 \
  --collect-all customtkinter \
  --hidden-import cv2 \
  --osx-bundle-identifier com.nezamilab.videoextractor \
  --noconfirm \
  main.py

echo "==> Forcing light mode in Info.plist (prevents dark-mode color override)..."
PLIST="dist/Video Extractor.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c \
  "Add :NSRequiresAquaSystemAppearance bool true" "$PLIST" 2>/dev/null || \
/usr/libexec/PlistBuddy -c \
  "Set :NSRequiresAquaSystemAppearance true" "$PLIST"

echo "==> Ad-hoc code signing (no Apple Developer account required)..."
codesign --force --deep --sign - "dist/Video Extractor.app"

# Remove quarantine so the app opens without Gatekeeper warning on this machine
xattr -cr "dist/Video Extractor.app" 2>/dev/null || true

echo "==> Creating DMG for distribution..."
hdiutil create \
  -volname "Video Extractor" \
  -srcfolder "dist/Video Extractor.app" \
  -ov -format UDZO \
  "dist/VideoExtractor.dmg" 2>/dev/null

echo ""
echo "✓  Built: $SCRIPT_DIR/dist/Video Extractor.app"
echo "✓  DMG:   $SCRIPT_DIR/dist/VideoExtractor.dmg"
echo ""
echo "   Sharing with others:"
echo "   - They may see 'unidentified developer' on first launch"
echo "   - They can right-click → Open to bypass it (once only)"
echo "   - Or run: xattr -cr 'Video Extractor.app'"
