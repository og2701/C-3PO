import discord
from discord import File, ui, ButtonStyle
from os import remove as delete_file
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib.utils import merge

class LightsaberButton(ui.Button):
    def __init__(self, part, label, style):
        super().__init__(label=label, custom_id=f'lightsaber_{part}', style=style)
        self.part = part

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("This is not your lightsaber configuration.", ephemeral=True)
            return

        self.view.choices[self.part - 1] = (self.view.choices[self.part - 1] % 6) + 1
        merge(self.view.choices, interaction.user.id)

        with open(f"resources/{interaction.user.id}.png", "rb") as f:
            file = discord.File(fp=f, filename="lightsaber.png")
            await interaction.response.edit_message(content=f'Your choices: {self.view.choices}', view=self.view, attachments=[file])
        delete_file(f"resources/{interaction.user.id}.png")

class LightsaberView(ui.View):
    def __init__(self, user_id):
        super().__init__()
        self.choices = [1, 1, 1, 1]
        self.user_id = user_id
        part_labels = ["Emitter", "Switch", "Sleeve", "Hilt"]
        for i, label in enumerate(part_labels, start=1):
            self.add_item(LightsaberButton(i, label, ButtonStyle.blurple))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        self.stop()

async def lightsaber(interaction: discord.Interaction):
    view = LightsaberView(interaction.user.id)
    merge(view.choices, interaction.user.id)
    
    with open(f"resources/{interaction.user.id}.png", "rb") as f:
        file = discord.File(fp=f, filename="lightsaber.png")
        await interaction.response.send_message('Select your lightsaber parts:', file=file, view=view)
    delete_file(f"resources/{interaction.user.id}.png")

    await view.wait()

    if not view.is_finished():
        await interaction.followup.send('The lightsaber configuration timed out.', ephemeral=True)
