import sqlite3
import pathlib
import os
import argparse
from PIL import Image
import requests
from rich.progress import Progress


def update_image_cache(card_list : list[str]):
    card_set = set(card_list)
    with sqlite3.connect("cards.db") as con:
        cursor = con.cursor()

        cache_path = pathlib.Path("cache")
        if not cache_path.exists():
            os.mkdir("cache")

        image_count = 0

        with Progress() as pbar:
            if len(card_set) == 0:
                data = cursor.execute("SELECT * FROM cards").fetchall()
                card_set = set(str(row[0]) for row in data)
            else:
                placeholders = ",".join("?" for _ in card_set)
                query = f"SELECT * FROM cards WHERE id IN ({placeholders})"
                data = cursor.execute(query, tuple(card_set)).fetchall()

            task = pbar.add_task("Downloading images...", total=len(data))

            downloaded : set[str] = set()

            for row in data:
                cid = str(row[0])
                art_url = str(row[3])
                sideways = bool(row[7])

                downloaded.add(cid)

                file_path = pathlib.Path(f"cache/{cid}.png")

                if not file_path.exists():
                    img_data = requests.get(art_url,timeout=2000).content


                    with open(file_path, 'wb') as handler:
                        handler.write(img_data)

                    if sideways:
                        img = Image.open(file_path)
                        rotated = img.rotate(90, expand=True)

                        rotated.save(file_path)

                    image_count+=1
                pbar.advance(task)

        print(f"(Downloaded {image_count})")

        missing = card_set.difference(downloaded)
        if len(missing) > 0:
            print(f"WARNING: some cards could not be found : {missing}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser("pull_art")
    parser.add_argument('-c','--cards', help="list of cards", nargs='*')
    args = parser.parse_args()

    CARDS: list[str] = args.cards or []
    update_image_cache(CARDS)
