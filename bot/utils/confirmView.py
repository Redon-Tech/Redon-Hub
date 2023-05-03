"""
    File: /bot/utils/confirmView.py
    Usage: A view for confirming items
"""
from discord import ui, Interaction, ButtonStyle

class ConfirmView(ui.View):
    def __init__(self, user, *, timeout=60.0):
        self.user = user
        super().__init__(timeout=timeout)
        self.value = None

    @ui.button(label="Confirm", style=ButtonStyle.success)
    async def confirm(self, interaction: Interaction, _):
        self.value = True
        self.stop()

    @ui.button(label="Cancel", style=ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, _):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: Interaction):
        return interaction.user == self.user