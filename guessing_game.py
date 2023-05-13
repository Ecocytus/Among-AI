import discord
import discord.ext

intents = discord.Intents.all() 
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

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
    await interaction.response.send_message(msg, "command")

TOKEN = ''
client.run(TOKEN)