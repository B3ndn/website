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
    import sys; sys.exit(1);

files = []
# oldest first, so the page can show images in the order they were added
for file in sorted(os.listdir("."), key=os.path.getmtime):
    try:
        im = Image.open(file)
        files.append([file, [im.width, im.height]])
    except: # e.g. .DS_Store, calculater.py, file
        continue
# Days stay chronological, but images within a day are shuffled so batches of
# similar back-to-back screenshots don't cluster. Seeded by date -> stable across runs.
mixed = []
day_batch = []
current_day = None
for entry in files:
    d = date.fromtimestamp(os.path.getmtime(entry[0]))
    if d != current_day:
        random.Random(str(current_day)).shuffle(day_batch)
        mixed.extend(day_batch)
        day_batch = []
        current_day = d
    day_batch.append(entry)
random.Random(str(current_day)).shuffle(day_batch)
mixed.extend(day_batch)
files = mixed

json.dump(files, open("image_widths_heights.json", 'w'))
print(f"Successfully created image_widths_heights.json with {len(files)} files.")