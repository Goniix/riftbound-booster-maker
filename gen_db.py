import sqlite3
import requests
import re
import os
import shutil
import pathlib

from rich.progress import Progress
    
class Card:
    rId : str
    name : str
    rarity : str
    art : str
    back : str
    rSet : str
    rType : str
    
    def __init__(self, card : dict) -> None:
        self.rId = "-".join(str(card["riftbound_id"]).split("-")[:2])
        self.name = str(card["name"])
        self.rarity =  str(card["classification"]["rarity"])
        self.art = str(card["media"]["image_url"])
        self.rSet = str(card["set"]["set_id"])
        self.rType = str(getType(self.rId, card))
        self.back = str(getBack(card, self.rType))
    
    def insert(self, cursor : sqlite3.Cursor):
        cursor.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?)", (self.rId, self.name, self.rarity, self.art, self.rSet, self.rType, self.back))
        
        
def getBack(card, cardType : str):
    classType = str(card["classification"]["type"])
    
    if classType == "Battlefield" or classType == "Legend":
        return "assets/CardBack_black.png"
    
    if cardType == "TKN":
        return "assets/CardBack_white.png"
    
    return "assets/CardBack_blue.png"

def getType(cardId: str, card)->str:
    cardId = cardId.upper()
    tokens = ["OGN-271", "OGN-272", "OGN-273", "OGN-274", "OGN-XXX"]
    runes = ["OGN-007", "OGN-007a", "OGN-042", "OGN-042a", "OGN-089", "OGN-089a", "OGN-126", "OGN-126a", "OGN-166", "OGN-166a", "OGN-214", "OGN-214a"]
    if cardId in tokens or cardId in runes or re.search(".*-[TR][0-9]+$",cardId) != None:
        return "TKN"
    
    isSigned = bool(card["metadata"]["signature"])
    isAlternate = bool(card["metadata"]["alternate_art"])
    isOvernumbered = bool(card["metadata"]["overnumbered"])
    
    if isAlternate: 
        return "ALT"
    if isOvernumbered:
        return "OVR"
    if isSigned:
        return "SGN"
    
    return "REG"

# def isPromoCard(cardId: str, cardName: str) -> bool:
#     return cardId.endswith("-p") or cardId.endswith("-P") or cardId.startswith("ARC") or cardName.endswith("Promo)") or cardName.endswith("(Oversized)")

def updateDatabase():
    with sqlite3.connect("cards.db") as con:
        cursor = con.cursor()
    
        try:
            cursor.execute("DROP TABLE IF EXISTS cards")
            cursor.execute("CREATE TABLE cards(id VARCHAR, name VARCHAR, rarity VARCHAR, image VARCHAR, setID CHAR(3), type VARCHAR, back VARCHAR)")
            res = requests.get("https://api.riftcodex.com/cards?size=100")
            
            if(res.status_code != 200):
                print(f"Error detected : status_code is {res.status_code}")
                return
            
            resJson = res.json()
            
            if(resJson == None):
                print("error : couldn't read json")
            
            pagecount = resJson["pages"]
            cardCount = resJson["total"]
            with Progress() as pbar:
                
                task = pbar.add_task("Pulling data from RiftCodex...", total=cardCount)
            
                for i in range(1,pagecount+1):
                    resJson = requests.get(f"https://api.riftcodex.com/cards?page={i}&size=100").json()
                    
                    cardList = resJson["items"]
                    for card in cardList:
                        dto = Card(card)
                        dto.insert(cursor)
                        
                        pbar.advance(task)

            con.commit()
        finally:
            pass
    
def clearImageCache():
    cachePath = pathlib.Path("cache")
    if cachePath.exists():
        shutil.rmtree("cache")
    os.mkdir("cache")

def updateImageCache(cardList : list[str] = []):
    with sqlite3.connect("cards.db") as con:
        cursor = con.cursor()
        
        cachePath = pathlib.Path("cache")
        if not cachePath.exists():
            os.mkdir("cache")
            
        imageCount = 0
        
        with Progress() as pbar:
            if len(cardList) == 0:
                data = cursor.execute(f"SELECT * FROM cards").fetchall()
            else:
                placeholders = ",".join("?" for _ in cardList)
                data = cursor.execute(f"SELECT * FROM cards WHERE id IN ({placeholders})", tuple(cardList)).fetchall()
            
            task = pbar.add_task("Downloading images...", total=len(data))
            
            
            for row in data:
                cid = str(row[0])
                art_url = str(row[3])
                
                filePath = pathlib.Path(f"cache/{cid}.png")
                
                if not filePath.exists():
                    img_data = requests.get(art_url).content

                    with open(filePath, 'wb') as handler:
                        handler.write(img_data)
                        
                    imageCount+=1
                pbar.advance(task)
            
        print(f"(Downloaded {imageCount} missing images)")
        

if __name__ == "__main__":
    updateDatabase()
    updateImageCache()
    
