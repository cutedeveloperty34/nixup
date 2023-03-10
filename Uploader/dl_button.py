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
import math
import json
import time
import shutil
import random
import aiohttp
import asyncio
import requests
import threading
from Uploader.utitles import *
from Uploader.config import Config
from Uploader.config import TOTAL_TASKS
from Uploader.script import Translation
from Uploader.functions.database import *
from Uploader.bypasser import get_details
from Uploader.functions.help_Nekmo_ffmpeg import thumb_create
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Uploader.functions.display_progress import progress_for_pyrogram as progress2, humanbytes, TimeFormatter

video_formats = [
  "MP4", "MOV", "WMV", "AVI", "AVCHD", "FLV", "F4V", "SWF", "MKV"
]
audio_formats = ["MP3", "WAV", "AIFF", "FLAC", "AAC", "WMA", "OGG", "M4A"]


# sourcery skip: low-code-quality
async def ddl_call_back(bot, update, USER, url, name, file_size, file_x):
  TOTAL_TASKS.append(USER)

  caption = find_any(USER, "CAPTION")
  if not caption:
    caption = name

  tmp_dir_for_user, status, thumb_path = random_dirs(USER)

  if not os.path.isdir(tmp_dir_for_user):
    os.makedirs(tmp_dir_for_user)
  download_directory = f"{tmp_dir_for_user}/{name}"

  sent_message = await update.reply_text(
    text=Translation.DOWNLOAD_START.format(name))

  try:
    with open(status, 'w') as f:
      statusMsg = {'running': True, 'message': sent_message.id}
      json.dump(statusMsg, f, indent=2)

  except:
    pass
  async with aiohttp.ClientSession() as session:
    time1 = time.time()
    try:
      await download_coroutine(bot, session, url, download_directory,
                               update.chat.id, sent_message.id, time1, status)

    except asyncio.TimeoutError:
      await sent_message.edit_text(text=Translation.SLOW_URL_DECED)
      if USER in TOTAL_TASKS:
        TOTAL_TASKS.remove(USER)

  if os.path.exists(download_directory):
    await sent_message.edit_text(text=Translation.UPLOAD_START.format(name))

    file_size = round(float(file_size))
    if file_size > Config.TG_MAX_FILE_SIZE:
      await sent_message.edit_text(text=Translation.RCHD_TG_API_LIMIT)

    else:
      try:
        width, height, duration = await Mdata01(download_directory)
      except:
        pass
      thumb_id = find_any(USER, "PHOTO_THUMB")
      if thumb_id:
        ph_path1 = await bot.download_media(thumb_id, thumb_path)
        width, height, ph_path = await fix_thumb(ph_path1)

      else:
        ph_path = None
        # thumb = await thumb_create(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))

      time2 = time.time()
      thumb = ph_path

      if file_x.upper() in video_formats:
        up_mode = find_any(USER, "AS_DOC")

        if up_mode == "OFF":

          SPOILER = find_any(USER, "SP_EFFECT")
          if SPOILER == "ON":
            spoiler = True
          else:
            spoiler = False

          _, __, duration = await Mdata01(download_directory)
          thumb_id = find_any(USER, "PHOTO_THUMB")
          if not thumb_id:
            thumb = await thumb_create(download_directory,
                                       os.path.dirname(download_directory),
                                       random.randint(0, duration - 1))

          await bot.send_video(
            chat_id=update.chat.id,
            video=download_directory,
            thumb=thumb,
            caption=caption,
            duration=duration,
            width=width,
            height=height,
            has_spoiler=spoiler,
            supports_streaming=True,
            progress=progress2,
            progress_args=(Translation.UPLOAD_START.format(name), sent_message,
                           time2, bot, id, status))
        else:
          await bot.send_document(
            chat_id=update.chat.id,
            document=download_directory,
            thumb=thumb,
            caption=caption,
            progress=progress2,
            progress_args=(Translation.UPLOAD_START.format(name), sent_message,
                           time2, bot, id, status))

      elif file_x.upper() in audio_formats:
        duration = await Mdata03(download_directory)
        await bot.send_audio(
          chat_id=update.chat.id,
          audio=download_directory,
          thumb=thumb,
          caption=caption,
          duration=duration,
          progress=progress2,
          progress_args=(Translation.UPLOAD_START.format(name), sent_message,
                         time2, bot, id, status))

      else:
        await bot.send_document(
          chat_id=update.chat.id,
          document=download_directory,
          thumb=thumb,
          caption=caption,
          progress=progress2,
          progress_args=(Translation.UPLOAD_START.format(name), sent_message,
                         time2, bot, id, status))

      time3 = time.time()
      up_time = time3 - time2
      down_time = time2 - time1

      try:
        shutil.rmtree(tmp_dir_for_user)

      except Exception:
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

  else:
    pass
    # await sent_message.edit_text(
    # text=Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link"),
    # disable_web_page_preview=True)

  if USER in TOTAL_TASKS:
    TOTAL_TASKS.remove(USER)


async def download_file(url, msg, file_name, start_t, d_msg, num_threads=1):
  """Download a file from a given URL using multi-connection"""

  # Get file size and calculate chunk size
  r = requests.head(url)

  size = int(r.headers.get('content-length', 0))
  chunk_size = size // num_threads

  # Create a list of threads to download each chunk
  threads = []
  with requests.get(url, stream=True) as r:
    # Set up progress tracking variables
    downloaded = 0
    progress_lock = threading.Lock()

    # Define function to download a single chunk
    def download_chunk(start, end):
      nonlocal downloaded
      headers = {'Range': f'bytes={start}-{end}'}
      with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(file_name, 'wb') as f:
          f.seek(start)
          for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
              break
            f.write(chunk)
            with progress_lock:
              downloaded += len(chunk)
              percent = downloaded / size * 100

              r_percent = round(percent)
              if (r_percent % 10 == 0):
                time1 = time.time() - start_t  # 15

                rem = size - downloaded  # load

                speed = (downloaded / time1) / (1024)
                speed1 = speed * 1024
                eta_time = ((rem / speed) // 1024) * 1000
                eta_time = round(eta_time)

                progress = "[{0}{1}]\n**Progress :** {2}%\n".format(
                  ''.join(["◾" for i in range(math.floor(percent / 10))
                           ]),  # 7.6923
                  ''.join(["◽" for i in range(10 - math.floor(percent / 10))]),
                  round(percent, 2))

                tmp = progress + "**Completed :** {0} of {1}\n**Speed :** {2}/s\n**ETA :** {3}\n".format(
                  humanbytes(downloaded), humanbytes(size), humanbytes(speed1),
                  TimeFormatter(eta_time))
                print(tmp)

                try:
                  msg.edit_text(tmp)
                except Exception as ex:
                  print(ex)

    # Start a thread for each chunk
    for i in range(num_threads):
      start = i * chunk_size
      end = start + chunk_size - 1 if i < num_threads - 1 else size - 1
      thread = threading.Thread(target=download_chunk, args=(start, end))
      threads.append(thread)
      thread.start()

    # Wait for all threads to finish
    for thread in threads:
      thread.join()

  return file_name


async def download_coroutine(bot, session, url, file_name, chat_id, message_id,
                             start, status):
  try:

    downloaded = 0
    # display_message = ""
    cancel_button = InlineKeyboardButton(
      "Cancel", callback_data=f"cancel_upload#{status}")

    reply_markup = InlineKeyboardMarkup([[cancel_button]])
    name = file_name.split("/")[-1]

    ud_type = f"**File Name:** {name}\n\n**Downloading...**\n"
    async with session.get(url,
                           timeout=Config.PROCESS_MAX_TIMEOUT) as response:

      total_length = int(response.headers["Content-Length"], 0)
      # print(response.headers)
      try:
        content_type = response.headers["Content-Type"]  # Content-Type
      except:
        content_type = 'video'
      if "text" in content_type or total_length < 500:
        return await response.release()
      with open(file_name, "wb") as f_handle:
        while True:
          chunk = await response.content.read(Config.CHUNK_SIZE)
          if not chunk:
            break
          f_handle.write(chunk)
          downloaded += Config.CHUNK_SIZE

          now = time.time()
          diff = now - start
          if round(diff % 5.0) == 0 or downloaded == total_length:
            if os.path.exists(status):
              with open(status, 'r+') as f:
                statusMsg = json.load(f)
                if not statusMsg["running"]:
                  return await response.release()

            percentage = downloaded * 100 / total_length
            speed = downloaded / diff
            # print(speed)
            elapsed_time = round(diff) * 1000
            time_to_completion = (round(
              (total_length - downloaded) / speed) * 1000)
            estimated_total_time = elapsed_time + time_to_completion
            progress = "[{0}{1}]\n**Progress :** {2}%\n".format(
              # 7.6923
              ''.join(["◾️" for i in range(math.floor(percentage / 10))]),
              ''.join(["◽️" for i in range(10 - math.floor(percentage / 10))]),
              round(percentage, 2))

            tmp = progress + "**Completed :** {0} of {1}\n**Speed :** {2}/s\n**ETA :** {3}\n".format(
              humanbytes(downloaded), humanbytes(total_length),
              humanbytes(speed), TimeFormatter(time_to_completion))

            text = "{}{}".format(ud_type, tmp)
            try:
              await bot.edit_message_text(chat_id,
                                          message_id,
                                          text=text,
                                          reply_markup=reply_markup)
            except:
              pass
      return await response.release()

  except Exception as ex:
    await bot.edit_message_text(chat_id, message_id, text=str(ex))
