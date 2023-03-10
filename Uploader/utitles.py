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


from PIL import Image
from Uploader.config import Config
from Uploader.functions.ran_text import random_char
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


async def Mdata01(download_directory):
    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")

    return width, height, duration


async def Mdata02(download_directory):
    width = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")

    return width, duration


async def Mdata03(download_directory):
    metadata = extractMetadata(createParser(download_directory))
    return (
        metadata.get('duration').seconds
        if metadata is not None and metadata.has("duration")
        else 0
    )


async def make_thumb(thumb_image_path, width, height):
  thumb_size = (width, height)
  try:
    img = Image.new('RGB', thumb_size, (85, 85, 85))
    img.save(thumb_image_path)
  except:
    img = Image.new('RGB', (1280, 1280), (85, 85, 85))
    img.save(thumb_image_path)

  return thumb_image_path


async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb != None:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, height))
                img.save(thumb, "JPEG")
    except Exception as e:
        print(e)
        thumb = None 
       
    return width, height, thumb

def random_dirs(chat_id):
    rendem = random_char(5)
    download_dir = Config.DOWNLOAD_LOCATION
    dir_for_user = f"{download_dir}/{rendem}-{str(chat_id)}/"
    status = f"{dir_for_user}status.json"
    thumb_path = f"{dir_for_user}image.jpg"

    return dir_for_user,status,thumb_path

