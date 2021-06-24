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
        text = "--**🗃️ File Details:**--\n\n\n"
        text += f"📂 __File Name:__ `{media.file_name}`\n\n" if media.file_name else ""
        text += f"💽 __Mime Type:__ `{media.mime_type}`\n\n" if media.mime_type else ""
        text += f"📊 __File Size:__ `{humanbytes(media.file_size)}`\n\n" if media.file_size else ""
        if not m.document:
            text += f"🎞 __Duration:__ `{TimeFormatter(media.duration * 1000)}`\n\n" if media.duration else ""
            if m.audio:
                text += f"🎵 __Title:__ `{media.title}`\n\n" if media.title else ""
                text += f"🎙 __Performer:__ `{media.performer}`\n\n" if media.performer else ""
    text += f"__✏ Caption:__ `{m.caption}`\n\n" if m.caption else ""
    text += "**--Uploader Details:--**\n\n\n"
    text += f"__🦚 First Name:__ `{m.from_user.first_name}`\n\n"
    text += f"__🐧 Last Name:__ `{m.from_user.last_name}`\n\n" if m.from_user.last_name else ""
    text += f"__👁 User Name:__ @{m.from_user.username}\n\n" if m.from_user.username else ""
    text += f"__👤 User Id:__ `{m.from_user.id}`\n\n"
    text += f"__💬 DC ID:__ {m.from_user.dc_id}\n\n" if m.from_user.dc_id else ""

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('--', ''))
    share_url = f"tg://share?url={txt}File%20Link%20👉%20{url}"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="Open Url 🔗", url=url),
        InlineKeyboardButton(text="Share Link 👤", url=share_url)
        ],[
        InlineKeyboardButton(text="Delete 🗑", callback_data=f"delete+{msg.message_id}")
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
        text = "**🗃️ File Details:**\n\n\n"
        text += f"📂 __File Name:__ `{media.file_name}`\n\n" if media.file_name else ""
        text += f"💽 __Mime Type:__ `{media.mime_type}`\n\n" if media.mime_type else ""
        text += f"📊 __File Size:__ `{humanbytes(media.file_size)}`\n\n" if media.file_size else ""
        if not m.document:
            text += f"🎞 __Duration:__ `{TimeFormatter(media.duration * 1000)}`\n\n" if media.duration else ""
            if m.audio:
                text += f"🎵 __Title:__ `{media.title}`\n\n" if media.title else ""
                text += f"🎙 __Performer:__ `{media.performer}`\n\n" if media.performer else ""
    text += f"__✏ Caption:__ `{m.caption}`\n\n"
    text += "**Uploader Details:**\n\n\n"
    text += f"__📢 Channel Name:__ `{m.chat.title}`\n\n"
    text += f"__🗣 User Name:__ @{m.chat.username}\n\n" if m.chat.username else ""
    text += f"__👤 Channel Id:__ `{m.chat.id}`\n\n"
    text += f"__💬 DC ID:__ {m.chat.dc_id}\n\n" if m.chat.dc_id else ""
    text += f"__👁 Members Count:__ {m.chat.members_count}\n\n" if m.chat.members_count else ""

    # if databacase channel exist forwarding message to channel
    if DB_CHANNEL_ID:
        msg = await m.copy(int(DB_CHANNEL_ID))
        await msg.reply(text)

    # creating urls
    bot = await c.get_me()
    base64_string = await encode_string(f"{m.chat.id}_{msg.message_id}")
    url = f"https://t.me/{bot.username}?start={base64_string}"
    txt = urllib.parse.quote(text.replace('--', ''))
    share_url = f"tg://share?url={txt}File%20Link%20👉%20{url}"

    # making buttons
    buttons = [[
        InlineKeyboardButton(text="Open Url 🔗", url=url),
        InlineKeyboardButton(text="Share Link 👤", url=share_url)
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
