from pypresence import Presence
import toml
import time
import requests

def get(url, params=None, headers=None):
    with requests.get(url, params=params, headers=headers) as response:
        response.raise_for_status()
        return response.json()
        

config = toml.load("settings.toml")
RPC = Presence(config["client_id"])
RPC.connect()

def main():
    past_of_set = False
    while True:
        config = toml.load("settings.toml")
        if not config["is_running"]:
            if past_of_set:
                RPC.close()  
                past_of_set = False
            time.sleep(0.1)
            continue
        if not past_of_set:
            past_of_set = True
        time.sleep(0.1)

        recent_track = get(url=f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={config["username"]}&api_key={config["api_key"]}&format=json')
        user_info = get(url=f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={config["username"]}&api_key={config["api_key"]}&format=json')
        recent_track = recent_track["recenttracks"]["track"][0]
        user_info = user_info["user"]
        if config["small_image_avatar"]:
            image = user_info["image"][1]["#text"]
        else:
            image = "https://i.imgur.com/EaBRPRJ.png"
            if "@attr" in recent_track:
                image = "https://i.imgur.com/ANd1OcZ.png"

        RPC.update(
        large_image=recent_track["image"][2]["#text"],
        large_text=f'{recent_track["name"]}',
        small_image=image,
        small_text=f'{config["username"]}',
        details=f'{recent_track["name"]}',
        state=f'By {recent_track["artist"]["#text"]}, on {recent_track["album"]["#text"]}',
        buttons=[{"label": config["button_text"].replace("{scrobbles}", user_info["playcount"]), "url": config["button_url"].replace("{profileurl}", f'https://www.last.fm/user/{config["username"]}')}])

        time.sleep(3)


def __del__():
    RPC.close()

main()