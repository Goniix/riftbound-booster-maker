from enum import Enum
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

def getCommonList(set: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Common' AND type = 'REG'",set)
    cards = res.fetchall()
    return cards

def getUncommonList(set: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Uncommon' AND type = 'REG'",set)
    cards = res.fetchall()
    return cards

def getRareList(set: str, cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT * FROM cards WHERE setID = ? AND rarity = 'Rare' AND type = 'REG'",set)
    cards = res.fetchall()
    return cards
    
def pickCount(cards : list[str], count : int):
    random.shuffle(cards)
    return cards[:count]
        
    

def genBooster(set : str):
    availableSets = ["OGN", "SFD", "OGS"]
    con = sqlite3.connect("cards.db")
    cursor = con.cursor()
    
    commons = pickCount(getCommonList(set, cursor),7)
    print(commons)
    
genBooster("OGN")
    
    