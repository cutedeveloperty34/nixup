#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the secret configuration specific things
import os
import shutil
import time
import json
import pyrogram
import random
from Uploader.utitles import *
from Uploader.script import Translation
from Uploader.functions.database import *
from Uploader.utitles import random_dirs, fix_thumb
from Uploader.functions.help_Nekmo_ffmpeg import thumb_create
from Uploader.config import DONT_SEND_TASK, SUDO_USERS, TOTAL_TASKS
from Uploader.functions.display_progress import progress_for_pyrogram

# MEDIA formats for sending files
video_formats = [
  "MP4", "MOV", "WMV", "AVI", "AVCHD", "FLV", "F4V", "SWF", "MKV"
]
audio_formats = ["MP3", "WAV", "AIFF", "FLAC", "AAC", "WMA", "OGG", "M4A"]


@pyrogram.Client.on_message(pyrogram.filters.command(["rename"]))
async def rename_doc(bot, update):
  USER = update.from_user.id
  try:
    if USER not in SUDO_USERS:
      if len(SUDO_USERS) >= 5:
        return await update.reply_text(
          text="I am too busy please send me that command after sometime.")

      if USER in TOTAL_TASKS:
        return await update.reply_text(text=DONT_SEND_TASK)

    TOTAL_TASKS.append(USER)

    if (" " in update.text) and (update.reply_to_message is not None):

      _, file_name = update.text.split(" ", 1)
      dl_for_each_user, status, thumb_path = random_dirs(USER)

      if not os.path.isdir(dl_for_each_user):
        os.makedirs(dl_for_each_user)

      sent_message = await update.reply_text(text="Processing...")

      MSG = update.reply_to_message
      media_msg = MSG.video or MSG.document or MSG.audio or MSG.animation
      real_filename = media_msg.file_name

      extension = os.path.splitext(real_filename)[1]
      extension1 = os.path.splitext(file_name)[1]
      if extension1:
        file_name = file_name.replace(extension1, '')
        download_location = dl_for_each_user + file_name + extension1
        extension = extension.replace('.', '')

      else:
        if extension:
          download_location = dl_for_each_user + file_name + extension
          extension = extension.replace('.', '')
        else:
          extension = ''
          download_location = dl_for_each_user + file_name + extension

      caption = find_any(USER, "CAPTION")
      if not caption:
        caption = file_name
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

      if download_location is not None:
        await bot.edit_message_text(text="Uploading file",
                                    chat_id=update.chat.id,
                                    message_id=sent_message.id)

        thumb_id = find_any(USER, "PHOTO_THUMB")
        try:
          width, height, duration = await Mdata01(download_location)
        except:
          pass
        if thumb_id:
          ph_path1 = await bot.download_media(thumb_id, thumb_path)
          width, height, ph_path = await fix_thumb(ph_path1)

        else:
          ph_path = None
          # ph_path = await thumb_create(download_location, os.path.dirname(download_location), random.randint(0, duration - 1))

        # STart Time of Uploading
        time2 = time.time()

        if extension.upper() in video_formats:

          up_mode = find_any(USER, "AS_DOC")
          if up_mode == "OFF":
            SPOILER = find_any(USER, "SP_EFFECT")
            if SPOILER == "ON":
              spoiler = True
            else:
              spoiler = False

            thumb_id = find_any(USER, "PHOTO_THUMB")
            if not thumb_id:
              ph_path =  await thumb_create(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))
             

            await bot.send_video(
              chat_id=update.chat.id,
              video=file_path,
              thumb=ph_path,
              caption=caption,
              duration=duration,
              has_spoiler=spoiler,
              width=width,
              height=height,
              supports_streaming=True,
              progress=progress_for_pyrogram,
              progress_args=(Translation.UPLOAD_START.format(file_name),
                             sent_message, time2, bot, id, status))

          else:
            await bot.send_document(
              chat_id=update.chat.id,
              document=file_path,
              thumb=ph_path,
              caption=caption,
              progress=progress_for_pyrogram,
              progress_args=(Translation.UPLOAD_START.format(file_name),
                             sent_message, time2, bot, id, status))

        elif extension.upper() in audio_formats:

          duration = await Mdata03(file_path)
          await bot.send_audio(
            chat_id=update.chat.id,
            audio=file_path,
            thumb=ph_path,
            caption=caption,
            duration=duration,
            progress=progress_for_pyrogram,
            progress_args=(Translation.UPLOAD_START.format(file_name),
                           sent_message, time2, bot, id, status))

        else:

          await bot.send_document(
            chat_id=update.chat.id,
            document=file_path,
            thumb=ph_path,
            caption=caption,
            progress=progress_for_pyrogram,
            progress_args=(Translation.UPLOAD_START.format(file_name),
                           sent_message, time2, bot, id, status))

        time3 = time.time()
        up_time = time3 - time2
        down_time = time2 - time1

        try:
          shutil.rmtree(dl_for_each_user)

        except:
          pass

        await bot.edit_message_text(
          text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
            str(round(down_time)), str(round(up_time))),
          chat_id=update.chat.id,
          message_id=sent_message.id,
          disable_web_page_preview=True)
        try:
          TOTAL_TASKS.remove(USER)
        except:
          pass
    else:
      await bot.send_message(chat_id=update.chat.id,
                             text=Translation.REPLY_TO_DOC_FOR_REN,
                             reply_to_message_id=update.id)

  except:
    try:
      TOTAL_TASKS.remove(USER)
    except:
      pass


async def rename_cb(bot, msg, file_name):
  USER = msg.from_user.id
  try:

    if USER not in SUDO_USERS:
      if len(SUDO_USERS) >= 5:
        return await msg.reply_text(
          text=
          "I am to busy righ now please send me this task again after sometime."
        )
      if USER in TOTAL_TASKS:
        return await msg.reply_text(
          text=
          "I am not only for you dear so please wait for your previous task to completed."
        )

    caption = find_any(USER, "CAPTION")
    if not caption:
      caption = file_name

    dl_for_each_user, status, thumb_path = random_dirs(USER)

    if not os.path.isdir(dl_for_each_user):
      os.makedirs(dl_for_each_user)

    TOTAL_TASKS.append(USER)
    sent_message = await msg.reply_text(text="Processing...")

    media_msg = msg.video or msg.audio or msg.document or msg.animation
    real_filename = media_msg.file_name

    extension = os.path.splitext(real_filename)[1]
    extension1 = os.path.splitext(file_name)[1]
    if extension1:
      file_name = file_name.replace(extension1, '')
      download_location = dl_for_each_user + file_name + extension1
      extension = extension.replace('.', '')

    else:
      if extension:
        download_location = dl_for_each_user + file_name + extension
        extension = extension.replace('.', '')
      else:
        extension = ''
        download_location = dl_for_each_user + file_name + extension

    try:
      with open(status, 'w') as f:
        statusMsg = {'running': True, 'message': sent_message.id}
        json.dump(statusMsg, f, indent=2)

    except:
      pass
    time1 = time.time()
    file_path = await bot.download_media(message=msg,
                                         file_name=download_location,
                                         progress=progress_for_pyrogram,
                                         progress_args=("Downloading...\n",
                                                        sent_message, time1,
                                                        bot, id, status))
    if file_path is not None:
      await bot.edit_message_text(text="Uploading file",
                                  chat_id=msg.chat.id,
                                  message_id=sent_message.id)

      thumb_id = find_any(USER, "PHOTO_THUMB")
      if extension.upper() in video_formats:
        width, height, duration = await Mdata01(download_location)

      if thumb_id:
        ph_path1 = await bot.download_media(thumb_id, thumb_path)
        width, height, ph_path = await fix_thumb(ph_path1)

      else:
        ph_path = None

      thumb_path = ph_path

      # STart Time of Uploading
      time2 = time.time()

      if extension.upper() in video_formats:

        up_mode = find_any(USER, "AS_DOC")
        if up_mode == "OFF":
          SPOILER = find_any(USER, "SP_EFFECT")
          if SPOILER == "ON":
            spoiler = True
          else:
            spoiler = False

          thumb_id = find_any(USER, "PHOTO_THUMB")
          if not thumb_id:
            ph_path =  await thumb_create(file_path, os.path.dirname(file_path), random.randint(0, duration - 1))

          await bot.send_video(
            chat_id=msg.chat.id,
            video=file_path,
            thumb=thumb_path,
            caption=caption,
            duration=duration,
            has_spoiler=spoiler,
            width=width,
            height=height,
            supports_streaming=True,
            progress=progress_for_pyrogram,
            progress_args=(Translation.UPLOAD_START.format(file_name),
                           sent_message, time2, bot, id, status))

        else:
          await bot.send_document(
            chat_id=msg.chat.id,
            document=file_path,
            thumb=ph_path,
            caption=caption,
            progress=progress_for_pyrogram,
            progress_args=(Translation.UPLOAD_START.format(file_name),
                           sent_message, time2, bot, id, status))

      elif extension.upper() in audio_formats:
        duration = await Mdata03(file_path)

        await bot.send_audio(
          chat_id=msg.chat.id,
          audio=file_path,
          thumb=thumb_path,
          caption=caption,
          duration=duration,
          progress=progress_for_pyrogram,
          progress_args=(Translation.UPLOAD_START.format(file_name),
                         sent_message, time2, bot, id, status))

      else:
        await bot.send_document(
          chat_id=msg.chat.id,
          document=file_path,
          thumb=thumb_path,
          caption=caption,
          progress=progress_for_pyrogram,
          progress_args=(Translation.UPLOAD_START.format(file_name),
                         sent_message, time2, bot, id, status))

      time3 = time.time()
      up_time = time3 - time2
      down_time = time2 - time1

      try:
        shutil.rmtree(dl_for_each_user)
        print("REmoved from rename reply")

      except:
        pass

      try:
        await sent_message.edit_text(
          text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
            str(round(down_time)), str(round(up_time))),
          disable_web_page_preview=True)
      except:
        pass

      if USER in TOTAL_TASKS:
        TOTAL_TASKS.remove(USER)

  except:
    if USER in TOTAL_TASKS:
      TOTAL_TASKS.remove(USER)
