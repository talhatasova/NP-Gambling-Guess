from discord import Intents, Interaction, app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import database
from database import Gambler, Guess, Round
from settings import ID, EmbedMessages, Emoji
from exceptions import NoGamblerFoundException, CooldownException, DuplicateGuessException
# Initialize the bot
load_dotenv()
app_id = os.getenv("APP_ID")
token = os.getenv("DC_BOT_TOKEN")
public_key = os.getenv("PUBLIC_KEY")

# Initialize bot
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GAME_CHANNEL = ID.Channels.NUMBER_GUESS

current_round = database.get_current_round()
if not current_round:
    database.new_round()
    
CURRENT_NUMBER = database.get_current_round().number

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print(f"Bot is ready. Logged in as {bot.user}")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.tree.command(name="guess", description="Take your chance and shoot a number between [1, 10000] to win the surprise.")
@app_commands.describe(guess="Make your guess as a whole number from 1 to 10000, including edges.")
async def guess(interaction:Interaction, guess:int):
    if interaction.user.bot:
        return  # Ignore messages from bots

    # Check if the message is from the designated channel
    if interaction.channel.id != GAME_CHANNEL:
        return
    
    try:
        guess_value = int(guess)
        if guess_value < 1 or guess_value > 10000:
            await interaction.response.send_message("Please enter a valid integer for your guess between [1, 10000].", ephemeral=True)
            return
    except ValueError:
        await interaction.response.send_message("Please enter a valid integer for your guess between [1, 10000].", ephemeral=True)
    try:
        gambler_id = interaction.user.id
        isCorrect = database.make_guess(guess_value, gambler_id)
        if isCorrect:
            await interaction.response.send_message(embed=EmbedMessages.getCorrectGuess(interaction, guess_value))
            channel = interaction.guild.get_channel(GAME_CHANNEL)
            await channel.send(embed=EmbedMessages.getNewRound())
        else:
            guess_num = database.get_current_guess_num()
            until_next_hint = 500-guess_num if guess_num<500 else 750-guess_num if guess_num<750 else 1000-guess_num if guess_num<1000 else 0
            if guess_num == 500:
                release_hint(interaction=interaction, hint_level=1)
            elif guess_num == 750:
                release_hint(interaction=interaction, hint_level=2)
            elif guess_num == 1000:
                release_hint(interaction=interaction, hint_level=3)
            await interaction.response.send_message(f"❌ {interaction.user.mention}'s guess **{guess_value}** is {Emoji.GAY_FLAG}. Make **{until_next_hint}** more guesses to unlock a hint.", delete_after=3)
    except NoGamblerFoundException as e:
        new_gambler = database.add_gambler(interaction.user.id, interaction.user.global_name)
        await interaction.response.send_message(f"{e} Registering... {new_gambler}", ephemeral=True)
    except CooldownException as e:
        await interaction.response.send_message(f"{e}", ephemeral=True)
    except DuplicateGuessException as e:
        await interaction.response.send_message(f"{e}", delete_after=3)


async def release_hint(interaction:Interaction, hint_level:int):
    hintMsg = EmbedMessages.releaseHint(bot, hint_level)
    msg = await interaction.channel.send(embed=hintMsg)
    msg.pin()


@bot.tree.command(name="hint", description="Give a hint.")
@app_commands.describe(msg="Give a hint to the gamblers as a message")
async def hint(interaction:Interaction, msg:str):
    hintMsg = EmbedMessages.giveHint(interaction, msg)
    await interaction.response.send_message(embed=hintMsg)

@bot.tree.command(name="get_answer", description="Get the correct answer of the current round.")
@app_commands.default_permissions(administrator=True)
async def get_answer(interaction:Interaction):
    await interaction.response.send_message(embed=EmbedMessages.getAnswer(), ephemeral=True)

# Run the bot
bot.run(token)
