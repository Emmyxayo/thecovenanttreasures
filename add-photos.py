#!/usr/bin/env python3
"""
Add photos to the Covenant Treasures gallery.

    1. Put new photos in  raw-photos/   (HEIC straight off a phone is fine —
       no need to rename anything)
    2. Run:  python3 add-photos.py
    3. It converts each one, then asks you for a caption. A few words is plenty.
    4. Commit and push.

One-time setup in a fresh Codespace:
    pip install pillow pillow-heif

While it asks for captions it prints the path of each converted file, so you
can click it open in the editor to see which photo you are captioning.

Captions matter: they are what a screen reader announces, what Google indexes
for image search, and what shows under the photo in the lightbox.

Options:
    --auto       skip the questions; caption everything "School photo" and fix
                 them later by editing the alt="" text in index.html
    --dry-run    convert and report, but don't touch index.html
"""

import os
import re
import shutil
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is missing.  Run:  pip install pillow pillow-heif")

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC = True
except ImportError:
    HEIC = False

SRC = "raw-photos"
OUT = os.path.join("assets", "img", "gallery")
PAGE = "index.html"

MAX_WIDTH = 1400
QUALITY = 78
EXTS = (".heic", ".heif", ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")

AUTO = "--auto" in sys.argv
DRY = "--dry-run" in sys.argv


def slugify(text, fallback):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60] or fallback


def next_free(base):
    """Avoid clobbering an existing file if two captions slugify the same."""
    name, i = base, 2
    while os.path.exists(os.path.join(OUT, name + ".webp")):
        name = "%s-%d" % (base, i)
        i += 1
    return name


def main():
    if not os.path.isdir(SRC):
        os.makedirs(SRC, exist_ok=True)
        sys.exit("Created %s/ — put your photos in there and run this again." % SRC)

    if not os.path.isfile(PAGE):
        sys.exit("Can't find %s. Run this from the folder that contains it." % PAGE)

    os.makedirs(OUT, exist_ok=True)
    page = open(PAGE, encoding="utf-8").read()

    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(EXTS))
    if not files:
        sys.exit("No images found in %s/" % SRC)

    if not HEIC and any(f.lower().endswith((".heic", ".heif")) for f in files):
        print("! pillow-heif is not installed, so HEIC files will be skipped.")
        print("  Run:  pip install pillow-heif\n")

    # ---------------------------------------------------------- convert pass
    print("Converting %d file(s)...\n" % len(files))
    staged = []
    total_in = total_out = 0

    for n, filename in enumerate(files, 1):
        try:
            im = Image.open(os.path.join(SRC, filename))
        except Exception as exc:
            print("  skipped %s: %s" % (filename, exc))
            continue

        # apply the phone's rotation flag, then drop all metadata including GPS
        im = ImageOps.exif_transpose(im).convert("RGB")
        if im.width > MAX_WIDTH:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)),
                           Image.LANCZOS)

        tmp = os.path.join(OUT, "_staged-%02d.webp" % n)
        im.save(tmp, "WEBP", quality=QUALITY, method=6)

        a = os.path.getsize(os.path.join(SRC, filename))
        b = os.path.getsize(tmp)
        total_in += a
        total_out += b
        staged.append({"src": filename, "tmp": tmp, "im": im.size, "n": n})
        print("  %2d. %s  %dKB -> %dKB" % (n, filename, a // 1024, b // 1024))

    if not staged:
        sys.exit("Nothing was converted.")

    print("\n%d photos: %dMB -> %dKB\n" % (len(staged), total_in // 1024 // 1024,
                                           total_out // 1024))

    # ---------------------------------------------------------- caption pass
    if AUTO:
        for item in staged:
            item["caption"] = "School photo"
    else:
        print("-" * 62)
        print("Now a caption for each. A few words is plenty, e.g.")
        print('  "Inter-house sports day"   "Primary 4 science class"')
        print("Click the file path shown to open it and see which photo it is.")
        print("Press Enter on its own to skip a photo (it won't be added).")
        print("-" * 62 + "\n")

        for item in staged:
            print("[%d/%d]  %s" % (item["n"], len(staged), item["tmp"]))
            try:
                caption = input("   caption: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nStopped. Nothing has been added to index.html.")
                for s in staged:
                    if os.path.exists(s["tmp"]):
                        os.remove(s["tmp"])
                sys.exit(1)
            item["caption"] = caption
            print()

    # ------------------------------------------------------------ name + emit
    figures = []
    for item in staged:
        caption = item["caption"]
        if not caption:
            os.remove(item["tmp"])
            print("  skipped %s (no caption given)" % item["src"])
            continue

        base = next_free(slugify(caption, "photo-%02d" % item["n"]))
        final = os.path.join(OUT, base + ".webp")
        shutil.move(item["tmp"], final)

        w, h = item["im"]
        safe = caption.replace('"', "&quot;")
        figures.append(
            '      <figure><img src="assets/img/gallery/%s.webp" '
            'alt="%s" width="%d" height="%d" '
            'loading="lazy" decoding="async"></figure>' % (base, safe, w, h)
        )

    if not figures:
        sys.exit("\nNothing to add.")

    if DRY:
        print("\n--dry-run, so index.html was not changed. Markup:\n")
        print("\n".join(figures))
        return

    anchor = '<div class="gallery">'
    if anchor not in page:
        sys.exit("Couldn't find the gallery in index.html. Paste these in by hand:\n\n"
                 + "\n".join(figures))

    shutil.copy(PAGE, PAGE + ".bak")
    page = page.replace(anchor, anchor + "\n" + "\n".join(figures), 1)
    open(PAGE, "w", encoding="utf-8").write(page)

    print("\nAdded %d photo(s) to %s" % (len(figures), PAGE))
    print("(previous version saved as %s.bak)" % PAGE)
    print("Check it in the preview, then commit and push.")


if __name__ == "__main__":
    main()
