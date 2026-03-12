import sqlite3
import pathlib
import re
import os
import shutil
import requests
from rich.progress import Progress
import pull_art

class Card:
    r_id : str
    name : str
    rarity : str
    art : str
    back : str
    r_set : str
    r_type : str

    def __init__(self, card : dict) -> None:
        self.r_id = "-".join(str(card["riftbound_id"]).split("-")[:2])
        self.name = str(card["name"])
        self.rarity =  str(card["classification"]["rarity"])
        self.art = str(card["media"]["image_url"])
        self.r_set = str(card["set"]["set_id"])
        self.r_type = str(get_type(self.r_id, card))
        self.back = str(get_back(card, self.r_type))
        self.sideways = str(card["classification"]["type"]) == "Battlefield"

    def insert(self, cursor : sqlite3.Cursor):
        query = "INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

        params = (self.r_id, self.name, self.rarity, self.art, self.r_set, self.r_type, self.back, self.sideways)
        cursor.execute(query, params)

def get_back(card, card_type : str):
    class_type = str(card["classification"]["type"])

    if class_type in ("Battlefield", "Legend"):
        return "assets/CardBack_black.png"

    if card_type == "TKN":
        return "assets/CardBack_white.png"

    return "assets/CardBack_blue.png"

def get_type(card_id: str, card)->str:
    card_id = card_id.upper()
    tokens = ["OGN-271", "OGN-272", "OGN-273", "OGN-274", "OGN-XXX"]
    runes = ["OGN-007", "OGN-007a", "OGN-042", "OGN-042a", "OGN-089", "OGN-089a", "OGN-126", "OGN-126a", "OGN-166", "OGN-166a", "OGN-214", "OGN-214a"]
    if card_id in tokens or card_id in runes or re.search(".*-[TR][0-9]+$",card_id) is not None:
        return "TKN"

    is_signed = bool(card["metadata"]["signature"])
    is_alternate = bool(card["metadata"]["alternate_art"])
    is_overnumbered = bool(card["metadata"]["overnumbered"])

    if is_alternate:
        return "ALT"
    if is_overnumbered:
        return "OVR"
    if is_signed:
        return "SGN"

    return "REG"

def update_database():
    with sqlite3.connect("cards.db") as con:
        cursor = con.cursor()

        try:
            cursor.execute("DROP TABLE IF EXISTS cards")
            cursor.execute("CREATE TABLE cards(id VARCHAR, name VARCHAR, rarity VARCHAR, image VARCHAR, setID CHAR(3), type VARCHAR, back VARCHAR, sideways BOOLEAN)")
            res = requests.get("https://api.riftcodex.com/cards?size=100", timeout=2000)

            if res.status_code != 200:
                print(f"Error detected : status_code is {res.status_code}")
                return

            res_json = res.json()

            if res_json is None:
                print("error : couldn't read json")

            page_count = res_json["pages"]
            card_count = res_json["total"]
            with Progress() as pbar:

                task = pbar.add_task("Pulling data from RiftCodex...", total=card_count)

                for i in range(1,page_count+1):
                    url = f"https://api.riftcodex.com/cards?page={i}&size=100"
                    res_json = requests.get(url, timeout=2000).json()

                    card_list = res_json["items"]
                    for card in card_list:
                        dto = Card(card)
                        dto.insert(cursor)

                        pbar.advance(task)

            con.commit()
        finally:
            pass

def clear_image_cache():
    cache_path = pathlib.Path("cache")
    if cache_path.exists():
        shutil.rmtree("cache")
    os.mkdir("cache")

if __name__ == "__main__":
    update_database()
    pull_art.update_image_cache([])
