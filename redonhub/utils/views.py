"""
    File: /bot/utils/confirmView.py
    Usage: A view for confirming items
"""

from typing import Union
from discord import ui, Interaction, ButtonStyle, Message, User, Member


class ConfirmView(ui.View):
    def __init__(self, user: Union[User, Member], *, timeout: float = 60.0):
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


class JumpToMessageView(ui.View):
    def __init__(self, message: Message, *, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.add_item(
            ui.Button(
                label="Jump to Message", style=ButtonStyle.link, url=message.jump_url
            )
        )
