from curl_cffi import requests
import os
import sys
import time
import json
from datetime import datetime, timedelta
import time
from colorama import init, Fore, Style
from urllib.parse import parse_qs, urlparse, unquote
from base64 import b64decode
from time import gmtime
from time import strftime

init(autoreset=True)
# Define color variables
RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
BLUE = Fore.BLUE + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
CYAN = Fore.CYAN + Style.BRIGHT
WHITE = Fore.WHITE + Style.BRIGHT
RESET = Fore.RESET + Style.BRIGHT
GRAY = Fore.BLACK + Style.BRIGHT

#base headers
headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
  "Accept": "application/json, text/plain, */*",
  "Accept-Encoding": "gzip, deflate, br, zstd",
  "Content-Type": "application/json",
  "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"',
  "origin": "https://major.glados.app",
  "sec-fetch-site": "same-origin",
  "sec-fetch-mode": "cors",
  "sec-fetch-dest": "empty",
  "referer": "https://major.glados.app/",
  "accept-language": "en-US,en;q=0.9",
  "priority": "u=1, i",
  'Cookie': "cf_clearance=ajsEOQAWcAFfYbM0qlLaFoOjTjYnpxFICsaAimutcGc-1722089663-1.0.1.1-Phq1c4a3.l668dXK4wEML_Bva6iQ75ptYdkPLCBb9D8ItJ2MKH7Q8t_dalKGytjkJ9TWM4t_3PB0LkpJe9o7OA"
       
}

#parsing data
def data_parsing( data):
  return {k: v[0] for k, v in parse_qs(data).items()}

#check token if is expired
def is_expired( token):
  header, payload, sign = token.split(".")
  payload = b64decode(payload + "==").decode()
  jload = json.loads(payload)
  now = round(datetime.now().timestamp())
  exp = jload["exp"]
  if now > exp:
      return True
  return False

#get local token
def get_local_token(userid):
  if not os.path.exists("tokens.json"):
      open("tokens.json", "w").write(json.dumps({}))
  tokens = json.loads(open("tokens.json", "r").read())
  if str(userid) not in tokens.keys():
      return False
  return tokens[str(userid)]

#log for text
def log( message):
  now = datetime.now().isoformat(" ").split(".")[0]
  print(f"{GRAY}[{now}]{RESET} {message}")

#renew access_token
def renew_access_token(tg_data):
  data = json.dumps({"init_data": tg_data})
  headers["Content-Length"] = str(len(data))
  url = "https://major.glados.app/api/auth/tg/"
  try:
    res = requests.post(url, data=data, headers=headers, impersonate="chrome124")
    if "access_token" not in res.json().keys():
        log(f"{RED}access_token is not found in response, check you query_id !!")
        return False
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error checking data: {e}", flush=True)
    return {}

  access_token = res.json()["access_token"]
  log(f"{GREEN}Success get access_token ")
  return access_token

#save access_token to local
def save_local_token(userid, token):
  tokens = json.loads(open("tokens.json", "r").read())
  tokens[str(userid)] = token
  open("tokens.json", "w").write(json.dumps(tokens, indent=4))

#spin roulete
def spin_roulete(access_token):
   try:
      url = "https://major.glados.app/api/roulette"
      headers['Authorization'] = f"Bearer {access_token}"
      res = requests.post(url, headers=headers)
      if "blocked_until" in res.text.lower():
        timestamp = res.json()["detail"]["blocked_until"]
        log(f"{YELLOW}you already spin in today, waiting{RESET} {RED}{strftime("%H:%M:%S", gmtime(timestamp))}{RESET} {YELLOW}Hours for next spin !")
        return
      if "1" in res.text.lower():
        star = res.json()["rating_award"]
        log(f"{GREEN}success play spin roulete, got{RESET} {GRAY}{star} star !")
        return
   except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to play roulete, data: {e}", flush=True)
    return {}

#streak login
def streak(access_token):
  try:
    url = "https://major.glados.app/api/user-visits/streak/"
    headers['Authorization'] = f"Bearer {access_token}"
    res = requests.get(url, headers=headers)
    return res.json()
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to get streak login, data: {e}", flush=True)
    return {}

#streak login daily
def checkin(access_token):
  try:
    url = "https://major.glados.app/api/user-visits/visit/"
    headers['Authorization'] = f"Bearer {access_token}"
    res = requests.post(url, headers=headers,  impersonate="chrome124")
    streak(access_token)
    if res.status_code == 404:
      log(f"{RED}already check in today !")
      return
    if res.json()["is_allowed"] == True:
      streak_cekin = res.json()["streak"]
      log(f"{GREEN}success {streak_cekin}x streak check in today !")
      return
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to checkin, data: {e}", flush=True)
    return {}
  
#get assets
def get_assets(access_token, user_id):
  try:
    url = f"https://major.glados.app/api/users/{user_id}/"
    headers['Authorization'] = f"Bearer {access_token}"
    res = requests.get(url, headers=headers, impersonate="chrome124")
    streak(access_token)
    if res.status_code == 404:
      log(f"{RED}failed to get assets !")
      return
    if res.json()["rating"]:
      balance = res.json()["rating"]
      log(f"{GREEN}assets : {RESET}{GRAY}{balance} STAR !")
      return
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to checkin, data: {e}", flush=True)
    return {}
  
#get task daily
def get_task_daily(access_token):
  try:
    url = "https://major.glados.app/api/tasks/"
    params = {
      'is_daily': "true"
    }
    headers['Authorization'] = f"Bearer {access_token}"
    res = requests.get(url, params=params, headers=headers, impersonate="chrome124")
    
    if res.status_code == 404:
      log(f"{RED}failed to get daily task !")
      return
    else:
      return res.json()
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to get daily task, data: {e}", flush=True)
    return {}
  
#complete task
def complete_task(access_token, task):
  try:
    url = "https://major.glados.app/api/tasks/"
    for no, data in enumerate(task):
      id = data["id"]
      title = data["title"]
      payload = json.dumps({
        "task_id": id
      })

      headers['Authorization'] = f"Bearer {access_token}"
      res = requests.post(url, data=payload, headers=headers, impersonate="chrome124")
      if res.status_code == 404:
        log(f"{RED}failed complete task !")
        return
      if "True" in res.text or "true" in res.text:
        log(f"{GREEN}success complete task{RESET}{GRAY}{title} !")
      else:
        log(f"{RED}failed to complete task {RESET}{GRAY}{title} !")
  except (requests.RequestsError, ValueError) as e:
    print(f"{RED}Error to  complete task, data: {e}", flush=True)
    return {}

#animated loading
def animation(delay):
  if not os.path.exists("spiner.json"):
      open("spiner.json", "w").write(json.dumps({}))
  spiner = json.load(open("spiner.json", encoding="utf8"))
  frames = spiner["clock"]["frames"]
  interval = spiner["clock"]["interval"]
  end_time = time.time() + delay
  while time.time() < end_time:
    remaining_time = int(end_time - time.time())
    for frame in frames:
      print(f"\r{CYAN}menunggu kopi dan jarum coklat{RESET} {MAGENTA}{frame}{RESET} {CYAN}Tersisa{RESET} {GRAY}{remaining_time}{RESET} {CYAN}detik{RESET}         ", end="", flush=True)
      time.sleep(interval/1000)

#save failed access_token
def save_failed_token(userid,data):
  file = "auth_failed.json"
  if not os.path.exists(file):
      open(file,"w").write(json.dumps({}))
  
  acc = json.loads(open(file,'r').read())
  if str(userid) in acc.keys():
      return
  
  acc[str(userid)] = data
  open(file,'w').write(json.dumps(acc,indent=4))

def main():
  
  animation(15)
  print(Fore.YELLOW + Style.BRIGHT + "Buy me a coffee and JARCOK :) 08383 5438 3569 DANA")
  query_id = open("query.txt", "r").read().splitlines()
  if len(query_id) <= 0:
    log(f"{RED}add data account in Query first")
    sys.exit()
  for no, data in enumerate(query_id):
    data_parse = data_parsing(data)
    user = json.loads(data_parse["user"])
    userid = user["id"]
    first_name = user["first_name"]
    print(f"\r{CYAN}=== Akun ke {no + 1} | {first_name} ===", flush=True)
    access_token = get_local_token(userid)
    failed_fetch_token = False
    if access_token is False:
      access_token = renew_access_token(data)
      if access_token is False:
        save_failed_token(userid,data)
        failed_fetch_token = True
      save_local_token(userid,access_token)
    expired = is_expired(access_token)
    if expired:
      access_token = False
    if failed_fetch_token:
      continue
    checkin(access_token)
    spin_roulete(access_token)
    task = get_task_daily(access_token)
    complete_task(access_token, task)
    get_assets(access_token, userid)

if __name__ == "__main__":
  main()