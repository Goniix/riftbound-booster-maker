#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sqlite3
import math

# Template import: different fpdf2 versions expose Template in different places.
try:
    from fpdf import Template
except Exception:
    from fpdf.template import Template  # fallback

con = sqlite3.connect("cards.db")
cursor = con.cursor()

def get_cards(cards: list[str], curs: sqlite3.Cursor) -> list[tuple[str, str]]:
    """
    Fetch cards whose id is in `cards`.
    Returns list of tuples: (front_art, back_art) using the same column indexes you used before.
    """
    if not cards:
        return []

    cardSet = set(cards)
    # Use parameterized query to avoid SQL injection and quoting issues
    placeholders = ",".join("?" for _ in cardSet)
    query = f"SELECT * FROM cards WHERE id IN ({placeholders})"
    data = curs.execute(query, tuple(cardSet)).fetchall()

    artDict: dict[str,tuple[str, str]] = dict()
    missing = cardSet.copy()
    for row in data:
        cid = str(row[0])
        missing.remove(cid)
        # keep your original chosen columns (row[3], row[6]) — adjust if your schema differs
        artDict[cid] = (str(row[3]), str(row[6]))

    # report missing ids
    for m in missing:
        print(f"could not find {m}")

    res = [artDict[cid] for cid in cards]

    return res

def print_page(cards: list[str], template: Template):
    """
    Accepts up to CARDS_P_PAGE card ids in `cards`, fetches art and writes them into the template.
    Template is expected to contain elements named card0..card{CARDS_P_PAGE-1}.
    """
    if not cards:
        return

    if len(cards) > CARDS_P_PAGE:
        # Either raise or silently trim — here we trim and warn
        print(f"Warning: received {len(cards)} cards, but CARDS_P_PAGE is {CARDS_P_PAGE}. Trimming.")
        cards = cards[:CARDS_P_PAGE]

    arts = get_cards(cards, cursor)
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
        sub = (i // ROW_COUNT)
        ind = ROW_COUNT - (i % ROW_COUNT) + (sub * ROW_COUNT) - 1
        template[f"card{ind}"] = card[1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser("printcards")
    parser.add_argument('tts', help="tts list of cards", nargs='*')
    args = parser.parse_args()

    TTS: list[str] = args.tts or []
    TTS = ["-".join(card_id.split("-")[:2]) for card_id in TTS]
    TTS = [s.lower() for s in TTS]

    CARDS_P_PAGE = 9
    ROW_COUNT = 3
    X_MARGIN = 0.77 / 2
    Y_MARGIN = 1.19 / 2

    templateElements = [
        {
            'name': f'card{i}',
            'type': 'I',
            'x1': X_MARGIN + 2.5 * (i % ROW_COUNT),
            'y1': Y_MARGIN + 3.5 * (i // ROW_COUNT),
            'x2': X_MARGIN + 2.5 * ((i % ROW_COUNT) + 1),
            'y2': Y_MARGIN + 3.5 * ((i // ROW_COUNT) + 1)
        } for i in range(CARDS_P_PAGE)
    ]

    templ = Template(format="A4", elements=templateElements, title="A4 Sheet", unit="in")

    if len(TTS) == 0:
        print("No cards provided, exiting.")
    else:
        slice_count = (len(TTS) + CARDS_P_PAGE - 1) // CARDS_P_PAGE
        for sl in range(slice_count):
            sli = TTS[sl * CARDS_P_PAGE: (sl + 1) * CARDS_P_PAGE]
            print(f"Processing slice {sl + 1}/{slice_count}: {sli}")
            print_page(sli, templ)

        templ.render("./template.pdf")
        print("Saved template.pdf")

    cursor.close()
    con.close()
