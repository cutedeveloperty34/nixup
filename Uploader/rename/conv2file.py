#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import os
import json
import time
import shutil
import asyncio
from pyrogram import Client, filters
from Uploader.script import Translation
from Uploader.functions.database import *
from Uploader.utitles import random_dirs, fix_thumb
from Uploader.config import TOTAL_TASKS, DONT_SEND_TASK, SUDO_USERS
from Uploader.functions.display_progress import progress_for_pyrogram


@Client.on_message(filters.private & filters.command(["convert2file"]))
async def convert_to_file(bot, update):
  USER = update.from_user.id

  try:
    update = update.message
  except:
    update = update

  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.reply_text(text=DONT_SEND_TASK)
    if len(TOTAL_TASKS) >= 5:
      return await update.reply_text(
        "I am too busy now please send this task after sometime...")
  if update.reply_to_message:

    down_location, status, thumb_path = random_dirs(USER)
    if not os.path.isdir(down_location):
      os.makedirs(down_location)

    TOTAL_TASKS.append(USER)
    sent_message = await update.reply_text(text="Processing...")
    file_name = update.reply_to_message.video.file_name
    file_path = down_location + file_name

    try:
      with open(status, 'w') as f:
        statusMsg = {'running': True, 'message': sent_message.id}
        json.dump(statusMsg, f, indent=2)

    except:
      pass

    time1 = time.time()
    file_path = await bot.download_media(message=update.reply_to_message,
                                         file_name=file_path,
                                         progress=progress_for_pyrogram,
                                         progress_args=("Downloading\n\n",
                                                        sent_message, time1,
                                                        bot, id, status))

    if file_path is not None:

      await sent_message.edit_text(text="Uploading...", )
      thumb_id = find_any(USER, "PHOTO_THUMB")

      if thumb_id:
        ph_path1 = await bot.download_media(thumb_id, thumb_path)
        width, height, ph_path = await fix_thumb(ph_path1)

      else:
        ph_path = None

      caption = find_any(USER, "CAPTION")
      if not caption:
        caption = file_name

      await asyncio.sleep(1)
      # try to upload file
      time2 = time.time()
      await bot.send_document(chat_id=update.chat.id,
                              document=file_path,
                              caption=caption,
                              thumb=ph_path,
                              reply_to_message_id=update.reply_to_message.id,
                              progress=progress_for_pyrogram,
                              progress_args=("Uploading...\n\n", sent_message,
                                             time2, bot, id, status))

      # removing all temp files from storage
      time3 = time.time()
      up_time = time3 - time2
      down_time = time2 - time1
      try:
        shutil.rmtree(down_location)

      except:
        pass

      try:
        await bot.edit_message_text(
          text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
            str(round(down_time)), str(round(up_time))),
          chat_id=update.chat.id,
          message_id=sent_message.id,
          disable_web_page_preview=True)
      except:
        pass

  else:
    await bot.send_message(chat_id=update.chat.id,
                           text=Translation.REPLY_TO_DOC_FOR_C2F,
                           reply_to_message_id=update.id)

  if USER in TOTAL_TASKS:
    TOTAL_TASKS.remove(USER)
