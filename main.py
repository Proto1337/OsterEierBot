import discord
import os
import asyncio
import json
from discord.ext import commands
from discord.ui import InputText, Modal
from SECRET import TOKEN
from CONFIG import SERVER

if os.name != "nt":
    print("uvloop wird genutzt")
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvloop.install()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=">")


bot = Bot()
guild = SERVER.GUILD

class MyModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Wie viele Eier hast du gefunden?", placeholder="1"))

    async def callback(self, interaction: discord.Interaction):
        try:
            guess = int(self.children[0].value)
        except:
            await interaction.response.send_message("Deine Eingabe muss eine ganze Zahl sein. Probier es erneut. 🐰", ephemeral=True)
            return

        with open("guesses.json", 'r') as f:
            data = json.load(f)

        if str(interaction.user.id) in data.__str__():
            await interaction.response.send_message("Du hast bereits teilgenommen! 🐰", ephemeral=True)
            return

        teilnehmeranzahl = data["teilnehmeranzahl"]

        data["teilnehmer"+str(teilnehmeranzahl)] = {"id":interaction.user.id, "guess":guess}

        data["teilnehmeranzahl"] = teilnehmeranzahl+1
        with open("guesses.json", 'w') as f:
            json.dump(data, f)

        embed = discord.Embed(title="Deine Eingabe", color=discord.Color.random())
        embed.add_field(name="Anzahl Eier", value=self.children[0].value, inline=False)
        await interaction.response.send_message(embeds=[embed], ephemeral=True)


@bot.slash_command(name="modaltest", guild_ids=[guild])
async def modal_slash(ctx):
    class MyView(discord.ui.View):
        @discord.ui.button(label="Gib deine Schätzung ab", style=discord.ButtonStyle.primary, emoji="🐇")
        async def button_callback(self, button, interaction):
            modal = MyModal(title="🐰 Ostern-Aktion 🐰")
            await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.send("Wie viele **Eier** hast du gefunden?", view=view)


bot.run(TOKEN.TOKEN)
