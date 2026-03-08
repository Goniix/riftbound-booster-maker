import sqlite3
import requests
import re
    
def getType(cardId: str)->str:
    tokens = ["OGN-271", "OGN-272", "OGN-273", "OGN-274", "OGN-XXX"]
    if cardId in tokens or re.search(".*-[TR][0-9]+$",cardId) != None:
        return "TKN"
    
    if re.search(".*-[0-9]{3}[aA]$",cardId) != None:
        return "ALT"
    
    try:
        spl = cardId.split("-")
        cardSet = str(spl[0])
        number = int(spl[1])
        match cardSet:
            case 'OGN':
                if number > 298:
                    return "OVR"
            case 'SFD':
                if number > 221:
                    return "OVR"
    except:
        pass

    return "REG"
    
        
    

def isPromoCard(cardId: str, cardName: str) -> bool:
    return cardId.endswith("-p") or cardId.endswith("-P") or cardId.startswith("ARC") or cardName.endswith("Promo)") or cardName.endswith("(Oversized)")

def isSignedCard(cardId: str)-> bool:
    return cardId.endswith("-STAR")

def isOgnRuneCard(cardId: str)->bool:
    ognRunes = ["OGN-007", "OGN-007a", "OGN-042", "OGN-042a", "OGN-089", "OGN-089a", "OGN-126", "OGN-126a", "OGN-166", "OGN-166a", "OGN-214", "OGN-214a"]
    return cardId in ognRunes

def updateDatabase():
    con = sqlite3.connect("cards.db")

    cursor = con.cursor()

    print("dropping table")
    cursor.execute("DROP TABLE IF EXISTS cards")
    print("creating table")
    cursor.execute("CREATE TABLE cards(id VARCHAR, name VARCHAR, rarity VARCHAR, image VARCHAR, setID CHAR(3), type VARCHAR)")
    print("fetching cards")
    res = requests.get("https://api.dotgg.gg/cgfw/getcards?game=riftbound&mode=plain")
    
    if(res.status_code != 200):
        print(f"Error detected : status_code is {res.status_code}")
        return
    
    print("reading json")    
    resJson = res.json()
    
    if(resJson == None):
        print("error : couldn't read json")
    
    for elem in resJson:
        cardId = str(elem["id"])
        cardName = str(elem["name"])
        
        isPromo = isPromoCard(cardId, cardName)
        isSigned = isSignedCard(cardId)
        ognRune = isOgnRuneCard(cardId)
        
        cardSet = cardId.split("-")[0]
        
        
        if(not isPromo and not isSigned and not ognRune):
            cardType = str(getType(cardId))
            cursor.execute("INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?)", (cardId, cardName, elem["rarity"], elem["image"], cardSet, cardType))
    
    cursor.close()
    con.commit()
    con.close()
        
        

updateDatabase()
    
