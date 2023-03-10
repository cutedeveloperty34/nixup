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


import os
import asyncio
from Uploader.bypasser import *
from pyrogram.types import Message
from pyrogram import Client, filters
from Uploader.script import Translation
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


video_formats = [
    "MP4", "MOV", "WMV", "AVI", "AVCHD", "FLV", "F4V", "SWF", "MKV"
]
audio_formats = ["MP3", "WAV", "AIFF", "FLAC", "AAC", "WMA", "OGG", "M4A"]


@Client.on_message(filters.media & filters.private & ~filters.photo & ~filters.video)
async def file_to_vid_qry(_, m: Message):
    media_msg = m.audio or m.document or m.animation

    real_filename = media_msg.file_name

    filesize = media_msg.file_size
    filesize = (filesize / (1024 * 1024))
    filesize = str(round(filesize, 2))

    extension = os.path.splitext(real_filename)[1]
    if extension == '':
        real_filename += '.zip'
    extension = extension.replace('.', '')

    if extension.upper() not in video_formats:
        return await m.reply_text(
            Translation.DOC_TEXT.format(
                real_filename, filesize, m.from_user.dc_id),
            reply_markup=Translation.BTN_FOR_OTHER,
            disable_web_page_preview=True,
            quote=True
        )

    return await m.reply_text(
        Translation.DOC_TEXT.format(
            m.document.file_name, filesize, m.from_user.dc_id),
        reply_markup=Translation.BTN_FOR_DOC_VID,
        disable_web_page_preview=True,
        quote=True
    )


@Client.on_message(filters.video & filters.private, )
async def vid_to_file_qry(_, m: Message):
    filesize = m.video.file_size
    filesize = (filesize / (1024 * 1024))
    filesize = str(round(filesize, 2))
    return await m.reply_text(
        Translation.DOC_TEXT.format(
            m.video.file_name, filesize, m.from_user.dc_id),
        reply_markup=Translation.BTN_FOR_VID,
        disable_web_page_preview=True,
        quote=True
    )


@Client.on_message(filters.regex(pattern="http.*") & filters.private)
async def link_echo(_, update):
    sentmsg = await update.reply_text("Processing...⏳", quote=True)
    if "youtu.be" in update.text:
        return await sentmsg.edit_text("**No Youtube Links Supported**")

    if "youtube.com" in update.text:
        return await sentmsg.edit_text("**No Youtube Links Supported**")

    link = update.text
    res = url_exists(link)
  
    if res == False:
      return await sentmsg.edit_text(
            "This link is not accessible or not direct download link",
            disable_web_page_preview=True)
    
    try:
      url = await final_url(link)
    except:
      return await sentmsg.edit_text(
            "This link is not accessible or not direct download link",
            disable_web_page_preview=True)
      
    await asyncio.sleep(0.2)

    file_name, file_size = await get_details(url)
    
    if file_size < 1:
        return await sentmsg.edit_text(
            "This link is not accessible or not direct download link",
            disable_web_page_preview=True)

    DOWN_BUTTONS = InlineKeyboardMarkup([[InlineKeyboardButton('📄 Default', callback_data='default_cb'),
                                          InlineKeyboardButton(
                                              '✏️ Rename', callback_data='rename_cb')
                                          ]])

    return await sentmsg.edit_text(Translation.GET_DETAILS.format(file_name, file_size), reply_markup=DOWN_BUTTONS, disable_web_page_preview=True)
