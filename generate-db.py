import sqlite3
import requests
import re
    
def getType(cardId: str)->str:
    cardId = cardId.upper()
    tokens = ["OGN-271", "OGN-272", "OGN-273", "OGN-274", "OGN-XXX"]
    runes = ["OGN-007", "OGN-007a", "OGN-042", "OGN-042a", "OGN-089", "OGN-089a", "OGN-126", "OGN-126a", "OGN-166", "OGN-166a", "OGN-214", "OGN-214a"]
    if cardId in tokens or cardId in runes or re.search(".*-[TR][0-9]+$",cardId) != None:
        return "TKN"
    return "REG"
    
        
    

def isPromoCard(cardId: str, cardName: str) -> bool:
    return cardId.endswith("-p") or cardId.endswith("-P") or cardId.startswith("ARC") or cardName.endswith("Promo)") or cardName.endswith("(Oversized)")

def updateDatabase():
    con = sqlite3.connect("cards.db")
    cursor = con.cursor()
    
    try:
        print("dropping table")
        cursor.execute("DROP TABLE IF EXISTS cards")
        cursor.execute("DROP TABLE IF EXISTS removed")
        print("creating table")
        cursor.execute("CREATE TABLE cards(id VARCHAR, name VARCHAR, rarity VARCHAR, image VARCHAR, setID CHAR(3), type VARCHAR)")
        cursor.execute("CREATE TABLE removed(id VARCHAR, name VARCHAR, rarity VARCHAR, image VARCHAR, setID CHAR(3), type VARCHAR)")
        print("fetching cards")
        res = requests.get("https://api.riftcodex.com/cards?size=100")
        
        if(res.status_code != 200):
            print(f"Error detected : status_code is {res.status_code}")
            return
        
        resJson = res.json()
        
        if(resJson == None):
            print("error : couldn't read json")
        
        pagecount = resJson["pages"]
        
        for i in range(1,pagecount+1):
            resJson = requests.get(f"https://api.riftcodex.com/cards?page={i}&size=100").json()
            
            cardList = resJson["items"]
            for card in cardList:
                print(card)
                cardId = "-".join(str(card["riftbound_id"]).split("-")[:2])
                cardName = str(card["name"])
                cardRarity = str(card["classification"]["rarity"])
                cardArtUrl = str(card["media"]["image_url"])
                
                isSigned = bool(card["metadata"]["signature"])
                isAlternate = bool(card["metadata"]["alternate_art"])
                isOvernumbered = bool(card["metadata"]["overnumbered"])
                
                cardSet = str(card["set"]["set_id"])
                
                cardType = str(getType(cardId))
                if isAlternate: 
                    cardType = "ALT"
                if isOvernumbered:
                    cardType = "OVR"
                if isSigned:
                    cardType = "SGN"
                
                cursor.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?)", (cardId, cardName, cardRarity, cardArtUrl, cardSet, cardType))
                    
            
        con.commit()
        
    finally:
        cursor.close()
        con.close()
        
        

updateDatabase()
    
