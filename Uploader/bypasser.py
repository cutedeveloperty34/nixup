import requests
import re
from bs4 import BeautifulSoup
from httpx import AsyncClient, Timeout

import time, bs4, json

login_key = "092bad969dc91a35b649"
key = "kqq3bYPdkvS6x9"


def get_ticket(file_id):
  headers = {'file': file_id, 'login': login_key, 'key': key}
  response = requests.get("https://api.strtape.tech/file/dlticket?", headers)
  data = json.loads(response.text)
  # print(data)
  result = data.get('result')
  return result


def dl_url(ticket, file_id):
  headers = {'file': file_id, 'ticket': ticket, 'login': login_key, 'key': key}
  response = requests.get("https://api.strtape.tech/file/dl?", headers)
  data = json.loads(response.text)
  # print(data)
  result = data.get('result')
  if result is not None:
    link = result.get('url')
    return link
  else:
    return "Not Found"


def get_file_id(link):
  lst = []
  for i in link:
    lst.append(i)

  lst2 = lst[25:]

  file_id = ""
  for i in lst2:
    if i == "/":
      break
    else:
      file_id += i
  # print(file_id)
  return file_id


def get_direct_streamtape(url):
  link = url.replace("tape.to", "tape.com")
  url = link
  file_id = get_file_id(url)
  result = get_ticket(file_id)
  ticket = result.get('ticket')
  time.sleep(result.get('wait_time'))
  link = dl_url(ticket, file_id)

  return link


# later
def streamtape_scrape(url):
  text = requests.get(url).text
  soup = bs4.BeautifulSoup(text, 'html.parser')
  norobotlink = soup.find(id='norobotlink')
  return norobotlink.text


def url_exists(url) -> bool:
    try:
        with requests.get(url, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False
  



class Httpx:

  @staticmethod
  async def get(url: str, headers: dict = None, red: bool = True):
    async with AsyncClient() as ses:
      try:
        return await ses.get(url,
                             headers=headers,
                             follow_redirects=red,
                             timeout=Timeout(10.0))
      except BaseException:
        pass


async def streamtape_bypass(url: str) -> str:

  response = await Httpx.get(url)
  if videolink := re.findall(r"document.*((?=id\=)[^\"']+)", response.text):
    return f"https://streamtape.com/get_video?{videolink[-1]}"
  return ""


async def mdisk_bypass(url: str) -> str:

  url = url[:-1] if url[-1] == "/" else url
  token = url.split("/")[-1]
  api = f"https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={token}"
  response = (await Httpx.get(api)).json()

  return response["download"].replace(" ", "%20")


async def mediafire_bypass(mediafire_url: str) -> str:

  link = re.search(r"\bhttps?://.*mediafire\.com\S+", mediafire_url)[0]
  page = BeautifulSoup((await Httpx.get(link)).content, "html.parser")
  return page.find("a", {"aria-label": "Download file"}).get("href")


async def anonfiles_bypass(anonfiles_url: str) -> str:
  soup = BeautifulSoup((await Httpx.get(anonfiles_url)).content, "html.parser")
  return dlurl["href"] if (dlurl := soup.find(id="download-url")) else ""


async def final_url(url: str) -> str:
  if 'https://anonfiles.com' in url:
    final_link = await anonfiles_bypass(url)
  elif '//bayfiles.com' in url:
    final_link = await anonfiles_bypass(url)
  elif 'mdisk.me' in url:
    final_link = await mdisk_bypass(url)
  elif 'streamtape' in url:
    final_link = get_direct_streamtape(url)
  elif 'mediafire.com' in url:
    final_link = await mediafire_bypass(url)
  else:
    final_link = url

  return final_link


async def get_details(url):
  response = requests.head(url)
  # print(response.headers)
  if "Content-Disposition" in response.headers:
    try:
      filename = re.findall("filename=(.+)",
                            response.headers["Content-Disposition"])[0]
    except:
      filename = "Untitled"
  else:
    filename = url.split("/")[-1]
    try:
      url = url[:url.index('?hash')]
      filename = url.split("/")[-1]

    except:
      filename = url.split("/")[-1]

  # Extract the file size
  if "Content-Length" in response.headers:
    file_size = int(response.headers["Content-Length"]) / 1024 / 1024
  else:
    file_size = None

  if file_size:
    file_size = (f"{file_size:.2f}") #file size in megaBytes
    
  else:
    file_size = "0.0"

  file_size = float(file_size)

  filename = filename.strip('"')

  return filename, file_size
