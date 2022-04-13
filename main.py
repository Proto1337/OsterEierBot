import discord
import os
import asyncio
import json
import random
from discord.ext import commands
from discord.ui import InputText, Modal
from SECRET import TOKEN
from CONFIG import SERVER, EGGS

if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvloop.install()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="^.^")


bot = Bot()
# load guild id from SERVER.py in CONFIG/
guild = SERVER.GUILD
# load admin role from SERVER.py in CONFIG/
admin = SERVER.ADMINROLE
# load number of eggs from EGGS.py in CONFIG/
eggs = EGGS.EGGS

class EierSuche(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # "How many eggs did you find?"
        self.add_item(InputText(label="Wie viele Eier hast du gefunden?", placeholder="1"))

    async def callback(self, interaction: discord.Interaction):
        # Check if Input is an Integer, end task if not
        try:
            guess = int(self.children[0].value)
        except:
            # "Your input must be a whole number. 🐰"
            await interaction.response.send_message("Deine Eingabe muss eine ganze Zahl sein. Probier es erneut. 🐰", ephemeral=True)
            return

        # anti-matter?
        if guess < 0:
            guess = 0

        # use local JSON Database
        with open("guesses.json", 'r') as f:
            data = json.load(f)

        # if user in database, end
        if str(interaction.user.id) in data.__str__():
            # "You already participated! 🐰"
            await interaction.response.send_message("Du hast bereits teilgenommen! 🐰", ephemeral=True)
            return

        participants = data["participants"]

        data["participant"+str(participants)] = {"id":interaction.user.id, "guess":guess}

        data["participants"] = participants+1
        # write to file
        with open("guesses.json", 'w') as f:
            json.dump(data, f)

        # "Your input"
        embed = discord.Embed(title="Deine Eingabe", color=discord.Color.random())
        # "No. of eggs"
        embed.add_field(name="Anzahl Eier", value=self.children[0].value, inline=False)
        await interaction.response.send_message(embeds=[embed], ephemeral=True)

# Start egghunt [eiersuche]
@discord.commands.permissions.has_role(admin, guild_id=guild)
@bot.slash_command(name="eiersuche", guild_ids=[guild], description="Starte die Eier-Suche.")
async def eiersuche(ctx):
    class EierView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        # "Enter your found number of eggs."
        @discord.ui.button(label="Gib deine Schätzung ab", style=discord.ButtonStyle.primary, emoji="🐇")
        async def button_callback(self, button, interaction):
            # "🐰 Easter-Campaign 🐰"
            modal = EierSuche(title="🐰 Ostern-Aktion 🐰")
            await interaction.response.send_modal(modal)

    view = EierView()
    # "How many eggs did you find?"
    await ctx.send("Wie viele **Eier** hast du gefunden?", view=view)

# Get a winner
@discord.commands.permissions.has_role(admin, guild_id=guild, description="Beende die Suche, ermittle einen random Gewinner.")
@bot.slash_command(name="eiergefunden", guild_ids=[guild])
async def eiersuche(ctx):
    # load local JSON database :: all participants
    with open("guesses.json", 'r') as f:
        data = json.load(f)
    
    # helping variables
    l = []
    i = 0

    # while loop to go through json
    while(True):
        try:
            if(data["participant"+str(i)]["guess"] == n):
                l.append(data["participant"+str(i)]["id"])
            i = i+1
        # exception -> end of json
        except:
            # get winner
            winner = random.randint(0, len(l)-1)
            winningmember = ctx.guild.get_member(l[winner])

            await ctx.respond("Gewinenr gefunden", ephemeral=True)
            await ctx.channel.send(f"Gewonnen hat {winningmember.mention}")


# Load token from TOKEN.py in folder SECRET/
bot.run(TOKEN.TOKEN)
