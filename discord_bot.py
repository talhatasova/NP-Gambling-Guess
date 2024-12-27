from discord import Intents, Interaction, app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import Gambler, Guess, Round
from database import get_current_round, new_round, make_guess, add_gambler
from settings import ID, EmbedMessages
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

current_round = get_current_round()
if not current_round:
    new_round()
    
CURRENT_NUMBER = get_current_round().number

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
        isCorrect = make_guess(guess_value, gambler_id)
        if isCorrect:
            await interaction.response.send_message(embed=EmbedMessages.getCorrectGuess(interaction, guess_value))
            channel = interaction.guild.get_channel(GAME_CHANNEL)
            await channel.send(embed=EmbedMessages.getNewRound())
        else:
            await interaction.response.send_message(f"❌ Oops, {interaction.user.mention}! Your guess of **{guess_value}** is shit. Try again!")
    except NoGamblerFoundException as e:
        new_gambler = add_gambler(interaction.user.id, interaction.user.global_name)
        await interaction.response.send_message(f"{e} Registering... {new_gambler}", ephemeral=True)
    except CooldownException as e:
        await interaction.response.send_message(f"{e}", ephemeral=True)
    except DuplicateGuessException as e:
        await interaction.response.send_message(f"{e}")

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
