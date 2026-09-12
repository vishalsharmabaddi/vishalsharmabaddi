"""Convert VishalK-preview.png into ASCII art for the profile SVG.

Usage: python face2ascii.py [cols] [rows]
Writes face.txt (ASCII) and face_preview.png (rendered check).
"""
import sys
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFont

SRC = r"C:\Users\Lenovo\Downloads\VishalK-preview.png"
COLS = int(sys.argv[1]) if len(sys.argv) > 1 else 44
# A monospace character cell is ~2.1x taller than wide; rows are derived from the
# crop so the face keeps its real proportions instead of stretching.
CHAR_ASPECT = 2.1
# Brightness thresholds -> character. Measured on the photo (0=black, 255=white):
#   hair ~41   neck ~107   beard ~121   lips ~162   shirt ~175   skin ~205   bg 255
# Skin is intentionally blank so the face isn't "busy".
LEVELS = [
    (60, "@"), (90, "%"), (115, "k"), (135, "j"), (155, "|"),
    (168, ";"), (176, ","), (196, "."), (256, " "),
]

def char_for(v):
    for limit, ch in LEVELS:
        if v < limit:
            return ch
    return " "

img = Image.open(SRC).convert("RGBA")
W, H = img.size

# Transparent background -> white. Anything less than half-opaque is treated as
# background too, so the soft cut-out edge doesn't turn into stray ` marks.
r, g, b, a = img.split()
mask = a.point(lambda v: 255 if v >= 128 else 0)
white = Image.new("RGB", img.size, (255, 255, 255))
img = Image.composite(img.convert("RGB"), white, mask)

# Crop to head + neck (500x500 image, face centred, shoulders start ~74% down).
crop = img.crop((int(W * 0.16), int(H * 0.03), int(W * 0.84), int(H * 0.76)))
cw, ch = crop.size
ROWS = int(sys.argv[2]) if len(sys.argv) > 2 else round(COLS * (ch / cw) / CHAR_ASPECT)

gray = ImageOps.grayscale(crop)
small = gray.resize((COLS, ROWS), Image.LANCZOS)

lines = []
for y in range(ROWS):
    row = "".join(char_for(small.getpixel((x, y))) for x in range(COLS))
    lines.append(row.rstrip())

text = "\n".join(lines)
open("face.txt", "w", encoding="utf-8").write(text)
print(text)

# Preview render (monospace, dark bg) so it can be eyeballed.
try:
    font = ImageFont.truetype("consola.ttf", 20)
except OSError:
    font = ImageFont.load_default()
pw, ph = int(COLS * 11.5) + 30, ROWS * 24 + 30
prev = Image.new("RGB", (pw, ph), "#161b22")
d = ImageDraw.Draw(prev)
for i, ln in enumerate(lines):
    d.text((15, 15 + i * 24), ln, font=font, fill="#c9d1d9")
prev.save("face_preview.png")
