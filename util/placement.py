import requests, json, time, os
from datetime import datetime, timedelta
from .funcs import git_push

BASE = "https://nyanko-events.ponosgames.com/control/placement/battlecats{}/event.json"
PIC = "https://ponosgames.com/information/appli/battlecats/placement{}/notice_{}.png"

def convertVersion(v):
    return f"{int(v[0:2])}.{int(v[2:4])}.{int(v[4:6])}"

def webhook(cc: str, res: dict):

    url = os.getenv("{}_WEBHOOK".format(cc.upper()))
    for event in res:
        data = {
            # "content":f"**檢測到新公告 !**\n\n`開始時間`:   <t:{event['start']}:F>\n`結束時間`:   <t:{event['end']}:F>\n\n`所需最小版本`:   `{convertVersion(event['min'])}`",
            "embeds": 
            [
                {
                    "title": "**檢測到新公告 !**",
                    "description":f"`開始時間`:   <t:{event['start']}:F>\n`結束時間`:   <t:{event['end']}:F>\n\n`所需最低版本`:   `{convertVersion(event['min'])}`",
                    "color": "4210752", #"int("%06x" % random.randint(0, 0xFFFFFF), 16),
                    "image": {"url": event["url"].replace("html", "png")},
                    "timestamp" : datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
        }

        headers = {
            "Content-Type": "application/json"
        }

        t = datetime.utcnow() + timedelta(hours=8)
        t_str = t.strftime("%Y-%m-%d %H:%M:%S")

        result = requests.post(url, json=data, headers=headers)
        
        if 200 <= result.status_code < 300:
            print(f"{t_str} Webhook sent {result.status_code}")
        else:
                print(f"{t_str} Not sent with {result.status_code}, response:\n{result.json()}")


def convertUnix(time: str):
    if time == -1:
        return -1
    t = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    t_gmt8 = t + timedelta(hours=8)
    return int(t_gmt8.timestamp())

def parse(cc: str, res: dict, notify: bool):
    dic = []
    j = json.load(open("event.json", "r"))
    for event in res["notice"]["data"]:
        if ((t:=convertUnix(event["start"])) > int(time.time())) and (event["id"] not in j[cc]["uuid"]):
            dic.append({
                "uuid": event["id"],
                "url": event["url"],
                "min": str(event["requirements"]["appversion"]["min"]),
                "start": t,
                "end": convertUnix(event.get("end", -1)),
            })
            print(f"{cc} new event: {event['id']}")
            j[cc]["uuid"].append(event["id"])
            with open(os.path.join(os.getcwd(), "Data", "placement", cc.upper(), f"{event['id']}.png"), "wb") as f:
                f.write(requests.get(PIC.format("" if cc == "jp" else f"/{cc}", event["id"])).content)
            open("placement.json", "w").write(json.dumps(j, indent=4))
    if cc != "kr" and notify:
        webhook(cc, dic)

def process(notify: bool):
    for cc in ["jp", "tw", "en", "kr"]:
        res = json.loads(requests.get(BASE.format("" if cc == "jp" else cc)).text)
        parse(cc, res, notify)

def placement(notify: bool):
    process(notify)
    git_push("add", "Update Certain Game Announcement")