"""club elec’s Discord server account verification"""

import os
import discord
from discord import app_commands
from discord.ext import commands
import random
import smtplib
from email.mime.text import MIMEText
import datetime
import re

import sqlite3
import traceback

bot_token: str = os.getenv("BOT_TOKEN", "")
public_channel: int = int(os.getenv("PUBLIC_CHANNEL", ""))
database_path: str = os.getenv("DATABASE_PATH", "./database.db")


conn: sqlite3.Connection = sqlite3.connect(database_path)
c: sqlite3.Cursor = conn.cursor()

c.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, timestamp TIMESTAMP)"
)
conn.commit()


def generate_code() -> str:
    return str(random.randint(000000, 999999))


def send_email(email: str, code: str) -> None:
    msg = MIMEText(
        f"Votre code de vérification pour valider votre compte Discord sur le serveur Discord du club elec est {code}."
    )
    msg["Subject"] = "Code de vérification pour le serveur Discord du club elec"
    msg["From"] = "no-reply@discord.clubelec.org"
    msg["To"] = email

    with smtplib.SMTP("localhost") as smtp:
        smtp.send_message(msg)


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def setup_hook(self) -> None:
        await self.tree.sync()


class EmailModal(discord.ui.Modal, title="Vérification de votre compte"):
    email = discord.ui.TextInput(
        label="Adresse de courriel",
        placeholder="ane.onyme@(etud.)u-picardie.fr",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.email.value.endswith("@u-picardie.fr") or self.email.value.endswith(
            "@etud.u-picardie.fr"
        ):
            email_already_registered = c.execute(
                "SELECT EXISTS(SELECT 1 FROM users WHERE email = :email)",
                {"email": self.email.value},
            ).fetchone()[0]
            if email_already_registered:
                await interaction.response.edit_message(
                    content="L’adresse de courriel que vous avez entrée a déjà été utilisée pour valider un compte.\nSi vous avez changé de compte et souhaitez valider un autre compte, veuillez contacter un administrateur de ce serveur Discord.",
                    view=None,
                )
            else:
                code = generate_code()
                send_email(self.email.value, code)
                await interaction.response.edit_message(
                    content="Veuillez vérifier votre boîte de courriels UPJV, un message contenant un code de vérification vous a été envoyé.\nUne fois en possession de ce code, veuillez cliquer sur le bouton ci-dessous",
                    view=CodeSentView(self.email.value, code),
                )
        else:
            await interaction.response.edit_message(
                content="L’adresse de courriel que vous avez entrée ne correspond pas à une adresse UPJV en `@u-picardie.fr` ou en `@etud.u-picardie.fr`.",
                view=None,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.edit_message(
            content="Oups... :sob:\nUne erreur est survenue.", view=None
        )
        traceback.print_exception(type(error), error, error.__traceback__)


class CodeModal(discord.ui.Modal, title="Entrez votre code de vérification"):
    def __init__(self, email: str, code: str) -> None:
        super().__init__()
        self.email = email
        self.code = code

    typed_code = discord.ui.TextInput(
        label="Code reçu par courriel", placeholder="000000", required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        if self.typed_code.value == self.code:
            c.execute(
                "INSERT INTO users (id, email, timestamp) VALUES (?, ?, ?)",
                (interaction.user.id, self.email, datetime.datetime.now()),
            )
            conn.commit()
            role = discord.utils.get(interaction.guild.roles, name="Vérifiés")
            await interaction.user.add_roles(role)
            await interaction.response.edit_message(
                content="Bravo !\nVous avez validé votre compte avec succès. :partying_face: :partying_face: :partying_face:\nLe rôle `Vérifié`, vous permettant d’accéder à l’ensemble des fonctionnalités de ce serveur Discord, vous a été ajouté.\n",
                view=None,
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.edit_message(
            content="Oups... :sob:\nUne erreur est survenue.",
            view=None,
        )
        traceback.print_exception(type(error), error, error.__traceback__)


class CodeSentView(discord.ui.View):
    def __init__(self, email: str, code: str) -> None:
        super().__init__()
        self.email = email
        self.code = code

    @discord.ui.button(
        label="Entrer mon code de vérification", style=discord.ButtonStyle.green
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(CodeModal(self.email, self.code))


class EmailModalView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()

    @discord.ui.button(
        label="Entrer mon adresse de courriel universitaire",
        style=discord.ButtonStyle.green,
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(EmailModal())


client = MyClient()


@client.tree.command(name="verify", description="Vérification de votre compte")
async def verify(interaction: discord.Interaction) -> None:
    is_verified = c.execute(
        "SELECT EXISTS(SELECT 1 FROM users WHERE id = :id)", {"id": interaction.user.id}
    ).fetchone()[0]
    if is_verified:
        await interaction.response.send_message(
            "Votre compte est déjà vérifié.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "En vérifiant votre compte Discord à l’aide de votre adresse de courriel universitaire, vous pourrez débloquer votre accès à l’ensemble des fonctionnalités de ce serveur Discord.\nCliquez sur le bouton ci-dessous pour commencer.",
            view=EmailModalView(),
            ephemeral=True,
        )


@client.tree.command(name="whois", description="Qui est cette personne ?")
@app_commands.checks.has_permissions(manage_messages=True)
async def whois(interaction: discord.Interaction, message: str) -> None:
    matches = re.findall(r"<@!?([0-9]{15,20})>", message)
    if matches:
        match = matches[0]
        get_email = c.execute("SELECT email FROM users WHERE id = :id", {"id": match})
        email = get_email.fetchone()
        if email:
            username = email[0].split("@").replace(".", " ")
            await interaction.response.send_message(
                f"{interaction.guild.get_member(int(match))} a pour adresse de courriel : {username}",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"{interaction.guild.get_member(int(match))} n’a pas vérifié son compte, il est donc impossible de trouver son adresse de courriel.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            "Hum... Il semble qu’il y a un souci avec votre demande...\nVeuillez vérifier si vous avez correctement mentionné un utilisateur.",
            ephemeral=True,
        )


@whois.error
async def whois_error(interaction: discord.Interaction, error) -> None:
    await interaction.response.send_message(
        f"Une erreur est survenue : {error}", ephemeral=True
    )


@client.tree.command(
    name="unverify", description="Suppression de la vérification d’un compte"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def unverify(interaction: discord.Interaction, id: str) -> None:
    matches = re.findall(r"<@!?([0-9]{15,20})>", id)
    if matches:
        match = matches[0]
        get_user = c.execute("SELECT email FROM users WHERE id = :id", {"id": match})
        user = get_user.fetchone()
        if user:
            delete_user = c.execute("DELETE FROM users WHERE id = :id", {"id": match})
            conn.commit()
            role = discord.utils.get(interaction.guild.roles, name="Vérifiés")
            member = interaction.guild.get_member(int(match))
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"La vérification du compte de {interaction.guild.get_member(int(match))} a été supprimé avec succès.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"{interaction.guild.get_member(int(match))} n’a pas vérifié son compte, il est donc impossible de supprimer sa vérification.",
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            "Hum... Il semble qu’il y a un souci avec votre demande...\nVeuillez vérifier si vous avez correctement mentionné un utilisateur.",
            ephemeral=True,
        )


@unverify.error
async def unverify_error(interaction: discord.Interaction, error) -> None:
    await interaction.response.send_message(
        f"Une erreur est survenue : {error}", ephemeral=True
    )


@client.event
async def on_member_remove(member) -> None:
    get_user = c.execute("SELECT email FROM users WHERE id = :id", {"id": member.id})
    user = get_user.fetchone()
    if user:
        delete_user = c.execute("DELETE FROM users WHERE id = :id", {"id": member.id})
        conn.commit()


@client.event
async def on_member_join(member) -> None:
    channel = client.get_channel(public_channel)
    await channel.send(
        f"Coucou {member.mention}, je suis club elec security, le bot de vérification de comptes Discord missionné par ce serveur.\nSi vous êtes étudiant·e ou personnel, vous pouvez cliquer sur le bouton ci-dessous pour valider votre compte avec votre courriel universitaire. Vous pouvez aussi taper la commande `/verify`. Laissez-vous guider, je suis un gentil petit bot !\nSi vous ne faites pas partie de l'UPJV, vous pouvez vous présenter dans ce salon afin que nous puissons valider votre compte manuellement et vous donner les autorisations adéquates.\nMerci et à très vite. :grin:",
        view=EmailModalView(),
    )


client.run(bot_token)
