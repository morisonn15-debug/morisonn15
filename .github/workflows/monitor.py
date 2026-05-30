import datetime
import math
import requests
import numpy as np
import time

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1508709432996139070/3yp3mciR9pEFV5treYOYd4cLPgFmpU1tzPw43cFf7YvrRRrgomTpO3kCtlGvdUJNGmFs"
ALERT_THRESHOLD = 70.0
W1, W2, W3, W4, THETA = 1.8, 2.2, 1.2, 1.0, 2.0

SPOTS = {
    "A:大洗サンビーチ": {"lat": 36.293451, "lon": 140.575631, "f_G": 1.5, "k_Topo": 0.6},
    "B:鉾田": {"lat": 36.195357, "lon": 140.591696, "f_G": 1.1, "k_Topo": 1.0},
    "C:神栖・波崎": {"lat": 35.782012, "lon": 140.767425, "f_G": 1.2, "k_Topo": 0.5},
    "D:千葉・一宮": {"lat": 35.388414, "lon": 140.392015, "f_G": 1.1, "k_Topo": 0.9},
    "E:千葉・勝浦": {"lat": 35.141505, "lon": 140.313412, "f_G": 1.3, "k_Topo": 0.8},
    "F:千葉・館山": {"lat": 34.984534, "lon": 139.851253, "f_G": 1.4, "k_Topo": 0.7}
}

def get_topo(lat, lon):
    return np.random.choice(["第1ブレイク接近", "離岸流あり", "急深", "サンドバー形成"])

class Engine:
    def calculate(self, config):
        sst, chl_a = 18.0, 0.5
        f_T = max(0, 1 - abs(sst - 19.0) / 5.0)
        f_W, f_C = 0.5, min(1.0, chl_a / 2.0)
        logit = W1 * f_T + W2 * f_W + W3 * f_C + W4 * config['k_Topo'] - THETA
        p_bait = (1 / (1 + math.exp(-logit))) * 100
        p_fish = min(100.0, p_bait * config['f_G'])
        return round(p_fish, 1), round(p_bait, 1), {"f_T": f_T, "f_W": f_W, "k_Topo_dyn": config['k_Topo']}

def send(name, pf, pb, fac, lat, lon):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = {"embeds": [{"title": "ヒラメ予測", "fields": [{"name": "スポット", "value": name, "inline": True}, {"name": "期待値", "value": f"{pf}%", "inline": True}]}]}
    requests.post(DISCORD_WEBHOOK_URL, json=msg)

if __name__ == "__main__":
    engine = Engine()
    for name, config in SPOTS.items():
        pf, pb, fac = engine.calculate(config)
        if pf >= ALERT_THRESHOLD:
            send(name, pf, pb, fac, config['lat'], config['lon'])
