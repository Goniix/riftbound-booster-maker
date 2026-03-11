#!/usr/bin/env python3
import argparse
import sqlite3
from fpdf import Template
from rich.progress import Progress
import gen_db

CARDS_P_PAGE = 9
ROW_COUNT = 3
X_MARGIN = 0.77 / 2
Y_MARGIN = 1.19 / 2

def get_cards_art(cards: list[str]) -> list[tuple[str, str]]:
    """
    Fetch cards whose id is in `cards`.
    Returns list of tuples: (front_art, back_art) using the same column indexes you used before.
    """
    if not cards:
        return []

    card_set = set(cards)
    placeholders = ",".join("?" for _ in card_set)

    with sqlite3.connect("cards.db") as con:
        cursor = con.cursor()

        query = f"SELECT * FROM cards WHERE id IN ({placeholders})"
        data = cursor.execute(query, tuple(card_set)).fetchall()

        art_dict: dict[str,tuple[str, str]] = dict()
        missing = card_set.copy()
        for row in data:
            cid = str(row[0])
            missing.remove(cid)

            art_dict[cid] = (f"cache/{cid}.png", str(row[6]))

        for m in missing:
            print(f"could not find {m}")

        res = [art_dict[cid] for cid in cards]

        return res

def print_page(cards: list[str], template: Template):
    """
    Accepts up to CARDS_P_PAGE card ids in `cards`, fetches art and writes them into the template.
    Template is expected to contain elements named card0..card{CARDS_P_PAGE-1}.
    """
    if not cards:
        return

    if len(cards) > CARDS_P_PAGE:
        print(f"Warning: received {len(cards)} cards, but CARDS_P_PAGE is {CARDS_P_PAGE}. Trimming.")
        cards = cards[:CARDS_P_PAGE]

    arts = get_cards_art(cards)
    if not arts:
        print("No arts found for this page, skipping.")
        return

    # Fronts
    template.add_page()
    for i, card in enumerate(arts):
        template[f"card{i}"] = card[0]

    # Backs: reproduce original index math (keeps your intended layout)
    template.add_page()
    for i, card in enumerate(arts):
        sub = i // ROW_COUNT
        ind = ROW_COUNT - (i % ROW_COUNT) + (sub * ROW_COUNT) - 1
        template[f"card{ind}"] = card[1]


if __name__ == "__main__":

    parser = argparse.ArgumentParser("printcards")
    parser.add_argument('-t','--tts', help="tts list of cards", nargs='*')
    parser.add_argument('-d','--refreshdb', help="refresh database", nargs='*')
    args = parser.parse_args()

    TTS: list[str] = args.tts or []
    TTS = ["-".join(card_id.split("-")[:2]) for card_id in TTS]
    TTS = [s.lower() for s in TTS]
    REFRESH_DATABASE :bool = args.refreshdb

    if REFRESH_DATABASE:
        gen_db.update_database()

    templateElements = [
        {
            'name': f'card{i}',
            'type': 'I',
            'x1': X_MARGIN + 2.5 * (i % ROW_COUNT),
            'y1': Y_MARGIN + 3.5 * (i // ROW_COUNT),
            'x2': X_MARGIN + 2.5 * ((i % ROW_COUNT) + 1),
            'y2': Y_MARGIN + 3.5 * ((i // ROW_COUNT) + 1)
        } for i in range(CARDS_P_PAGE)
    ] + [
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN, 'y1' : 0, 'x2' : X_MARGIN, 'y2' : Y_MARGIN},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5, 'y1' : 0, 'x2' : X_MARGIN  + 2.5, 'y2' : Y_MARGIN},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 5, 'y1' : 0, 'x2' : X_MARGIN  + 5, 'y2' : Y_MARGIN},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 7.5, 'y1' : 0, 'x2' : X_MARGIN  + 7.5, 'y2' : Y_MARGIN},

        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN, 'y1' : 3.5*3 +Y_MARGIN, 'x2' : X_MARGIN, 'y2' : 11.69},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5, 'y1' :3.5*3 +Y_MARGIN, 'x2' : X_MARGIN  + 2.5, 'y2' : 11.69},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 5, 'y1' : 3.5*3 +Y_MARGIN, 'x2' : X_MARGIN  + 5, 'y2' : 11.69},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 7.5, 'y1' : 3.5*3 +Y_MARGIN, 'x2' : X_MARGIN  + 7.5, 'y2' : 11.69},

        {'name' : "line0", 'type' : "L", 'x1' : 0, 'y1' : Y_MARGIN, 'x2' : X_MARGIN, 'y2' : Y_MARGIN},
        {'name' : "line0", 'type' : "L", 'x1' : 0, 'y1' : Y_MARGIN + 3.5, 'x2' : X_MARGIN, 'y2' : Y_MARGIN + 3.5},
        {'name' : "line0", 'type' : "L", 'x1' : 0, 'y1' : Y_MARGIN + 7, 'x2' : X_MARGIN, 'y2' : Y_MARGIN + 7},
        {'name' : "line0", 'type' : "L", 'x1' : 0, 'y1' : Y_MARGIN + 10.5, 'x2' : X_MARGIN, 'y2' : Y_MARGIN + 10.5},

        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5*3, 'y1' : Y_MARGIN, 'x2' : 8.27, 'y2' : Y_MARGIN},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5*3, 'y1' : Y_MARGIN + 3.5, 'x2' : 8.27, 'y2' : Y_MARGIN + 3.5},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5*3, 'y1' : Y_MARGIN + 7, 'x2' : 8.27, 'y2' : Y_MARGIN + 7},
        {'name' : "line0", 'type' : "L", 'x1' : X_MARGIN + 2.5*3, 'y1' : Y_MARGIN + 10.5, 'x2' : 8.27, 'y2' : Y_MARGIN + 10.5},
    ]

    templ = Template(format="A4", elements=templateElements, title="A4 Sheet", unit="in")

    if len(TTS) == 0:
        print("No cards provided, exiting.")
    else:
        gen_db.update_image_cache(list(TTS))

        slice_count = (len(TTS) + CARDS_P_PAGE - 1) // CARDS_P_PAGE
        with Progress() as pbar:
            task = pbar.add_task("Printing template...", total=slice_count)

            for sl in range(slice_count):
                sli = TTS[sl * CARDS_P_PAGE: (sl + 1) * CARDS_P_PAGE]
                print_page(sli, templ)

                pbar.advance(task)

            templ.render("./template.pdf")

        print("Saved template.pdf")
