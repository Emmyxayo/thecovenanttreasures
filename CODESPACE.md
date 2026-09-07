# Adding photos in Codespaces

## First time in a new Codespace

```bash
pip install pillow pillow-heif
```

That's the only setup. Nothing else to install, no build step.

## Every time you want to add photos

```bash
mkdir -p raw-photos          # only needed once
# drag your photos into raw-photos/ in the file explorer
python3 add-photos.py
```

The script converts them (HEIC included), drops them into
`assets/img/gallery/`, and inserts them at the top of the gallery in
`index.html`. Then commit and push.

Use `python3 add-photos.py --dry-run` to see what it would do without
changing anything.

## Captions

You don't need to rename anything. After converting, the script asks you for a
caption for each photo, one at a time, and prints the converted file path so you
can click it open in the editor to see which one you're looking at.

Press Enter on its own to skip a photo — it won't be added.

Captions are what a screen reader announces, what Google indexes for image
search, and what shows under the photo in the lightbox, so a few real words
beat "Img 4412".

Use `python3 add-photos.py --auto` to skip the questions entirely and caption
everything "School photo", then fix the `alt=""` text in index.html later.

## Notes

- Re-running is safe. Anything already in the gallery is skipped.
- `index.html.bak` is written before each change, so you can always undo.
- `raw-photos/` is gitignored — the originals stay on your machine, only the
  converted versions get committed.
- All metadata including GPS coordinates is stripped during conversion.
- To remove a photo, delete its `<figure>` line from `index.html` and the file
  from `assets/img/gallery/`.
- To reorder, move the `<figure>` lines around. Top of the list shows first.

## Checking your work

In Codespaces, right-click `index.html` and choose "Open with Live Preview",
or run `python3 -m http.server 8000` and open the forwarded port.

Opening the file directly from the file explorer won't work properly — the
page needs to be served over http for everything to behave.
