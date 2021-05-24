import os
import logging
import logging.config

# Get logging configurations
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import ListenerCanceled
DB_CHANNEL_ID = os.environ.get("DB_CHANNEL_ID")
OWNER_ID = os.environ.get("OWNER_ID")
BATCH = []


@Client.on_message(filters.command('start') & filters.incoming & filters.private)
async def start(c, m, cb=False):
    owner = await c.get_users(int(OWNER_ID))
    owner_username = owner.username if owner.username else 'Ns_bot_updates'

    # start text
    text = f"""Hey! {m.from_user.mention(style='md')}

💡 ** I am Telegram File Store Bot**

`You can store your Telegram Media for permanent Link!`


**👲 Maintained By:** {owner.mention(style='md')}
"""

    # Buttons
    buttons = [
        [
            InlineKeyboardButton('My Father 👨‍✈️', url=f"https://t.me/{owner_username}"),
            InlineKeyboardButton('Help 💡', callback_data="help")
        ],
        [
            InlineKeyboardButton('About 📕', callback_data="about")
        ]
    ]

    # when button home is pressed
    if cb:
        return await m.message.edit(
                   text=text,
                   reply_markup=InlineKeyboardMarkup(buttons)
               )

    if len(m.command) > 1: # sending the stored file
        chat_id, msg_id = m.command[1].split('_')
        msg = await c.get_messages(int(chat_id), int(msg_id)) if not DB_CHANNEL_ID else await c.get_messages(int(DB_CHANNEL_ID), int(msg_id))

        if msg.empty:
            owner = await c.get_users(int(OWNER_ID))
            return await m.reply_text(f"🥴 Sorry bro your file was missing\n\nPlease contact my owner 👉 {owner.mention(style='md')}")
        
        caption = f"{msg.caption.markdown}\n\n\n" if msg.caption else ""

        if chat_id.startswith('-100'): #if file from channel
            channel = await c.get_chat(int(chat_id))
            caption += "**--Uploader Details:--**\n\n"
            caption += f"__📢 Channel Name:__ `{channel.title}`\n\n"
            caption += f"__🗣 User Name:__ @{channel.username}\n\n" if channel.username else ""
            caption += f"__👤 Channel Id:__ `{channel.id}`\n\n"
            caption += f"__💬 DC ID:__ {channel.dc_id}\n\n" if channel.dc_id else ""
            caption += f"__👁 Members Count:__ {channel.members_count}\n\n" if channel.members_count else ""

        else: #if file not from channel
            user = await c.get_users(int(chat_id))
            caption += "**--Uploader Details:--**\n\n"
            caption += f"__🦚 First Name:__ `{user.first_name}`\n\n"
            caption += f"__🐧 Last Name:__ `{user.last_name}`\n\n" if user.last_name else ""
            caption += f"__👁 User Name:__ @{user.username}\n\n" if user.username else ""
            caption += f"__👤 User Id:__ `{user.id}`\n\n"
            caption += f"__💬 DC ID:__ {user.dc_id}\n\n" if user.dc_id else ""

        await msg.copy(m.from_user.id, caption=caption)


    else: # sending start message
        await m.reply_text(
            text=text,
            quote=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@Client.on_message(filters.command('me') & filters.incoming & filters.private)
async def me(c, m):
    """ This will be sent when /me command was used"""

    me = await c.get_users(m.from_user.id)
    text = "--**YOUR DETAILS:**--\n\n\n"
    text += f"__🦚 First Name:__ `{me.first_name}`\n\n"
    text += f"__🐧 Last Name:__ `{me.last_name}`\n\n" if me.last_name else ""
    text += f"__👁 User Name:__ @{me.username}\n\n" if me.username else ""
    text += f"__👤 User Id:__ `{me.id}`\n\n"
    text += f"__💬 DC ID:__ {me.dc_id}\n\n" if me.dc_id else ""
    text += f"__✔ Is Verified By TELEGRAM:__ `{me.is_verified}`\n\n" if me.is_verified else ""
    text += f"__👺 Is Fake:__ {me.is_fake}\n\n" if me.is_fake else ""
    text += f"__💨 Is Scam:__ {me.is_scam}\n\n" if me.is_scam else ""
    text += f"__📃 Language Code:__ {me.language_code}\n\n" if me.language_code else ""

    await m.reply_text(text, quote=True)


@Client.on_message(filters.command('batch') & filters.private & filters.incoming)
async def batch(c, m):
    """ This is for batch command"""

    BATCH.append(m.from_user.id)
    files = []
    i = 1

    while m.from_user.id in BATCH:
        if i == 1:
            media = await c.ask(chat_id=m.from_user.id, text='Send me some files or videos or photos or text or audio.')
            files.append(media)
        elif i <= 10 and i != 1:
            try:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Done ✅', callback_data='done')]])
                media = await c.ask(chat_id=m.from_user.id, text='Ok 😉. Now send me some more files Or press done to get shareable link.', reply_markup=reply_markup)
                files.append(media)
            except ListenerCanceled:
                pass
            except Exception as e:
                print(e)
                await m.reply_text(text="Something went wrong. Try again later.")
        else:
            break
        i += 1

    string = ""
    for file in files:
        if DB_CHANNEL_ID:
            copy_message = await file.copy(int(DB_CHANNEL_ID))
        else:
            copy_message = await file.copy(m.from_user.id)
        string += f"{copy_message.message_id}&"

    bot = await c.get_me()
    url = f"https://t.me/{bot.username}?start=batch_{m.chat.id}_{string}" if not DB_CHANNEL_ID else f"https://t.me/{bot.username}?start=batch_{m.chat.id}_{string}"

    await m.reply_text(text=url)
