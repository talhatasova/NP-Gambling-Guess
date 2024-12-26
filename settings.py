from datetime import datetime
from discord import Colour, Embed, Interaction


class Constant():
    ID_LENGTH = 8
    BET_OUTCOMES = [1,0,2]

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
        NUMBER_GUESS = 1321601580222513253

class Emoji():
    X = "❌"
    CHECK = "✅"
    ZERO = "0️⃣"
    ONE = "1️⃣"
    TWO = "2️⃣"
    
    REACTION_ROLES = {
    "🎲": ID.Roles.GAMBLER
    }


class EmbedMessages():
    def getCorrectGuess(interaction:Interaction, guess:int) -> Embed:
        embed = Embed(
                title="🎉 Congratulations! 🎉",
                description=f"Well done {interaction.user.mention}! You've guessed the correct number **{guess}**! 🏆",
                colour=Colour.green(),
                timestamp=datetime.now()
            )
        embed.set_thumbnail(url=interaction.user.avatar.url)  # Set user's avatar as thumbnail
        embed.add_field(name="🏅 Rewards", value="You've earned a special yarrak for your win!", inline=False)
        embed.set_footer(text="@talhatasova @nicksizim54")
        return embed

    def getNewRound() -> Embed:
        embed = Embed(
                title="🎉 New Round Started!🎉",
                colour=Colour.blue(),
                timestamp=datetime.now()
            )
        embed.add_field(name="🏅 Rewards", value="Make your guesses for a special yarrak from Çüksüzüm54!", inline=False)
        embed.set_footer(text="Use /guess command to make your guess.")
        return embed