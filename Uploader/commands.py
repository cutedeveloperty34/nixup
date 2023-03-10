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
import time
import sys
from Uploader.bypasser import *
from pyrogram.types import Message
from pyrogram import Client, filters
from Uploader.functions.database import *
from Uploader.dl_button import ddl_call_back
from Uploader.rename.renamefile import rename_cb
from Uploader.script import Translation, check_time
from Uploader.config import DONT_SEND_TASK, SUDO_USERS, TOTAL_TASKS

video_formats = [
  "MP4", "MOV", "WMV", "AVI", "AVCHD", "FLV", "F4V", "SWF", "MKV"
]
audio_formats = ["MP3", "WAV", "AIFF", "FLAC", "AAC", "WMA", "OGG", "M4A"]


@Client.on_message(
  filters.command("start") & filters.private, )
async def start_bot(_, m: Message):
  return await m.reply_text(
    Translation.START_TEXT.format(m.from_user.mention),
    reply_markup=Translation.START_BUTTONS,
    disable_web_page_preview=True,
    quote=True,
  )


@Client.on_message(
  filters.command("help") & filters.private, )
async def help_bot(_, m: Message):
  return await m.reply_text(
    Translation.HELP_TEXT,
    reply_markup=Translation.HELP_BUTTONS,
    disable_web_page_preview=True,
  )


@Client.on_message(
  filters.command(['user', 'users']) & filters.user(SUDO_USERS))
async def user_cmd(_, M):
  users = total_user()
  await M.reply_text(f"Total Users: {users}")


@Client.on_message(
  filters.command(['broadcast', 'bcast']) & filters.user(SUDO_USERS))
async def broadcast(_, M):
  if not M.reply_to_message_id:
    await M.reply_text("No Message Found")
    return

  ids = getid()
  success = 0
  failed = 0
  total = len(ids)
  msG = await M.reply_text(f"Started Broadcast\n\nTotal users: {str(total)}")
  for id in ids:

    try:
      await M.reply_to_message.copy(id)
      time.sleep(0.33)
      success += 1
    except:
      failed += 1
      delete({"_id": id})
      pass
  await msG.edit_text(
    f"**Total:** {str(total)}\n**Success:** {str(success)}\n**Failed:** {str(failed)}"
  )


@Client.on_message(
  filters.regex("!!exit") & filters.private & filters.user(SUDO_USERS))
async def exit_bot(_, m: Message):
  await m.reply_text("Exited Successfully")
  sys.exit(1)


@Client.on_message(
  filters.command("about") & filters.private, )
async def aboutme(_, m: Message):
  return await m.reply_text(
    Translation.ABOUT_TEXT,
    reply_markup=Translation.ABOUT_BUTTONS,
    disable_web_page_preview=True,
  )


@Client.on_message(filters.command("list") & filters.private)
async def list_tasks(_, m: Message):
  return await m.reply_text(Translation.UPLOAD_LIST,
                            reply_markup=Translation.UPLOAD_LIST_BUTTONS)


@Client.on_message(filters.command("restart") & filters.private)
async def restart_tasks(_, m: Message):
  USER = m.from_user.id
  try:
    TOTAL_TASKS.remove(USER)
  except:
    pass

  return await m.reply_text("Reseted Success")


@Client.on_message(filters.private & filters.reply
                   & ~filters.command(['rename']))
async def reply_2(bot, update):
  reply_msg = update.reply_to_message
  if not reply_msg:
    return
  res = await check_time(str(reply_msg.date))
  if res == False:
    return
  if not reply_msg.text:

    return

  m_id = reply_msg.reply_to_message_id

  USER = update.from_user.id
  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.reply_text(DONT_SEND_TASK)

  if "Send new name for this file" in reply_msg.text:
    pass
  elif "Send new name to rename this file" in reply_msg.text:
    pass

  else:
    return
  details = await bot.get_messages(update.chat.id, m_id)
  await reply_msg.delete()
  file_name1 = update.text
  if not details.text:
    return await rename_cb(bot, details, file_name1)

  url = details.text
  try:
    url = await final_url(url)
    file_name, file_size = await get_details(url)

  except BaseException as ex:
    return await update.reply_text(str(ex))

  file_ext = file_name1.split(".")[-1]

  if file_ext == file_name1:
    file_ext = file_name.split(".")[-1]
    file_name1 += f".{file_ext}"

  await ddl_call_back(bot, reply_msg, USER, url, file_name1, file_size,
                      file_ext)
