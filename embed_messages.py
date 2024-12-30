from datetime import datetime
from discord import Colour, Embed, Interaction
from discord.ext.commands import Bot

from database import get_current_round, Round
from settings import Emoji

class EmbedMessages():
    def getCorrectGuess(interaction:Interaction, guess:int, guess_count:int) -> Embed:
        current_round = get_current_round()
        embed = Embed(
                title=f"🎉 Congratulations! Round#{current_round.id-1} is over!🎉",
                description=f"Well done {interaction.user.mention}! You've guessed the correct number **{guess}** after **{guess_count}** trials! 🏆",
                colour=Colour.green(),
                timestamp=datetime.now()
            )
        embed.set_thumbnail(url=interaction.user.avatar.url)  # Set user's avatar as thumbnail
        embed.add_field(name="🏅 Rewards", value="A random CS2 skin that is worth $2-$10", inline=False)
        embed.set_footer(text="@talhatasova @nicksizim54")
        return embed

    def getNewRound() -> Embed:
        current_round = get_current_round()
        embed = Embed(
                title=f"🎉 Round#{current_round.id} Started!🎉",
                colour=Colour.blue(),
                timestamp=datetime.now()
            )
        embed.add_field(name="🏅 Rewards", value="Make your guesses for a special yarrak from Çüksüzüm54!", inline=False)
        embed.set_footer(text="Use /guess command to make your guess.")
        return embed
    
    def giveHint(interaction:Interaction, msg:str) -> Embed:
        embed = Embed(
                title="🎉 New Hint Released!🎉",
                description=msg,
                colour=Colour.blue(),
                timestamp=datetime.now()
            )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_footer(text=f"Hint is given by {interaction.user.global_name}")
        return embed
    
    def releaseHint(bot:Bot, hint_level:int) -> Embed:
        current_round = get_current_round()
        match hint_level:
            case 1:
                if current_round.number > 5000:
                    msg = "Sayimiz 5000'den büyük ya da eşittir."
                elif current_round.number <= 5000:
                    msg = "Sayimiz 5000'den küçük ya da eşittir."
            case 2:
                if current_round.number % 2 == 0:
                    msg = "Sayimiz çifttir."
                elif current_round.number % 2 == 1:
                    msg = "Sayimiz tektir."
            case 3:
                sum_of_digits = sum(int(digit) for digit in str(current_round.number))
                msg = f"Sayimizin rakamlarinin toplamı: {sum_of_digits}"
        embed = Embed(
                title="🎉 New Hint Released!🎉",
                description=msg,
                colour=Colour.blue(),
                timestamp=datetime.now()
            )
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text=f"Hint is given by {bot.user.name}")
        return embed
    
    def getAnswer() -> Embed:
        current_round:Round = get_current_round()
        embed = Embed(
                title=f"{Emoji.CHECK} You requested the correct answer. {Emoji.CHECK}",
                description=f"**{current_round.number}**",
                colour=Colour.red(),
                timestamp=datetime.now()
            )
        return embed