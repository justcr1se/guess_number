"""Generates simple 16x16 placeholder textures and 64x32 armor layer textures
for the Knight mod. Run once: `python3 generate_textures.py`.
Replace these with higher quality artwork (e.g. CC0 sets from OpenGameArt)
before release if desired."""

from PIL import Image, ImageDraw
import os

BASE = os.path.join(os.path.dirname(__file__), "src", "main", "resources",
                    "assets", "knightmod", "textures")
ITEM_DIR = os.path.join(BASE, "item")
ARMOR_DIR = os.path.join(BASE, "models", "armor")
os.makedirs(ITEM_DIR, exist_ok=True)
os.makedirs(ARMOR_DIR, exist_ok=True)

# Knight steel palette
STEEL_DARK = (60, 65, 80, 255)
STEEL_MID = (120, 130, 145, 255)
STEEL_LIGHT = (185, 195, 210, 255)
STEEL_HIGH = (235, 240, 250, 255)
GOLD_TRIM = (212, 175, 55, 255)
HANDLE_DARK = (60, 38, 22, 255)
HANDLE_LIGHT = (110, 70, 40, 255)
CLEAR = (0, 0, 0, 0)


def save(img, path):
    img.save(path)
    print("wrote", path)


def fill(img, points, color):
    for (x, y) in points:
        img.putpixel((x, y), color)


def make_helmet():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    # Visor outline shape (a great helm silhouette)
    shape = [
        "................",
        "................",
        "....DDDDDDDD....",
        "...DMMMMMMMMD...",
        "..DMLLLLLLLLMD..",
        "..DMLDDDDDDLMD..",
        "..DMLDHHHHDLMD..",
        "..DMLDDDDDDLMD..",
        "..DMLLLLLLLLMD..",
        "..DMLLDDDDLLMD..",
        "..DMLLLLLLLLMD..",
        "..DMMMMMMMMMMD..",
        "..DDDDDDDDDDDD..",
        "...DMMMMMMMMD...",
        "....DDDDDDDD....",
        "................",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT, "H": STEEL_HIGH}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    # Gold trim cross on forehead
    px[7, 6] = GOLD_TRIM
    px[8, 6] = GOLD_TRIM
    save(img, os.path.join(ITEM_DIR, "knight_helmet.png"))


def make_chestplate():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    shape = [
        "................",
        "...DDDD..DDDD...",
        "..DMMMMDDMMMMD..",
        ".DMLLLLMMLLLLMD.",
        ".DMLHHLMMLHHLMD.",
        ".DMLLLLGGLLLLMD.",
        ".DMLLLLGGLLLLMD.",
        ".DMLLLLMMLLLLMD.",
        ".DMLLLLLLLLLLMD.",
        ".DMLLLLGGLLLLMD.",
        ".DMLLLLGGLLLLMD.",
        ".DMLLLLLLLLLLMD.",
        ".DMMMMMMMMMMMMD.",
        ".DDDDDDDDDDDDDD.",
        "................",
        "................",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT,
              "H": STEEL_HIGH, "G": GOLD_TRIM}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    save(img, os.path.join(ITEM_DIR, "knight_chestplate.png"))


def make_leggings():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    shape = [
        "................",
        ".DDDDDDDDDDDDDD.",
        ".DMMMMMMMMMMMMD.",
        ".DMLLLLMMLLLLMD.",
        ".DMLHHLMMLHHLMD.",
        ".DMLLLLMMLLLLMD.",
        ".DMLLLLMMLLLLMD.",
        ".DMLLLL..LLLLMD.",
        ".DMLLLL..LLLLMD.",
        ".DMLLLL..LLLLMD.",
        ".DMLLLL..LLLLMD.",
        ".DMMMMM..MMMMMD.",
        ".DDDDDD..DDDDDD.",
        "................",
        "................",
        "................",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT, "H": STEEL_HIGH}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    save(img, os.path.join(ITEM_DIR, "knight_leggings.png"))


def make_boots():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    shape = [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "..DDDD....DDDD..",
        ".DMMMMD..DMMMMD.",
        ".DMLLMD..DMLLMD.",
        ".DMLLMD..DMLLMD.",
        ".DMLLMDDDDMLLMD.",
        ".DMLLLLMMLLLLMD.",
        ".DMMMMMMMMMMMMD.",
        ".DDDDDDDDDDDDDD.",
        "................",
        "................",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    save(img, os.path.join(ITEM_DIR, "knight_boots.png"))


def make_sword():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    shape = [
        "..............HD",
        ".............HLD",
        "............HLMD",
        "...........HLMD.",
        "..........HLMD..",
        ".........HLMD...",
        "........HLMD....",
        ".......HLMD.....",
        "......HLMD......",
        ".....HLMD.......",
        ".GGGGGGD........",
        "....GG..........",
        "...bbbb.........",
        "...bllb.........",
        "...bbbb.........",
        "..bb.....bb.....",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT,
              "H": STEEL_HIGH, "G": GOLD_TRIM,
              "b": HANDLE_DARK, "l": HANDLE_LIGHT}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    save(img, os.path.join(ITEM_DIR, "knight_sword.png"))


def make_dagger():
    img = Image.new("RGBA", (16, 16), CLEAR)
    px = img.load()
    shape = [
        "................",
        "................",
        "................",
        ".........HD.....",
        "........HLD.....",
        ".......HLMD.....",
        "......HLMD......",
        ".....HLMD.......",
        "....HLMD........",
        "...GGGGD........",
        "....bb..........",
        "....bb..........",
        "....bb..........",
        "...GGGG.........",
        "................",
        "................",
    ]
    colors = {"D": STEEL_DARK, "M": STEEL_MID, "L": STEEL_LIGHT,
              "H": STEEL_HIGH, "G": GOLD_TRIM, "b": HANDLE_DARK}
    for y, row in enumerate(shape):
        for x, c in enumerate(row):
            if c in colors:
                px[x, y] = colors[c]
    save(img, os.path.join(ITEM_DIR, "knight_dagger.png"))


# Armor layer textures: layer 1 is helmet/chest/boots, layer 2 is leggings.
# Each is 64x32. We draw the standard armor regions in steel tones.
def make_armor_layer(filename, leggings=False):
    img = Image.new("RGBA", (64, 32), CLEAR)
    draw = ImageDraw.Draw(img)

    def block(x, y, w, h, color):
        draw.rectangle([x, y, x + w - 1, y + h - 1], fill=color)

    def shaded(x, y, w, h):
        block(x, y, w, h, STEEL_MID)
        draw.rectangle([x, y, x + w - 1, y + h - 1], outline=STEEL_DARK)
        # highlight strip
        for hx in range(x + 1, x + w - 1):
            img.putpixel((hx, y + 1), STEEL_LIGHT)

    if not leggings:
        # Helmet (layer 1: pixels 0..32 wide, 0..16 tall area for head)
        # Head: top 8x8 at (8,0), sides at (0,8..16,8) etc.
        # Following vanilla armor uv layout for layer 1
        shaded(0, 0, 64, 16)   # head region
        shaded(16, 16, 24, 16)  # body
        shaded(0, 16, 16, 16)   # right arm/left arm region (sleeve)
        shaded(40, 16, 16, 16)  # right/left leg covering (boots)
        # Gold trim line on chest
        for x in range(20, 36):
            img.putpixel((x, 20), GOLD_TRIM)
        for x in range(20, 36):
            img.putpixel((x, 26), GOLD_TRIM)
    else:
        # Leggings layer 2 covers legs/lower body
        shaded(16, 16, 24, 16)  # waist/body
        shaded(0, 16, 16, 16)   # right leg
        shaded(40, 16, 16, 16)  # left leg
        # Belt
        for x in range(16, 40):
            img.putpixel((x, 18), GOLD_TRIM)

    save(img, os.path.join(ARMOR_DIR, filename))


def main():
    make_helmet()
    make_chestplate()
    make_leggings()
    make_boots()
    make_sword()
    make_dagger()
    make_armor_layer("knight_layer_1.png", leggings=False)
    make_armor_layer("knight_layer_2.png", leggings=True)


if __name__ == "__main__":
    main()
