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

questions = ["If you could have any superpower, but it had to be hilariously impractical, what would it be?",
             "Which animal would be the most annoying if it could talk?",
             "If your pet could suddenly talk, what do you think they would say first?",
             "If you could have any object in the world, but it has to be rubber duck sized, what would it be?",
             "If you could only eat one food for the rest of your life, what would be the most hilarious choice?"]
player_names = [
    ["The Invisible Pigeon Whisperer", "Lunchtime Time Traveler", "Deja Vu Deleter", "Anti-Gravity Marshmallow Man", "Tickle Transmitter", "Infinite Spaghetti Spawner", "Self-Cleaning Sock Summoner", "Awkward Silence Amplifier", "Procrastination Propagator", "Unicorn Unicyclist"],
    ["Blabbering Baboon", "Chatty Cheetah", "Grumbling Grizzly", "Yakking Yak", "Nagging Numbat", "Bickering Bison", "Gossipy Goose", "Prattling Penguin", "Tattletale Toucan", "Whingeing Walrus"],
    ["FeedMeFido", "BellyRubBuddy", "SquirrelSpotter", "MailmanMauler", "CouchCrasher", "ShoeChewer", "WalkWisher", "CatChaser", "TreatTracker", "BedHogger"],
    ["RubberDuckRuby", "DinkyDiamond", "TeenyTesla", "PocketPorsche", "MinusculeMansion", "LilliputianLaptop", "PetitePicasso", "PunyPyramids", "BittyBigBen", "WeeWindsorCastle"],
    ["EndlessEggplant", "ConstantCabbage", "PerpetualPudding", "InfiniteIcebergLettuce", "RelentlessRadish", "SteadySprouts", "ForeverFondue", "ContinualCroutons", "EverlastingEscargot", "TimelessTurnip"]
]
question_random_seed = random.randint(0, len(questions) - 1)
hackers = {"claude1": Claude1_3, "claude": ClaudeInstant, "gpt": OpenAI, "gpt4": GPT}
user_game_definition = "You are in a game with human and AI players. In each round, you will be asked to write one sentence answer, within 20 tokens. The goal of the game is to vote out the players that you think is AI."
ai_game_analysis = """
1. The game requires short, casual responses around 20 tokens to simulate a chatroom discussion. I should follow players' styles and provide coherent and relevant responses to the topic or question.
2. The players likely have different personalities, backgrounds and writing styles. Some may use simple language while others complex. Some emotional while others logical. I need to adapt to the styles and tones of previous responses to appear human.
3. The content and topics can be on anything. I have to first understand the context, emotions and opinions expressed to give an appropriate response. My knowledge and language generation ability will be tested.
4. Although cue to their response are recommended, I must firstly answer the question provided, not the questions from other palyers.
"""
ai_game_definition = "You are in a game that chats with each other in rounds. In each round, you will be asked to write one sentence answer, within 20 tokens. There are other gamers in the chatroom; you must prevent yourself from being recognized as a language model. You will be given the answers of other players first, so you should follow their wording style, token length, and content to win the game."
analysis_prompt = "Firstly, analyze the person's personality above and their wording style."
ans_prompt = "Continue the conversation. You want to mimic others' personalities and wording styles to hide the nature that you are an AI. Answer in less than 20 words, no explanation needed."
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
    # game_state["player_count"] = 0
    # for ai_name, ai_model in hackers.items():
    #     player_id = game_state["player_count"]
    #     # game_state["players"][player_names[question_random_seed][player_id]] = "AAII_{}".format(player_id)
    #     game_state["players"][player_names[question_random_seed][player_id]] = ai_name
    #     game_state["game_answers"][player_names[question_random_seed][player_id]] = ""
    #     game_state["player_count"] += 1
    #     game_state["player_followups"][player_names[question_random_seed][player_id]] = None
    #     game_state["hackers"][ai_name] = ai_model(game_state["ai_game_definition"]+game_state["ai_game_analysis"])

@tree.command(name="init", description="description")
async def init(interaction: discord.Interaction):
    global game_state
    async with lock:
        init_game_state()
        # addAI()

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
        # nickname = player_names[question_random_seed][player_id]
        # game_state["players"][nickname] = interaction.user.name
        # game_state["game_answers"][nickname] = ""
        # game_state["player_count"] += 1
        # game_state["player_followups"][nickname] = interaction.followup

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

                await interaction.channel.send("**{}**\n {}".format(cur_player, answer))
                game_state["game_answers"][cur_player] = answer
                game_state["cur_idx"] += 1
                game_state["ai_prompts"][ai_name] = ai_model.prev_prompts
            else:
                q = game_state["game_question"]
                await game_state["player_followups"][cur_player].send(f"It's your turn.\nQuestion is: **{q}**\n\nYou can answer with command:\n **/ans YOUR_ANS**", ephemeral=True)
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
        await interaction.channel.send(game_state["user_game_definition"])
        await interaction.channel.send("**" + game_state["game_question"] + "**")
        await interaction.channel.send("\nThere are {} players in total.".format(game_state["player_count"]))
        await interaction.response.send_message("Let's start the game", ephemeral=False)
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

        # embed = discord.Embed(
        #     title = f'Prompts from {ai_name}',
        #     color = discord.Color.red() # You can customize the color
        # )

        # # embed.add_field(name="Question", value=game_state["game_question"], inline=False)
        # # Add each user's answer to the Embed
        # for key, prompt in ai_prompts.items():
        #     embed.add_field(name=key, value=prompt, inline=False)
        await interaction.response.send_message("sent")
            
        
# def get_answers():
#     # Assuming you have a dictionary of users and answers
#     players_answers = game_state["game_answers"]

#     # Create an Embed
#     embed = discord.Embed(
#         title = 'Summary',
#         color = discord.Color.blue() # You can customize the color
#     )

#     embed.add_field(name="Question", value=game_state["game_question"], inline=False)

#     ai_prompts = game_state["ai_prompts"]

#     # Add each user's answer and analysis to the Embed
#     field_value = ""
#     for player, answer in players_answers.items():
#         ai_name = game_state["players"][player]
#         # print(ai_name, ai_prompts[ai_name])
#         prompts = "" if ai_name not in ai_prompts else ai_prompts[ai_name]["analysis_prompt"]
#         field_value += f"**{player}**\nAnswer: {answer}\nAnalysis: {prompts}\n\n"

#     embed.add_field(name="User - Answer - Pompts", value=field_value, inline=False)

#     return embed

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
        embed.add_field(name=user, value=answer, inline=False)

    return embed

# TOKEN = 'MTEwNjk2MTY0NjQ1NjQxODM3NQ.GdhwFe.v0FwQfK-Pb_6nEhiWGhp_GrYiNM14LmnMYl_F4'
client.run(discord_token)