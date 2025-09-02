import discord
from discord.ext import commands
from discord import FFmpegPCMAudio,TextChannel
import random
import yt_dlp
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from classes import Base,Poll,MusicQueue,MemberLog


engine = create_engine("sqlite:///bot_data.db")

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


with open("config.json") as f:
    config = json.load(f)

TOKEN = config["DISCORD_TOKEN"]
PREFIX = "!"
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.command(name="commands")
async def list_commands(ctx):
    embed = discord.Embed(title="Available Commands")

    commands_list = [f"!{command}" for command in bot.commands]
    commands_string = "\n".join(commands_list)

    await ctx.send(embed=embed)
    await ctx.send(commands_string)


@bot.event
async def on_member_join(member):
    channel: TextChannel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}! 🎉")

    with SessionLocal() as session:
        log = MemberLog(
            member_id=member.id,
            member_name=member.name,
            action="join",
            timestamp=str(datetime.now())
        )
        session.add(log)
        session.commit()

@bot.event
async def on_member_remove(member):
    channel: TextChannel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"{member.name} has left the server.")


    with SessionLocal() as session:
        log = MemberLog(
            member_id=member.id,
            member_name=member.name,
            action="leave",
            timestamp=str(datetime.now())
        )
        session.add(log)
        session.commit()


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member.top_role >= ctx.me.top_role:
        await ctx.send("❌ I cannot kick this user because their role is higher than mine.")
        return
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} was kicked. Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member.top_role >= ctx.me.top_role:
        await ctx.send("❌ I cannot ban this user because their role is higher than mine.")
        return
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} was banned. Reason: {reason}")

@bot.command()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    if role >= ctx.me.top_role:
        await ctx.send("❌ I cannot assign a role higher than or equal to mine.")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.name} to {member.display_name}")


@bot.command()
async def roll(ctx):
    """Rolls a six-sided dice"""
    result = random.randint(1, 6)
    await ctx.send(f"🎲 You rolled a {result}!")

@bot.command()
async def poll(ctx, question: str = None, *options):
    if not question:
        await ctx.send("❌ You forgot to provide a question. Usage: `!poll \"Your question?\" option1 option2 ...`")
        return
    if len(options) < 2:
        await ctx.send("❌ You need at least 2 options. Usage: `!poll \"Your question?\" option1 option2 ...`")
        return

    lines = []
    for i, option in enumerate(options):
        lines.append(f"{i + 1}. {option}")
    description = "\n".join(lines)

    embed = discord.Embed(title=question, description=description)
    msg = await ctx.send(embed=embed)

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i in range(len(options)):
        await msg.add_reaction(emojis[i])

    with SessionLocal() as session:
        new_poll = Poll(question=question, options=json.dumps(options))
        session.add(new_poll)
        session.commit()


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"✅ Connected to {channel.name}")
    else:
        await ctx.send("❌ You are not in a voice channel!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected from the voice channel")
    else:
        await ctx.send("❌ I’m not in a voice channel!")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(join)
    vc = ctx.voice_client

    if vc.is_playing():
        vc.stop()

    ydl_opts = {"format": "bestaudio"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']

        with SessionLocal() as session:
            new_song = MusicQueue(
                guild_id=ctx.guild.id,
                title=info['title'],
                url=audio_url
            )
            session.add(new_song)
            session.commit()

        audio_source = FFmpegPCMAudio(audio_url, executable="ffmpeg")

        def after_playing(error):
            if error:
                print(f"Player error: {error}")

        vc.play(audio_source, after=after_playing)
        await ctx.send(f"▶️ Now playing: {info['title']}")
    except Exception as e:
        await ctx.send(f"❌ Could not play the URL. Error: {e}")

@bot.command()
async def pause(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("⏸️ Paused playback")
    else:
        await ctx.send("❌ Nothing is playing right now!")

@bot.command()
async def resume(ctx):
    vc = ctx.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("▶️ Resumed playback")
    else:
        await ctx.send("❌ Nothing is paused right now!")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏹️ Stopped playback")
    else:
        await ctx.send("❌ Nothing is playing right now!")


bot.run(TOKEN)