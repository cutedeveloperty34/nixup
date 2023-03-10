# MIT License

# Copyright (c) 2023 Rahul Thakor

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

from pyrogram import Client, filters
from pyrogram.types import Message
from Uploader.functions.database import *


@Client.on_message(filters.photo & filters.incoming & filters.private)
async def save_photo(_, msg: Message):
    addDATA(msg.chat.id, "PHOTO_THUMB", msg.photo.file_id)
    await msg.reply_text("Custom thumbnail is saved!", quote=True)


@Client.on_message(filters.command(["thumbnail", "thumb"]) & filters.private)
async def see_thumb_cmd(_, msg):
    USER = msg.from_user.id
    PHOTO_THUMB = find_any(USER, "PHOTO_THUMB")

    if PHOTO_THUMB:
        try:
            await msg.reply_photo(PHOTO_THUMB, caption="👆 Custom thumbnail")
        except:
            pass
    else:
        await msg.reply_text(text="You haven't set any thumbnail 😅.")


@Client.on_message(filters.private & filters.command(['delete_thumb', 'del_thumb']))
async def delete_thumb(_, msg):
    user = msg.from_user.id
    PHOTO_THUMB = find_any(user, "PHOTO_THUMB")
    if not PHOTO_THUMB:
        await msg.reply_text("You haven't set any thumbnail 😅.")
        return
    delDATA(user, 'PHOTO_THUMB')
    await msg.reply_text("**Custom thumbnail is deleted successfully**")

thumb_text = """Please send image which you want to set as a custom thumbnail.

No need to use this command every time, just send imamge and I will use it as a thumbnail 😅"""


@Client.on_message(filters.private & filters.command('set_thumbnail'))
async def seta_thumb_cmd(_, msg: Message):
    user = msg.from_user.id
    if not msg.reply_to_message:
        return await msg.reply_text(thumb_text)
    if not msg.reply_to_message.photo:
        return await msg.reply_text(thumb_text)

    image = msg.reply_to_message.photo.file_id
    addDATA(user, 'PHOTO_THUMB', image)
    await msg.reply_text("Custom thumbnail is saved!", quote=True)
