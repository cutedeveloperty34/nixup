# MIT License

# Copyright (c) 2022 Rahul Thakor

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

from Uploader.script import Translation
from pyrogram import Client, filters
from Uploader.functions.database import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_message(filters.command("settings") & filters.private, )
async def settings_func(_, msg):
    sent_msg = await msg.reply_text("**Getting all settings...**", quote=True)
    user = dbcol.find_one({'_id': msg.chat.id})
    if not user:
        insert(msg.chat.id, msg.from_user.first_name)

    BUTON = getSettings(msg.from_user.id)
    await sent_msg.edit_text("**⚙️ Here you can change bot settings**", reply_markup=BUTON, disable_web_page_preview=True)




@Client.on_message(filters.command("caption") & filters.private)
async def see_caption_cmd(_, msg):
    USER = msg.from_user.id
    CAPTION = find_any(USER, "CAPTION")

    if CAPTION:
        try:
            await msg.reply_text(CAPTION, disable_web_page_preview=True)

        except:
            pass
    else:
        await msg.reply_text(text="You haven't set any caption 😅.")


@Client.on_message(filters.private & filters.command('set_caption'))
async def add_footer(_, msg):
    user = msg.from_user.id
    if len(msg.command) == 1:
        return await msg.reply_text(Translation.CAPTION_TEXT)
    CAPTION = msg.text.split(" ", 1)[1]
    addDATA(user, 'CAPTION', CAPTION)
    await msg.reply_text("**Custom caption is saved!**")


@Client.on_message(filters.private & filters.command('del_caption'))
async def delete_caption(_, msg):
    user = msg.from_user.id
    CAPTION = find_any(user, "CAPTION")
    if not CAPTION:
        await msg.reply_text("You haven't set any caption 😅.")
        return
    delDATA(user, 'CAPTION')
    await msg.reply_text("**Custom caption is deleted successfully**")


def getSettings(USER):
    ALL_SETTINGS = ["PHOTO_THUMB", "CAPTION", "SP_EFFECT", "AS_DOC", "NOTIFY"]
    seting_name = {"NOTIFY": "🤖 Receive bot update:",
                   "AS_DOC": "📤 Upload as Document:", "SP_EFFECT": "🎆 Spoiler effect:", "PHOTO_THUMB": "🏞 See custom thumbnail", "CAPTION": "📝 Set custom caption"}
    BUTTONS = []

    for setting in ALL_SETTINGS:
        res = find_any(USER, setting)

        button_text = f"{seting_name[setting]} {'ON' if res == 'ON' else 'OFF'}"
        cb_data = f"toggle_{setting.lower()}"
        if "PHOTO_THUMB" in setting:
            if res:
                button_text = "🏞 See custom thumbnail"
                cb_data = "see_thumb"
            else:
                button_text = "🏞 Set custom thumbnail"
                cb_data = "set_thumb"

        if "CAPTION" in setting:
            if res:
                button_text = "📝 See custom caption"
                cb_data = "see_cap"
            else:
                button_text = "📝 Set custom caption"
                cb_data = "set_cap"

        button = InlineKeyboardButton(button_text, callback_data=cb_data)
        BUTTONS.append([button])

    return InlineKeyboardMarkup(BUTTONS)
