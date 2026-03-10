import sqlite3
import random

#slot 1-7 : common
#slot 8-10 : uncommon
#slot 11 : foil common or uncommon or third rare -> uncommon or rare
#slot 12-13 : rare and betters
#slot 14 : rune or token

#common: 7
#uncommon: 3
#rare: 2~
#epic: 1/4~
#alt-art: 1/12~ => skins
#showcase: 1/72~ => any fullart
#signed: 1/720~ (osef)

def get_common_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Common' AND type = 'REG'", (set_id,))
    cards = res.fetchall()
    return cards

def get_uncommon_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Uncommon'", (set_id,))
    cards = res.fetchall()
    return cards

def get_rare_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Rare'", (set_id,))
    cards = res.fetchall()
    return cards

def get_epic_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Epic'", (set_id,))
    cards = res.fetchall()
    return cards

def get_alt_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'ALT'", (set_id,))
    cards = res.fetchall()
    return cards

def get_over_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'OVR'", (set_id,))
    cards = res.fetchall()
    return cards

def get_signed_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'SGN'", (set_id,))
    cards = res.fetchall()
    return cards

def get_token_list(set_id: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ?  AND type = 'TKN'", (set_id,))
    cards = res.fetchall()
    return cards

def pick_count(cards : list[str], count : int):
    if count <0:
        return []
    random.shuffle(cards)
    return cards[:count]

def gen_booster(set_id : str):
    availableSets = ["OGN", "SFD", "OGS"]
    con = sqlite3.connect("cards.db")
    cursor = con.cursor()

    commons = pick_count(get_common_list(set_id, cursor),7)
    uncommons = pick_count(get_uncommon_list(set_id, cursor),3)

    flex_list = pick_count(get_uncommon_list(set_id, cursor),3) + pick_count(get_rare_list(set_id, cursor),1)
    random.shuffle(flex_list)
    flex = flex_list[1:]


    epic = random.randrange(0,4) == 0
    alt = random.randrange(0,12) == 0
    over= random.randrange(0,72) == 0
    signed = random.randrange(0,720) == 0

    special: list[str] = []
    if epic:
        special += pick_count(get_epic_list(set_id, cursor),1)
    if alt:
        special += pick_count(get_alt_list(set_id, cursor),1)
    if over:
        special += pick_count(get_over_list(set_id, cursor),1)
    if signed:
        special += pick_count(get_signed_list(set_id, cursor),1)

    rares =  pick_count(get_rare_list(set_id, cursor),2 - len(special)) + special


    token = pick_count(get_token_list(set_id, cursor),1)

    booster = commons + uncommons + flex + rares + token

    for card in booster:
        try:
            print(f"{card[1]} | {card[2]}")
        except:
            print(card)

if __name__ == "__main__":
    gen_booster("OGN")
