class Constant():
    ID_LENGTH = 8
    BET_OUTCOMES = [1,0,2]
    HINT_COUNTS = [2,5,7]
    GUESS_COOLDOWN = 3

class ID():
    class Roles():
        ADMIN = 330595330494169090
        GAMBLER = 1317238552886775869

    class Channels():
        ADMIN = 1317240924585201714
        MAC_SONUC = 1317239926202564608
        MAC_BILDIRIM = 1317239684493213757
        KAYIT = 1317239294242455602
        LEADERBOARD = 1317239426203783239
        NUMBER_GUESS = 1322739933810655303

class Emoji():
    X = "❌"
    CHECK = "✅"
    ZERO = "0️⃣"
    ONE = "1️⃣"
    TWO = "2️⃣"
    GAY_KISS = "👨🏿‍❤️‍💋‍👨🏿"
    GAY_FLAG = "🏳️‍🌈"
    CONFETTI = "🎉" 
    
    REACTION_ROLES = {
    "🎲": ID.Roles.GAMBLER
    }