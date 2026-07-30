import os
import json
import random
from datetime import date
try:
    from PIL import Image
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError as e:
    print("Got import error", e)
    print("You need to install pillow and pillow-heif: `pip3 install pillow pillow-heif`")
    import sys; sys.exit(1)

OUT = "image_widths_heights.json"

# Entries carry [name, [w, h], "YYYY-MM-DD"]. Known files reuse the stored
# dimensions and day, so old images are never re-opened — iCloud may have
# evicted their contents from disk (reading those hangs), and git checkouts
# reset mtimes; the JSON is the durable source of truth for both.
known = {}
if os.path.exists(OUT):
    for entry in json.load(open(OUT)):
        known[entry[0]] = [entry[1], entry[2] if len(entry) > 2 else None]

entries = []
for file in os.listdir("."):
    if file == OUT or not os.path.isfile(file):
        continue
    if file in known:
        dims, day = known[file]
        if day is None:  # first run after migration: fall back to mtime
            day = str(date.fromtimestamp(os.path.getmtime(file)))
        entries.append([file, dims, day])
        continue
    try:
        im = Image.open(file)
        dims = [im.width, im.height]
    except Exception:  # e.g. .DS_Store, lister.py, index.html
        continue
    entries.append([file, dims, str(date.fromtimestamp(os.path.getmtime(file)))])

# Oldest day first; within a day, shuffle (seeded by the date, so the order is
# stable across runs) so batches of similar screenshots don't cluster.
entries.sort(key=lambda e: (e[2], e[0]))
mixed = []
day_batch = []
current_day = None
for entry in entries:
    if entry[2] != current_day:
        random.Random(current_day).shuffle(day_batch)
        mixed.extend(day_batch)
        day_batch = []
        current_day = entry[2]
    day_batch.append(entry)
random.Random(current_day).shuffle(day_batch)
mixed.extend(day_batch)

json.dump(mixed, open(OUT, 'w'))
print(f"Successfully created {OUT} with {len(mixed)} files.")
