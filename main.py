import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import logging
import datetime

# Setup logging
logging.basicConfig(filename="discord.log", encoding="utf-8", level=logging.DEBUG)

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix=".", intents=intents)


# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"We are ready to go in {bot.user.name}")


# Handle unknown commands gracefully
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Did you type it correctly?")
    else:
        raise error


# Welcome new members with a DM
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server, {member.name}!")


# Moderate messages and process commands
@bot.event
async def on_message(message):
    print(message.content)

    # Ignore messages from bots
    if message.author.bot:
        return

    # Process commands first
    await bot.process_commands(message)

    # Delete messages containing the word "bot"
    if "bot" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} Don't use that word")


# Command: hello
@bot.command()
async def hello(ctx):
    await ctx.reply(f"hi {ctx.author.mention}")


# Command: hi
@bot.command()
async def hi(ctx):
    await ctx.send("hoi")


@bot.command()
async def dm(ctx, member: discord.User, *, msg):
    embed = discord.Embed(
        title=f"Message from {ctx.author.name}",
        description=msg,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now(),
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    try:
        await member.send(embed=embed)
        await ctx.message.add_reaction("👍")
        await ctx.send(
            f"Successfully sent a DM to {member.mention}.",
            delete_after=delete_time,
            allowed_mentions=discord.AllowedMentions(users=False),
        )
    except discord.Forbidden:
        await ctx.send(
            f"Could not send a DM to {member.mention}. They may have DMs disabled or have blocked the bot.",
            delete_after=delete_time,
        )
    except Exception as e:
        # Handle other potential errors
        await ctx.send(
            f"An error occurred while trying to send a DM: {e}",
            delete_after=delete_time,
        )


@bot.command()
@commands.is_owner()  # Only the bot owner can use this command
async def setavatar(ctx, file_path: str):
    """
    Sets the bot's avatar from a local file path.
    Example: !setavatar images/my_new_avatar.gif
    """
    try:
        with open(file_path, "rb") as image_file:
            await bot.user.edit(avatar=image_file.read())
        await ctx.send("Avatar updated successfully!", delete_after=delete_time)
    except FileNotFoundError:
        await ctx.send(
            f"Error: The file '{file_path}' was not found.", delete_after=delete_time
        )
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", delete_after=delete_time)


# time to delete messages

delete_time = 10  # seconds


@bot.command(name="purge", aliases=["clear"])
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send(
            "Please specify a positive number of messages more than 0 to delete ",
            delete_after=delete_time,
        )
        return
    try:
        deleted_messages = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(
            f"Successfully deleted {len(deleted_messages) -1}", delete_after=delete_time
        )
    except discord.Forbidden:
        await ctx.send(
            "I dont have permission to delete messages in this channel",
            delete_after=delete_time,
        )
    except discord.HTTPException as e:
        await ctx.send(
            f"An error occured while trying to delete the messages {e}",
            delete_after=delete_time,
        )


# Debug: List registered commands
print("commands should be written below this")
print("Registered commands:", [cmd.name for cmd in bot.commands])


# Run the bot
bot.run(token)
