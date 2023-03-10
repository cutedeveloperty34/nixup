import time
import json
import os
import random
import shutil
from Uploader.utitles import *
from Uploader.script import Translation
from Uploader.functions.database import *
from Uploader.functions.help_Nekmo_ffmpeg import thumb_create
from Uploader.config import TOTAL_TASKS, DONT_SEND_TASK, SUDO_USERS
from Uploader.functions.display_progress import progress_for_pyrogram

video_formats = [
  "MP4", "MOV", "WMV", "AVI", "AVCHD", "FLV", "F4V", "SWF", "MKV"
]
audio_formats = ["MP3", "WAV", "AIFF", "FLAC", "AAC", "WMA", "OGG", "M4A"]


async def change_thumb_func(bot, update):
  USER = update.from_user.id
  update = update.message

  if USER not in SUDO_USERS:
    if USER in TOTAL_TASKS:
      return await update.reply_text(text=DONT_SEND_TASK)
    if len(TOTAL_TASKS) >= 5:
      return await update.reply_text(
        "I am too busy now please send this task after sometime...")

  download_for_user, status, thumb_path = random_dirs(USER)

  if not os.path.isdir(download_for_user):
    os.makedirs(download_for_user)

  sent_message = await update.reply_text(text="Processing...")
  TOTAL_TASKS.append(USER)

  MSG = update.reply_to_message

  if MSG.video:
    real_filename = MSG.video.file_name

  if MSG.audio:
    real_filename = MSG.audio.file_name

  if MSG.animation:
    real_filename = MSG.animation.file_name

  if MSG.document:
    real_filename = MSG.document.file_name

  extension = os.path.splitext(real_filename)[1]

  extension = extension.replace('.', '')

  download_location = f"{download_for_user}/{real_filename}"

  caption = find_any(USER, "CAPTION")
  if not caption:
    caption = real_filename

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
                                                      sent_message, time1, bot,
                                                      id, status))
  if file_path is not None:
    await bot.edit_message_text(text="Uploading file",
                                chat_id=update.chat.id,
                                message_id=sent_message.id)

    try:
      width, height, duration = await Mdata01(file_path)
    except:
      pass
    thumb_id = find_any(USER, "PHOTO_THUMB")
    if thumb_id:
      ph_path1 = await bot.download_media(thumb_id, thumb_path)
      width, height, ph_path = await fix_thumb(ph_path1)

    else:
      ph_path = None

    file_name = real_filename
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
          ph_path = await thumb_create(file_path, os.path.dirname(file_path),
                                       random.randint(0, duration - 1))
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
      shutil.rmtree(download_for_user)

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

  if USER in TOTAL_TASKS:
    TOTAL_TASKS.remove(USER)
