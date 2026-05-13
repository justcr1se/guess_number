"""Compose a single preview image showing all knight mod textures, upscaled
and labelled, so they are visible at a glance."""

from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.join(os.path.dirname(__file__), "src", "main", "resources",
                    "assets", "knightmod", "textures")

ITEMS = [
    ("Knight Helmet",      "item/knight_helmet.png"),
    ("Knight Chestplate",  "item/knight_chestplate.png"),
    ("Knight Leggings",    "item/knight_leggings.png"),
    ("Knight Boots",       "item/knight_boots.png"),
    ("Knight Sword",       "item/knight_sword.png"),
    ("Knight Dagger",      "item/knight_dagger.png"),
]

LAYERS = [
    ("Armor layer 1 (helmet + chest + boots)", "models/armor/knight_layer_1.png"),
    ("Armor layer 2 (leggings)",               "models/armor/knight_layer_2.png"),
]

ITEM_SCALE = 10   # 16 -> 160
LAYER_SCALE = 6   # 64x32 -> 384x192
PAD = 24
LABEL_H = 28
BG = (40, 42, 50)
FG = (235, 240, 250)

try:
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except OSError:
    font = ImageFont.load_default()


def open_scaled(rel, scale):
    img = Image.open(os.path.join(BASE, rel)).convert("RGBA")
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)


def tile(title, img):
    w = max(img.width, 200)
    h = LABEL_H + img.height
    out = Image.new("RGBA", (w, h), BG)
    d = ImageDraw.Draw(out)
    bbox = d.textbbox((0, 0), title, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((w - tw) / 2, 4), title, font=font, fill=FG)
    out.paste(img, ((w - img.width) // 2, LABEL_H), img)
    return out


item_tiles = [tile(name, open_scaled(p, ITEM_SCALE)) for name, p in ITEMS]
layer_tiles = [tile(name, open_scaled(p, LAYER_SCALE)) for name, p in LAYERS]

cols = 3
row_h = max(t.height for t in item_tiles)
col_w = max(t.width for t in item_tiles)
grid_w = cols * col_w + (cols + 1) * PAD
grid_rows = (len(item_tiles) + cols - 1) // cols
grid_h = grid_rows * row_h + (grid_rows + 1) * PAD

layer_row_h = max(t.height for t in layer_tiles)
layer_total_w = sum(t.width for t in layer_tiles) + (len(layer_tiles) + 1) * PAD

total_w = max(grid_w, layer_total_w)
total_h = grid_h + layer_row_h + PAD * 2

canvas = Image.new("RGBA", (total_w, total_h), BG)

# Item tiles grid
for i, t in enumerate(item_tiles):
    r, c = divmod(i, cols)
    x = PAD + c * (col_w + PAD) + (col_w - t.width) // 2 + \
        (total_w - grid_w) // 2
    y = PAD + r * (row_h + PAD)
    canvas.paste(t, (x, y), t)

# Layer tiles row
x = (total_w - layer_total_w) // 2 + PAD
y = grid_h + PAD
for t in layer_tiles:
    canvas.paste(t, (x, y + (layer_row_h - t.height) // 2), t)
    x += t.width + PAD

out_path = os.path.join(os.path.dirname(__file__), "knight_textures_preview.png")
canvas.convert("RGB").save(out_path)
print("wrote", out_path)
