# MIT License

# Copyright (c) 2022 Hash Minner

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
import json
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from Uploader.functions.settings import getSettings
from Uploader.config import SUDO_USERS, TOTAL_TASKS
from Uploader.script import Translation, check_time
from Uploader.bypasser import get_details, final_url
from Uploader.rename.conv2file import convert_to_file
from Uploader.rename.conv2vid import convert_to_video
from Uploader.rename.thum_cb import change_thumb_func
from Uploader.functions.database import find_any, addDATA
from Uploader.dl_button import ddl_call_back  #download_file


@Client.on_callback_query(filters.regex(r'^conv_to_doc$'))
async def conv_to_doc_cb(client, cb):
  await cb.message.delete()
  await convert_to_file(client, cb)


@Client.on_callback_query(filters.regex(r'^conv_to_vid$'))
async def conv_to_vid_cb(client, cb):
  await cb.message.delete()
  await convert_to_video(client, cb)


@Client.on_callback_query(filters.regex(r'^change_thumb$'))
async def change_thumb_cb(client, cb):
  THUMB = find_any(cb.from_user.id, "PHOTO_THUMB")
  if not THUMB:
    return await cb.answer("Please /set_thumbnail before using this function.",
                           show_alert=True)
  await cb.message.delete()
  await change_thumb_func(client, cb)


@Client.on_callback_query(filters.regex(r"^set_thumb$"))
async def set_caption_cb(_, query):
  # USER = query.from_user.id
  text = "Send image or reply /set_thumb to any image to set it as a custom thumbnail"

  try:
    await query.answer(text, show_alert=True)
  except:
    pass


@Client.on_callback_query(filters.regex(r"^set_cap$"))
async def set_thumb_cb(_, query):

  text = "Send /set_caption to know more how to set a custom caption"
  try:
    await query.answer(text, show_alert=True)
  except:
    pass


@Client.on_callback_query(filters.regex(r"^see_cap$"))
async def see_caption_cb(_, query):
  USER = query.from_user.id
  CAPTION = find_any(USER, "CAPTION")
  await query.message.delete()

  if CAPTION:
    try:
      ms = await query.message.reply_text(CAPTION,
                                          disable_web_page_preview=True)
      await query.message.reply_text("**This is your custom caption**",
                                     reply_to_message_id=ms.id,
                                     disable_web_page_preview=True)

    except:
      pass
  else:
    await query.message.reply_text(text="You haven't set any caption 😅.")


@Client.on_callback_query(filters.regex(r"^see_thumb$"))
async def see_thumb_cb(_, query):
  USER = query.from_user.id
  THUMB = find_any(USER, "PHOTO_THUMB")

  if THUMB:
    try:
      await query.message.reply_photo(photo=THUMB,
                                      caption="👆 Custom thumbnail")
    except:
      pass
  else:
    await query.message.reply_text(text="You haven't set any thumbnail 😅.")


@Client.on_callback_query(filters.regex(r"^toggle_as_doc$"))
async def doc_cb(_, query):
  USER = query.from_user.id

  res = find_any(USER, "AS_DOC")
  if res == "OFF":
    addDATA(USER, "AS_DOC", "ON")
  if res == "ON":
    addDATA(USER, "AS_DOC", "OFF")

  BUTTONS = getSettings(USER)
  try:
    await query.message.edit_text(Translation.SETTING_TXT,
                                  reply_markup=BUTTONS)
  except:
    pass


@Client.on_callback_query(filters.regex(r"^toggle_notify$"))
async def notify_cb(_, query):
  USER = query.from_user.id

  res = find_any(USER, "NOTIFY")
  if res == "OFF":
    addDATA(USER, "NOTIFY", "ON")
  if res == "ON":
    addDATA(USER, "NOTIFY", "OFF")

  BUTTONS = getSettings(USER)
  try:
    await query.message.edit_text(Translation.SETTING_TXT,
                                  reply_markup=BUTTONS)
  except:
    pass


@Client.on_callback_query(filters.regex(r"^toggle_sp_effect$"))
async def spoiler_cb(_, query):
  USER = query.from_user.id

  res = find_any(USER, "SP_EFFECT")
  if res == "OFF":
    addDATA(USER, "SP_EFFECT", "ON")

  if res == "ON":
    addDATA(USER, "SP_EFFECT", "OFF")

  BUTTONS = getSettings(USER)
  try:
    await query.message.edit_text(Translation.SETTING_TXT,
                                  reply_markup=BUTTONS)
  except:
    pass


# Handle the callback query for the "Cancel" button
@Client.on_callback_query(filters.regex(r'^cancel_upload$'))
async def handle_callback_query(client, callback_query):

  status = callback_query.data.split("#")[1]
  if os.path.isfile(status):
    with open(status, 'r+') as f:
      statusMsg = json.load(f)
      statusMsg['running'] = False
      f.seek(0)
      json.dump(statusMsg, f, indent=2)
      if 'pid' in statusMsg.keys():
        try:
          os.kill(statusMsg["pid"], 9)

        except:
          pass

        delete_downloads(status)
      try:
        await client.delete_messages(callback_query.message.chat.id,
                                     statusMsg["message"])
        await callback_query.message.reply_text("Cancelled")
      except:
        pass

  else:
    pass


@Client.on_callback_query(filters.regex(r'^home$'))
async def home_cb(bot, update):
  await update.message.edit(text=Translation.START_TEXT.format(
    update.from_user.mention),
                            reply_markup=Translation.START_BUTTONS,
                            disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r'^help$'))
async def help_cb(bot, update):
  await update.message.edit(text=Translation.HELP_TEXT,
                            reply_markup=Translation.HELP_BUTTONS,
                            disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r'^about$'))
async def about_cb(bot, update):
  await update.message.edit(text=Translation.ABOUT_TEXT,
                            reply_markup=Translation.ABOUT_BUTTONS,
                            disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r'^close$'))
async def close_cb(bot, update):
  await update.message.delete(True)


@Client.on_callback_query(filters.regex(r'^rename_cb$'))
async def rename_cb(bot, update):
  res = await check_time(str(update.message.date))
  if res == False:
    return await update.answer(
      "You are replying to too old message, Please send me that message again.",
      show_alert=True)

  USER = update.from_user.id
  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.answer(
        "Please don't send new task until the previous one has been completed.",
        show_alert=True)

    if len(TOTAL_TASKS) >= 5:
      return await update.answer(
        "I am so busy now so please me your task after sometime.",
        show_alert=True)

  reply_msg = update.message.reply_to_message
  m_id = reply_msg.id
  url = reply_msg.text
  url = await final_url(url)
  file_name, file_size = await get_details(url)
  await update.message.delete()

  TEXT = '''**Title:** `{}`

Send new name for this file'''
  await update.message.reply_text(text=TEXT.format(file_name),
                                  reply_to_message_id=m_id,
                                  reply_markup=ForceReply(
                                    True, placeholder="Enter file name"),
                                  quote=True)


@Client.on_callback_query(filters.regex(r'^rename_file$'))
async def rename_file_cb(bot, update):
  res = await check_time(str(update.message.date))
  if res == False:
    return await update.answer(
      "You are replying to too old message, Please send me that message again.",
      show_alert=True)

  USER = update.from_user.id
  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.answer(
        "Please don't send new task until the previous one has been completed.",
        show_alert=True)
    if len(TOTAL_TASKS) >= 5:
      return await update.answer(
        "I am so busy now so please me your task after sometime.",
        show_alert=True)
  reply_msg = update.message.reply_to_message

  await update.message.delete()
  mediamsg = reply_msg.video or reply_msg.document or reply_msg.audio
  file_name = mediamsg.file_name
  real_file_size = mediamsg.file_size
  filesize = (real_file_size / (1024 * 1024))
  filesize = str(round(filesize, 2))

  TEXT = '''**Title:** `{}`

Send new name to rename this file'''
  await update.message.reply_text(text=TEXT.format(file_name),
                                  reply_to_message_id=reply_msg.id,
                                  reply_markup=ForceReply(
                                    True, placeholder="Enter file name"),
                                  quote=True)


@Client.on_callback_query(filters.regex(r'^default_cb$'))
async def default_cb(bot, update):

  res = await check_time(str(update.message.date))
  if res == False:
    return await update.answer(
      "You are replying to too old message, Please send me that url again.",
      show_alert=True)

  USER = update.from_user.id
  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.answer(
        "Please don't send new task until the previous one has been completed.",
        show_alert=True)

    if len(TOTAL_TASKS) >= 5:
      return await update.answer(
        "I am so busy now so please me your task after sometime.",
        show_alert=True)
  reply_msg = update.message.reply_to_message

  url = reply_msg.text
  url = await final_url(url)
  file_name, file_size = await get_details(url)
  
  await update.message.delete()

  file_x = (file_name.strip('"')).split(".")[-1]

  await ddl_call_back(bot, reply_msg, USER, url,file_name,file_size, file_x)


@Client.on_callback_query(filters.regex('cancel'))
async def cancel_cb(bot, update):
  await handle_callback_query(bot, update)


@Client.on_callback_query()
async def any_cb(bot, update):
  if "server_one" == update.data:
    t = len(TOTAL_TASKS)
    return await update.answer(f"Active tasks: {str(t)}", show_alert=True)
  await update.message.delete()


def delete_downloads(USER):
  os.system(f'rm -rf {USER}')
