import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant
from config import Config

FORCE_SUB_CHANNELS = Config.FORCE_SUB_CHANNELS


async def not_subscribed(_, __, message):
    for channel in FORCE_SUB_CHANNELS:
        try:
            user = await message._client.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                return True
        except UserNotParticipant:
            return True
    return False


@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    not_joined_channels = []
    for channel in FORCE_SUB_CHANNELS:
        try:
            user = await client.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"📢 Rejoindre {channel.capitalize()} 📢", url=f"https://t.me/{channel}"
            )
        ]
        for channel in not_joined_channels
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="✅ J'ai rejoint ✅", callback_data="check_subscription"
            )
        ]
    )

    text = "**Désolé, vous n'êtes pas abonné à tous les canaux requis 😐. Veuillez rejoindre les canaux de mise à jour pour continuer**"
    await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    not_joined_channels = []

    for channel in FORCE_SUB_CHANNELS:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)

    if not not_joined_channels:
        await callback_query.message.edit_text(
            "**Vous avez rejoint tous les canaux requis. Merci ! 😊 /start maintenant**"
        )
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"📢 Rejoindre {channel.capitalize()} 📢",
                    url=f"https://t.me/{channel}",
                )
            ]
            for channel in not_joined_channels
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    text="✅ J'ai rejoint", callback_data="check_subscription"
                )
            ]
        )

        text = "**Vous n'avez pas rejoint tous les canaux requis. Veuillez les rejoindre pour continuer.**"
        await callback_query.message.edit_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons)
        )
