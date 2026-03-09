import sqlite3
import requests
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

def getCommonList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Common' AND type = 'REG'", (setID,))
    cards = res.fetchall()
    return cards

def getUncommonList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Uncommon'", (setID,))
    cards = res.fetchall()
    return cards

def getRareList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Rare'", (setID,))
    cards = res.fetchall()
    return cards

def getEpicList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Epic'", (setID,))
    cards = res.fetchall()
    return cards

def getAltList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'ALT'", (setID,))
    cards = res.fetchall()
    return cards

def getOverList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'OVR'", (setID,))
    cards = res.fetchall()
    return cards

def getSignedList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND type = 'SGN'", (setID,))
    cards = res.fetchall()
    return cards

def getTokenList(setID: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ?  AND type = 'TKN'", (setID,))
    cards = res.fetchall()
    return cards
    
def pickCount(cards : list[str], count : int):
    if count <0:
        return []
    random.shuffle(cards)
    return cards[:count]
        
def genBooster(setID : str):
    availableSets = ["OGN", "SFD", "OGS"]
    con = sqlite3.connect("cards.db")
    cursor = con.cursor()
    
    commons = pickCount(getCommonList(setID, cursor),7)
    uncommons = pickCount(getUncommonList(setID, cursor),3)
    
    flexList = pickCount(getUncommonList(setID, cursor),3) + pickCount(getRareList(setID, cursor),1)
    random.shuffle(flexList)
    flex = flexList[1:]
    
    
    epic = random.randrange(0,4) == 0
    alt = random.randrange(0,12) == 0
    over= random.randrange(0,72) == 0
    signed = random.randrange(0,720) == 0
    
    special: list[str] = []
    if epic:
        special += pickCount(getEpicList(setID, cursor),1)
    if alt:
        special += pickCount(getAltList(setID, cursor),1)
    if over:
        special += pickCount(getOverList(setID, cursor),1)
    if signed:
        special += pickCount(getSignedList(setID, cursor),1)
    
    rares =  pickCount(getRareList(setID, cursor),2 - len(special)) + special
        
        
    token = pickCount(getTokenList(setID, cursor),1)
    
    booster = commons + uncommons + flex + rares + token
    
    for card in booster:
        try:
            print(f"{card[1]} | {card[2]}")
        except:
            print(card)
    
genBooster("OGN")
    
    