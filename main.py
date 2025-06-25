from utils import *
from temp_mails import Mail_tm
from time import sleep
import requests, re, time, secrets, json


def register():
    r = requests.session()
    tm = Mail_tm()

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.meshy.ai",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.meshy.ai/",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "x-client-info": "supabase-ssr/0.4.1",
        "x-supabase-api-version": "2024-01-01",
    }

    json_data = {
        "email": tm.email,
        "data": {},
        "create_user": True,
        "gotrue_meta_security": {},
        "code_challenge": hsh(),
        "code_challenge_method": "s256",
    }

    response = r.post(
        "https://auth.meshy.ai/auth/v1/otp", headers=headers, json=json_data
    ).json()
    if response:
        if response["code"]:
            return False

    ic("OTP SENT !")
    ic("temp address:", tm.email)
    otp = None
    for x in range(10):
        if otp:
            break
        for msg in tm.get_inbox():
            html = tm.get_mail_content(msg["id"])
            # print(html)
            if m := re.search(r';">(\d{4,8})', html):
                otp = m.group().replace(';">', "")
                break
        time.sleep(4)
    if not otp:
        ic("OTP NOT FOUND")
        return False
    ic(otp)

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
        "cache-control": "no-cache",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.meshy.ai",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.meshy.ai/",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "x-client-info": "supabase-ssr/0.4.1",
        "x-supabase-api-version": "2024-01-01",
    }

    json_data = {
        "type": "email",
        "email": tm.email,
        "token": otp,
        "gotrue_meta_security": {},
    }
    try:
        response = r.post(
            "https://auth.meshy.ai/auth/v1/verify", headers=headers, json=json_data
        ).json()
        if response.get("access_token"):
            ic("Successfully created", tm.email)
            del response["user"]
            save(tm.email, response)
            return response
    except:
        ic("FATAL register() : failed account creation.")
    ic("failed account creation.")
    ic(response)

    return False


# register()


def getacc():
    with open("accounts.json", "r+") as f:
        accs = json.load(f)
        return accs


class meshy:
    def __init__(self, acc_data):
        self.email, self.auth_data = acc_data
        self.expires_at = self.auth_data["expires_at"]
        self.r = requests.session()
        if self.expires_at < int(time.time()):
            self.auth_data = self.reauth()
        self.access_token = self.auth_data["access_token"]
        self.token_type = self.auth_data["token_type"]
        self.r.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {self.access_token}",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.meshy.ai",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://www.meshy.ai/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def reauth(self):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluZnJlY2xzeGZncW52Z2ZweGNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU1ODQwNjUsImV4cCI6MjAzMTE2MDA2NX0.015muXUW_O30jeBOxEU9-TQOJigcKMUhkNFbPOWu_iA",
            "cache-control": "no-cache",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.meshy.ai",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://www.meshy.ai/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-client-info": "supabase-ssr/0.4.1",
            "x-supabase-api-version": "2024-01-01",
        }

        params = {
            "grant_type": "refresh_token",
        }

        json_data = {
            "refresh_token": self.auth_data["refresh_token"],
        }

        response = self.r.post(
            "https://auth.meshy.ai/auth/v1/token",
            params=params,
            headers=headers,
            json=json_data,
        ).json()
        if response.get("access_token"):
            ic("Refreshed session:", self.email)
            del response["user"]
            save(self.email, response)
            return response
        else:
            ic("Failed to refresh auth creds eziting..")
            exit()
            return False

    def task(self, text="King", model="meshy-5", seed =secrets.randbits(32)): 
        self.prompt = text
        json_data = {
            'phase': 'draft',
            'args': {
                'draft': {
                    'prompt': text,
                    'seed': seed,
                    'license': 'cc-by-4.0',
                    'aiModel': 'meshy-5',
                    'symmetryMode': 0,
                },
            },
            'isNSFW': False,
        }
        
        response = self.r.post('https://api.meshy.ai/web/v2/tasks', json=json_data).json()
        if response['code'] == "OK":
            return response['result']
        else:
            ic(response)
            return None
        
    def status(self, taskid, poll=True):
        response = self.r.get(f'https://api.meshy.ai/web/v1/tasks/{taskid}/status').json()
        result = response['result']
        if response["code"] == "OK":
            while (result['status'] == "IN_PROGRESS" or result['status'] == 'PENDING') and poll:
                response = self.r.get(f'https://api.meshy.ai/web/v1/tasks/{taskid}/status').json()
                result = response['result']
                sleep(2)
            # if result['status'] == "SUCCEEDED":
            #     print(self.r.get(f'https://api.meshy.ai/web/v1/tasks/{taskid}').text)
            if result["status"] =="FAILED":
                return "FAILED"
            return result
        return "FAILED"
    
    def colour_it(self, taskid, prompt = "king", seed =secrets.randbits(32),targetPolycount=10000):
        try:
            prompt = self.prompt
        except:
            pass
        json_data = {
            'phase': 'generate',
            'parent': taskid,
            'args': {
                'generate': {
                    'draftIds': [
                        '1',
                    ],
                },
                'texture': {
                    'prompt': prompt,
                    'imageId': '',
                    'artStyle': 'realistic',
                    'seed': seed,
                },
                'remesh': {
                    'topology': 'triangle',
                    'decimationMode': 0,
                    'targetPolycount': targetPolycount,
                },
            },
        }

        response = self.r.post('https://api.meshy.ai/web/v2/tasks', json=json_data).json()
        print(response)
        return response['result'][0]
        
        
    def animate_it(self, taskid, prompt="king"):
        estimation = self.r.post(f"https://api.meshy.ai/web/v2/tasks/{taskid}/estimate-pose").json()
        if estimation["code"] != "OK":
            ic("Estimation failed ", taskid)
            return "FAILED ESTIMATION"
        estimation = estimation['result']
        json_data = {
            'phase': 'animate',
            'parent': taskid,
            'args': {
                'animate': {
                    'showcaseId': '',
                    'animationType': 'biped',
                    'fps': 30,
                    'offset': 0,
                    'scale': 1.7,
                    'positionJson': json.dumps(estimation),
                    'rx': 0,
                    'ry': 0,
                    'rz': 0,
                },
            },
        }
        # print(json_data)
        # exit()
        response = self.r.post('https://api.meshy.ai/web/v2/tasks', json=json_data).json()
        if response["code"] == "OK":
            return response["result"]
        ic(response)
        return "FAILED"
    
    def getTask(self, taskid):
        return self.r.get(f"https://api.meshy.ai/web/v2/tasks/{taskid}").json()
    
# register()
ai = meshy(list(getacc().items())[0])

taskid = ai.task("king")
ic(taskid)
ai.status(taskid)
coloured_id = ai.colour_it(taskid)
ic(coloured_id)
status = ai.status(coloured_id)


########## this is only for coloured urls

if status["status"] == "SUCCEEDED":
    colour_modelurl = status['result']['modelUrl']
    ic(colour_modelurl)
    colour_preview = status['result']['previewUrl']
    ic(colour_preview)
    colour_videoUrl  = status['result']['videoUrl']
    ic(colour_videoUrl)
    
    
############### animating it

animate_id = ai.animate_it(coloured_id)
ic(animate_id)
status = ai.status(animate_id)
if status["status"] == "SUCCEEDED":
    animate_modelurl = status['result']['modelUrl']
    ic(animate_modelurl)
    animate_preview = status['result']['previewUrl']
    ic(animate_preview)
    animate_videoUrl  = status['result']['videoUrl']
    ic(animate_videoUrl)
    
animate_final = ai.getTask(animate_id)['result']['result']['animate']['actions']
walking_model = animate_final[0]["animationGlbUrl"]
running_model = animate_final[1]["animationGlbUrl"]
ic(walking_model)
ic(running_model)