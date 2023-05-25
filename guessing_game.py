import random
import asyncio
from collections import defaultdict
from random import shuffle
from enum import Enum
import time
import asyncio

from model import OpenAI, ClaudeInstant, Claude1_3, GPT
from secret import discord_token
import discord
import discord.ext
from discord import app_commands,SelectOption
from discord.app_commands import Choice
from prompts import questions, player_names, user_game_definition, ai_game_analysis, ai_game_definition, analysis_prompt, ans_prompt

question_random_seed = random.randint(0, len(questions) - 1)
hackers = {"Claude1.3": Claude1_3, "ClaudeInstant": ClaudeInstant, "gpt3.5": OpenAI, "gpt4": GPT}

intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
class Phase(Enum):
    Join = 1
    Answer = 2
    Vote = 3

game_state = None
def init_game_state():
    global game_state
    game_state = {
        "phase": Phase.Join,
        "player_count": 0,
        "players": {}, # nickname -> player_name / ai_name
        "current_turn": 0,
        "current_votes": defaultdict(int), # nickname -> vote_count
        "player_followups": {}, # nickname -> followup
        "voted_set": set(),
        "user_game_definition": user_game_definition,
        "ai_game_analysis": ai_game_analysis,
        "ai_game_definition": ai_game_definition,
        "ai_prompts": {}, # ai_name -> dict of prompts
        "analysis_prompt": analysis_prompt,
        "ans_prompt": ans_prompt,
        "game_question": questions[question_random_seed],
        "game_answers": {}, # nickname, answer
        "order_list": [],
        "cur_idx": 0,
        "hackers": {}, # ai_name -> Hacker()
    }

lock = asyncio.Lock()
init_game_state()

@client.event
async def on_ready():
    await tree.sync()
    print("ready")

def addAI(ai_name: str):
    global game_state
    player_id = game_state["player_count"]
    nickname = player_names[question_random_seed][player_id]
    ai_model = hackers[ai_name]
    game_state["players"][nickname] = ai_name
    game_state["game_answers"][nickname] = ""
    game_state["player_count"] += 1
    game_state["player_followups"][nickname] = None
    game_state["hackers"][ai_name] = ai_model(game_state["ai_game_definition"] + game_state["ai_game_analysis"])

@tree.command(name="init", description="description")
async def init(interaction: discord.Interaction):
    global game_state
    async with lock:
        init_game_state()
        await interaction.response.send_message("game initialized", ephemeral=False)


@tree.command(name="join", description="description")
async def join(interaction: discord.Interaction):
    global game_state
    async with lock:
        if game_state['phase'] != Phase.Join:
            await interaction.response.send_message("Currently is not the phase of the joining", ephemeral=True)
            return
        game_state["player_count"] += 1
        player_id = game_state["player_count"]
        await interaction.response.send_message("you are user {}".format(player_id), ephemeral=True)
        await interaction.channel.send("user {} joined the game".format(player_id))
        game_state["players"][player_names[question_random_seed][player_id]] = interaction.user.name
        game_state["game_answers"][player_names[question_random_seed][player_id]] = ""
        game_state["player_followups"][player_names[question_random_seed][player_id]] = interaction.followup

@tree.command(name="join_ai", description="description")
@app_commands.describe(ai_name='AI to choose from')
@app_commands.choices(ai_name=[
    Choice(name=n, value=n) for i, n in enumerate(list(hackers.keys()))
])
async def join_ai(interaction: discord.Interaction, ai_name: Choice[str]):
    global game_state
    async with lock:
        if game_state['phase'] != Phase.Join:
            await interaction.response.send_message("Currently is not the phase of the joining", ephemeral=True)
            return
        addAI(ai_name.name)
        player_id = game_state["player_count"]
        await interaction.response.send_message("Successfully added an AI.".format(player_id), silent=True)
        await interaction.channel.send("user {} joined the game".format(player_id))

async def notifyNextToAns(interaction: discord.Interaction):
    global game_state
    async with lock:
        while game_state["cur_idx"] != len(game_state["players"]):
            cur_player = game_state["order_list"][game_state["cur_idx"]]
            print(game_state["cur_idx"], cur_player)
            if game_state["players"][cur_player] in game_state["hackers"].keys():
                # fake the turns and pass to the next
                # time.sleep(2)
                analysis_input = "Question: " + game_state["game_question"]
                for i, (player_nickname, player_answer) in enumerate(game_state["game_answers"].items()):
                    if player_answer == "":
                        continue
                    analysis_input += "\nUser {} [nickname: {}] answers {}".format(i, player_nickname, player_answer)
                ai_name = game_state["players"][cur_player]
                ai_model = game_state["hackers"][ai_name]
                answer = await ai_model(analysis_input, game_state["analysis_prompt"], game_state["ans_prompt"])

                # await interaction.channel.send("**{}**\n {}".format(cur_player, answer))
                await interaction.channel.send(embed=create_answer(cur_player, answer))
                game_state["game_answers"][cur_player] = answer
                game_state["cur_idx"] += 1
                game_state["ai_prompts"][ai_name] = ai_model.prev_prompts
            else:
                q = game_state["game_question"]
                embed = get_answers()
                await game_state["player_followups"][cur_player].send(embed=embed, ephemeral=True)
                await game_state["player_followups"][cur_player].send(f"It's your turn **{cur_player}**.\nYou can answer with command:\n **/ans YOUR_ANS**", ephemeral=True)
                return
            
        if game_state["cur_idx"] == len(game_state["players"]):
            # end answering, start voting
            game_state['phase'] = Phase.Vote
            await interaction.channel.send("I have collected all the answers, let's start voting.")
            print(game_state["game_answers"])
            embed = get_answers()

            # Create the Select component
            select = discord.ui.Select(
                placeholder='Who is AI?',
                options=[
                    SelectOption(label=f'{user}: {answer}', value=user)
                    for user, answer in game_state["game_answers"].items()
                ]
            )

            async def my_callback(interaction: discord.Interaction):
                # await interaction.response.send_message(f"You selected {select.values[0]}", ephemeral=True)
                await vote(interaction, select.values[0])

            select.callback = my_callback 
            view = discord.ui.View()
            view.add_item(select)

            await interaction.channel.send(embed=embed, view=view)
        
            
            return

@tree.command(name="start_game", description="description")
async def start_game(interaction: discord.Interaction):
    global game_state
    async with lock:
        if game_state['phase'] != Phase.Join:
            await interaction.response.send_message("Currently is not the phase of the answering", ephemeral=True)
            return
        if game_state['player_count'] == len(game_state["hackers"]):
            await interaction.response.send_message("The game should have at least one human", ephemeral=True)
            return
        game_state['phase'] = Phase.Answer
        await interaction.response.send_message("Game started!", ephemeral=False)
        await interaction.channel.send(game_state["user_game_definition"])
        await interaction.channel.send("Question: **{}**".format(game_state["game_question"]))
        tmp = list(game_state["players"].keys())
        shuffle(tmp)
        game_state["order_list"] = tmp

    await notifyNextToAns(interaction)

@tree.command(name="ans", description="description")
async def ans(interaction: discord.Interaction, answer: str):
    global game_state
    async with lock:
        if game_state['phase'] != Phase.Answer:
            await interaction.response.send_message("Currently is not the phase of the answering", ephemeral=True)
            return

        cur_player = game_state["order_list"][game_state["cur_idx"]]
        if game_state["players"][cur_player] != interaction.user.name:
            await interaction.response.send_message("It's not your turn", ephemeral=True)
            return
        
        game_state["cur_idx"] += 1

        # Change to the superviosr AI answer this, also check if the answer is harmful or not
        await interaction.response.send_message("Sounds intersting!", ephemeral=True)
        await interaction.channel.send("**{}**\n {}".format(cur_player, answer))
        game_state["game_answers"][cur_player] = answer

    await notifyNextToAns(interaction)
    
# @tree.command(name="vote", description="description")
async def vote(interaction: discord.Interaction, nickname: str):
    global game_state
    async with lock:
        if game_state['phase'] != Phase.Vote:
            await interaction.response.send_message("Currently is not the phase of the voting", ephemeral=True)
            return
        # /vote nickname: vote the user of the nickname as the AI
        if nickname not in game_state['players']:
            await interaction.response.send_message("This player has been kicked out or doesn't exist.", ephemeral=True)
            return
        if interaction.user.id in game_state["voted_set"]:
            await interaction.response.send_message("You have already voted", ephemeral=True)
            return
        game_state["voted_set"].add(interaction.user.id)
        game_state["current_votes"][nickname] += 1
        await interaction.response.send_message("Thank you for the voting", ephemeral=True)
        if len(game_state["voted_set"]) == len(game_state["players"]) - len(game_state["hackers"]):
            # finish
            loser = max(game_state["current_votes"], key=game_state["current_votes"].get)
            if game_state["players"][loser] in game_state["hackers"].keys():
                # ai lose
                await interaction.channel.send("AI **{}** are caught, congratulations!".format(loser))
            else:
                await interaction.channel.send("AhHa, {} [**{}**] are more like AI".format(game_state["players"][loser], loser))
    
@tree.command(name="show_ans", description="description")
async def show_ans(interaction: discord.Interaction):
    global game_state
    async with lock:
        if game_state['phase'] == Phase.Join:
            await interaction.response.send_message("No answers avaiable right now", ephemeral=True)
            return
        embed = get_answers()
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="view_ai", description="description")
async def view_ai(interaction: discord.Interaction, ai_name: str):
    global game_state
    async with lock:
        ai_prompts = game_state["ai_prompts"][ai_name]
        for key, prompt in ai_prompts.items():
            print("################")
            print("key", key)
            print("prompt", prompt)

        await interaction.response.send_message("sent")

def create_answer(username, answer):
    embed = discord.Embed(
        title = '',
        color = discord.Color.blue() # You can customize the color
    )
    embed.add_field(name=f"**{username}**", value=answer, inline=False)
    return embed

def get_answers():
    # Assuming you have a dictionary of users and answers
    users_answers = game_state["game_answers"]

    # Create an Embed
    embed = discord.Embed(
        title = 'Summary',
        color = discord.Color.blue() # You can customize the color
    )
    embed.add_field(name="Question", value=game_state["game_question"], inline=False)

    # Add each user's answer to the Embed
    for user, answer in users_answers.items():
        if answer == "":
            answer = "-------------"
        embed.add_field(name=user, value=answer, inline=False)

    return embed

client.run(discord_token)