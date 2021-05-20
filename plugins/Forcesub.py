from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
OWNER_ID = os.environ.get('OWNER_ID')
UPDATE_CHANNEL = os.environ.get('UPDATE_CHANNEL', '')


@Client.on_message(filters.private & filters.incoming)
async def forcesub(c, m):
    owner = await c.get_users(int(OWNER_ID))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, )
            if user.status == "kicked":
               await m.reply_text("**Hey you are banned 😜**", quote=True)
               return
        except UserNotParticipant:
            buttons = [[InlineKeyboardButton(text='Updates Channel 🔖', url=f"https://t.me/{UPDATE_CHANNEL}")]]
            if m.text:
                if (len(m.command) > 1) & (m.command[0] == 'start'):
                    chat_id, msg_id = m.command[1].split('_')
                    buttons.append([InlineKeyboardButton('🔄 Refresh', callback_data=f'refresh+{chat_id}+{msg_id}')])
            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
                "__Press the Following Button to join Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}", quote=True)
            return
    await m.continue_propagation()
