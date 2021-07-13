import os
import urllib
from .commands import encode_string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import *

#################################### FOR PRIVATE ################################################
@Client.on_message((filters.document|filters.video|filters.audio|filters.photo) & filters.incoming & ~filters.edited & ~filters.channel)
async def storefile(c, m):
    if IS_PRIVATE:
        if m.from_user.id not in AUTH_USERS:
            return
    send_message = await m.reply_text("**Processing...**", quote=True)
    media = m.document or m.video or m.audio or m.photo
    # text
    text = ""
    if not m.photo:
        text = "--**️ File Details:**--\n\n"
        text += f"   **File Name:** `{media.file_name}`\n" if media.file_name else ""
        text += f"   **Mime Type:** `{media.mime_type}`\n" if media.mime_type else ""
        text += f"   **File Size:** `{humanbytes(media.file_size)}`\n" if media.file_size else ""
    text += f"   **User Name:** @{m.from_user.username}\n" if m.from_user.username else ""
    text += f"   **User Id:** `{m.from_user.id}`\n"

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('--', ''))
    share_url = f"tg://share?url=File%20Link%20👉%20{url}"
    text += f"\n**COPY LINK: ** `{url}`"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="OPEN URL", url=url),
        InlineKeyboardButton(text="SHARE LINK", url=share_url)
        ],[
        InlineKeyboardButton(text="DELETE", callback_data=f"delete+{msg.message_id}")
    ]]

    # sending message
    await send_message.edit(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
#################################### FOR CHANNEL################################################

@Client.on_message((filters.document|filters.video|filters.audio|filters.photo) & filters.incoming & filters.channel & ~filters.forwarded & ~filters.edited)
async def storefile_channel(c, m):
    if IS_PRIVATE:
        if m.chat.id not in AUTH_USERS:
            return
    media = m.document or m.video or m.audio or m.photo

    # text
    text = ""
    if not m.photo:
        text = "**File Details:**\n\n\n"
        text += f"__ File Name:__ `{media.file_name}`\n" if media.file_name else ""
        text += f"__ Mime Type:__ `{media.mime_type}`\n" if media.mime_type else ""
        text += f"__ File Size:__ `{humanbytes(media.file_size)}`\n" if media.file_size else ""
        if not m.document:
            text += f"__ Duration:__ `{TimeFormatter(media.duration * 1000)}`\n" if media.duration else ""
            if m.audio:
                text += f"__ Title:__ `{media.title}`\n" if media.title else ""
                text += f" __ Performer:__ `{media.performer}`\n" if media.performer else ""
    text += f"__ Caption:__ `{m.caption}`\n\n\n"
    text += "**Uploader Details:**\n\n"
    text += f"__ Channel Name:__ `{m.chat.title}`\n"
    text += f"__ User Name:__ @{m.chat.username}\n" if m.chat.username else ""
    text += f"__ Channel Id:__ `{m.chat.id}`\n"
    text += f"__ DC ID:__ {m.chat.dc_id}\n" if m.chat.dc_id else ""
    text += f"__ Members Count:__ {m.chat.members_count}\n" if m.chat.members_count else ""

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('--', ''))
    share_url = f"tg://share?url=File%20Link%20👉%20{url}"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="OPEN URL", url=url),
        InlineKeyboardButton(text="SHARE LINK", url=share_url)
    ]]

    # Editing and adding the buttons
    await m.edit_reply_markup(InlineKeyboardMarkup(buttons))


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " days, ") if days else "") + \
        ((str(hours) + " hrs, ") if hours else "") + \
        ((str(minutes) + " min, ") if minutes else "") + \
        ((str(seconds) + " sec, ") if seconds else "") + \
        ((str(milliseconds) + " millisec, ") if milliseconds else "")
    return tmp[:-2]
