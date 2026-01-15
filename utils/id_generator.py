# utils/id_generator.py

from datetime import datetime
import os

COUNTER_FILE = "data/parcel_counter.txt"


def generate_parcel_id():
    today = datetime.now().strftime("%Y%m%d")

    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("0")

    with open(COUNTER_FILE, "r+") as f:
        count = int(f.read().strip()) + 1
        f.seek(0)
        f.write(str(count))
        f.truncate()

    return f"LICS-{today}-{str(count).zfill(4)}"
