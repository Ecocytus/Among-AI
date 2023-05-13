import discord
import discord.ext
import random
import asyncio
from collections import defaultdict
from random import shuffle
from enum import Enum

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

game_state = None
class Phase(Enum):
    Join = 1
    Answer = 2
    Vote = 3

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
    game_state = {
        "phase": Phase.Join,
        "player_count": 0,
        "players": {}, # nickname -> player_name
        "current_turn": 0,
        "current_votes": defaultdict(int), # nickname -> vote_count
        "player_followups": {}, # nickname -> followup
        "voted_set": set(),
        "game_definition": "this is a simple game",
        "game_question": "this is a simple question",
        "game_answers": {}, # nickname, answer
        "order_list": [],
        "cur_idx": 0
    }
    await interaction.response.send_message("game initialized", ephemeral=False)


@tree.command(name="join", description="description")
async def join(interaction: discord.Interaction):
    global game_state
    player_id = game_state["player_count"]
    await interaction.response.send_message("you are user {}".format(player_id), ephemeral=True)
    await interaction.channel.send("user {} joined the game".format(player_id))
    # TODO: change to random name
    game_state["players"][str(player_id)] = interaction.user.name
    game_state["game_answers"][str(player_id)] = ""
    game_state["player_count"] += 1
    game_state["player_followups"][str(player_id)] = interaction.followup

    
@tree.command(name="start_game", description="description")
async def start_game(interaction: discord.Interaction):
    global game_state
    # game definition: ...
    # round 1, question: ...
    # user 1: your turn
    game_state['phase'] = Phase.Answer
    await interaction.channel.send(game_state["game_definition"])
    await interaction.channel.send(game_state["game_question"])
    tmp = list(game_state["players"].keys())
    shuffle(tmp)
    game_state["order_list"] = tmp
    cur_player = game_state["order_list"][game_state["cur_idx"]]
    await interaction.response.send_message("{}, it's your turn".format(cur_player))
    await game_state["player_followups"][cur_player].send("It's your turn", ephemeral=True)

@tree.command(name="ans", description="description")
async def ans(interaction: discord.Interaction, answer: str):
    global game_state

    cur_player = game_state["order_list"][game_state["cur_idx"]]
    if game_state["players"][cur_player] != interaction.user.name:
        await interaction.response.send_message("It's not your turn", ephemeral=True)
        return
    
    game_state["cur_idx"] += 1

    # Change to the superviosr AI answer this, also check if the answer is harmful or not
    await interaction.response.send_message("Sounds intersting!", ephemeral=True)
    await interaction.channel.send("{} give answer: {}".format(cur_player, answer))
    game_state["game_answers"][cur_player] = ans
    # TODO: format ans print the summary of all previous answerss

    if game_state["cur_idx"] == len(game_state["players"]):
        # end answering, start voting
        game_state['phase'] = Phase.Vote
        await interaction.channel.send("I have collected all the answers, let start voting.")
        return

    await game_state["player_followups"][cur_player].send("It's your turn", ephemeral=True)
    


@tree.command(name="vote", description="description")
async def vote(interaction: discord.Interaction, nickname: str):
    global game_state
    # /vote nickname: vote the user of the nickname as the AI
    if nickname not in game_state['players']:
        await interaction.response.send_message("This player has been kicked out or doesn't exist.", ephemeral=True)
        return
    if interaction.user.id in game_state["voted_set"]:
        await interaction.response.send_message("You have already voted", ephemeral=True)
        return
    game_state["voted_set"].add(interaction.user.id)
    game_state["current_votes"][nickname] += 1
    if len(game_state["voted_set"]) == len(game_state["players"]):
        # finish
        await interaction.channel.send("Vote ended, {} get the most vote".format(max(game_state["current_votes"], key=game_state["current_votes"].get)))
    await interaction.response.send_message("Thank you for the voting", ephemeral=True)
    

TOKEN = 'MTEwNjk2MTY0NjQ1NjQxODM3NQ.GYuP80.v_paJaZBfHQN8vE42iEwzqGBd7onvT5kWwtqfI'
client.run(TOKEN)