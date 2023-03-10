#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import os
import time
import shutil
import json
import random
from Uploader.utitles import *
from pyrogram import Client, filters
from Uploader.script import Translation
from Uploader.functions.database import *
from Uploader.functions.help_Nekmo_ffmpeg import thumb_create
from Uploader.config import TOTAL_TASKS, DONT_SEND_TASK, SUDO_USERS
from Uploader.functions.display_progress import progress_for_pyrogram


@Client.on_message(filters.private & filters.command(["convert2video"]))
async def convert_to_video(bot, update):
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
    # print(update.reply_to_message)
    if not (update.reply_to_message.video or update.reply_to_message.document):
      return await update.reply_text(Translation.REPLY_TO_DOC_FOR_C2V)

    media_msg = update.reply_to_message
    # filesize = media_msg.document.file_size
    media = media_msg.document or media_msg.video or media_msg.animation
    file_name = media.file_name

    sent_message = await update.reply_text(text="Processing...")
    TOTAL_TASKS.append(USER)

    download_location, status, thumb_path = random_dirs(USER)
    if not os.path.isdir(download_location):
      os.makedirs(download_location)

    try:
      with open(status, 'w') as f:
        statusMsg = {'running': True, 'message': sent_message.id}
        json.dump(statusMsg, f, indent=2)

    except:
      pass

    time1 = time.time()

    file_path = await bot.download_media(message=update.reply_to_message,
                                         file_name=download_location,
                                         progress=progress_for_pyrogram,
                                         progress_args=("Downloading...\n",
                                                        sent_message, time1,
                                                        bot, id, status))

    if file_path is not None:

      await sent_message.edit_text(text="Uploading...", )
      caption = find_any(USER, "CAPTION")
      if not caption:
        caption = file_name

      thumb_id = find_any(USER, "PHOTO_THUMB")
      width, height, duration = await Mdata01(file_path)
      if thumb_id:
        ph_path1 = await bot.download_media(thumb_id, thumb_path)
        width, height, ph_path = await fix_thumb(ph_path1)

      else:
        ph_path = None
        #thumb = await thumb_create(file_path, os.path.dirname(file_path), random.randint(0, duration - 1))

      SPOILER = find_any(USER, "SP_EFFECT")
      if SPOILER == "ON":
        spoiler = True
      else:
        spoiler = False

      thumb_id = find_any(USER, "PHOTO_THUMB")
      if not thumb_id:
        ph_path = await thumb_create(file_path, os.path.dirname(file_path),
                                     random.randint(0, duration - 1))

      time2 = time.time()
      await bot.send_video(chat_id=update.chat.id,
                           video=file_path,
                           duration=duration,
                           caption=caption,
                           width=width,
                           height=height,
                           supports_streaming=True,
                           has_spoiler=spoiler,
                           thumb=ph_path,
                           reply_to_message_id=update.reply_to_message.id,
                           progress=progress_for_pyrogram,
                           progress_args=("Uploading...\n", sent_message,
                                          time2, bot, id, status))
      time3 = time.time()
      up_time = time3 - time2
      down_time = time2 - time1

      try:
        shutil.rmtree(download_location)

      except:
        pass

      await bot.edit_message_text(
        text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
          str(round(down_time)), str(round(up_time))),
        chat_id=update.chat.id,
        message_id=sent_message.id,
        disable_web_page_preview=True)

  else:
    await bot.send_message(chat_id=update.chat.id,
                           text=Translation.REPLY_TO_DOC_FOR_C2V,
                           reply_to_message_id=update.id)

  if USER in TOTAL_TASKS:
    TOTAL_TASKS.remove(USER)
