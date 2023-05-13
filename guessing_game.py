import discord
import discord.ext
import random
import asyncio


# class MyClient(discord.Client):
#     def __init__(self):
#         print('self defined')
    
#     async def on_ready(self):
#         print(f'Logged in as {self.user} (ID: {self.user.id})')
#         print('------')

#     async def on_message(self, message):
#         # we do not want the bot to reply to itself
#         if message.author.id == self.user.id:
#             return

#         if message.content.startswith('$guess'):
#             await message.channel.send('Guess a number between 1 and 10.')

#             def is_correct(m):
#                 return m.author == message.author and m.content.isdigit()

#             answer = random.randint(1, 10)

#             try:
#                 guess = await self.wait_for('message', check=is_correct, timeout=5.0)
#             except asyncio.TimeoutError:
#                 return await message.channel.send(f'Sorry, you took too long it was {answer}.')

#             if int(guess.content) == answer:
#                 await message.channel.send('You are right!')
#             else:
#                 await message.channel.send(f'Oops. It is actually {answer}.')

intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

channel = None
game_state = None

@client.event
async def on_ready():
    await tree.sync()
    print("ready")

# make the slash command
@tree.command(name="dm", description="description")
async def dm(interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg, ephemeral=True)


@tree.command(name="pm", description="description")
async def pm(interaction: discord.Interaction, msg: str):
    await interaction.response.send_message(msg, ephemeral=False)


@tree.command(name="init", description="description")
async def init(interaction: discord.Interaction):
    global game_state
    global channel
    channel = interaction.channel
    game_state = {
        "is_started": False,
        "player_count": 0,
        "players": {}, # player_id -> player_name
        "current_turn": None, # player_id
        "current_votes": {}, # player_id -> vote_count
        "game_definition": "this is a simple game",
        "game_question": "this is a simple question",
        "game_answers": {},
    }
    await interaction.response.send_message("game initialized", ephemeral=False)


@tree.command(name="join", description="description")
async def join(interaction: discord.Interaction):
    global game_state
    player_id = game_state["player_count"]
    await interaction.response.send_message("you are user {}".format(player_id), ephemeral=True)
    game_state["players"][player_id] = interaction.user.name
    game_state["player_count"] += 1
    # breakpoint()
    # interaction.
    # response = interaction.response
    # channel = interaction.channel
    # await channel.send("abccbcb")
    # for member in interaction.guild.members:
    #     if member.bot:
    #         continue
    #     # game_state["player_count"] 
    #     # await member.send("member" + member.name)
    #     await response.send_message("member" + member.name, ephemeral=True)

    
@tree.command(name="start_game", description="description")
async def start_game(interaction: discord.Interaction):
    global game_state
    global channel
    # game definition: ...
    # round 1, question: ...
    # user 1: your turn
    await channel.send(game_state["game_definition"])
    await channel.send(game_state["game_question"])
    await interaction.response.send_message("user [i], your turn")
    
    def is_valid_reply(m):
        if m.content == 'harmful':
            return False
        return True
    
    ans = await client.wait_for('message', check=is_valid_reply)
    print(ans)

TOKEN = 'MTEwNjk2MTY0NjQ1NjQxODM3NQ.GPlzag.3U5QwuhYSkr-eUJsVmV8Fpwh_dpTSBrtTOnD1s'
client.run(TOKEN)