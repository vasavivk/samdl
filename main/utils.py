import re,os
from datetime import datetime
from requests import get, post
from pycountry import countries as con
from pathlib import Path

BOT_TOKEN = "6450639403:AAEE169_oqYsjovDSY3Q56WADiqOB1HOz3o"
APP_ID='23028247'
API_HASH="659c5f1124a81ad789a6ea021da73f4d"


def get_cookies_path(url, cookies_folder="./cookies"):
    pattern = r"https://music\.apple\.com/([a-zA-Z]+)/"
    country_code = re.search(pattern, url)
    if country_code:
        country_code = country_code.group(1)
        for filename in os.listdir(cookies_folder):
            if re.match(r"([a-zA-Z]+)\.txt$", filename):
                file_country_code = re.match(
                    r"([a-zA-Z]+)\.txt$", filename).group(1)
                if file_country_code == country_code:
                    return os.path.join(cookies_folder, filename), country_code

    return os.path.join(cookies_folder, "us.txt"), "us"
 

def art_name(link):
    if 'playlist' in link:
        art = post("https://clients.dodoapps.io/playlist-precis/playlist-artwork.php",data = {'url': link}).json()['large']
        playlist_name = re.search(r'/playlist/([\w-]+)/', link).group(1) if re.search(r'/playlist/([\w-]+)/', link) else "Playlist"
        return playlist_name.replace('/','-') + " [Playlist][iTunes][aac].zip" ,art
    elif "music-video" in link:
        apple_rx = re.compile(r"apple\.com/(\w\w)/music-video/.+/(\d+)")
        region, id = apple_rx.search(link).groups()
        res = get(f"https://itunes.apple.com/lookup?id={id}&country={region}&lang=en_us").json()
        return res["results"][0]["trackName"].replace('/','-') + " [iTunes][m4v-aac].zip", res["results"][0]["artworkUrl100"].replace("100x100bb.jpg", "300x300bb.jpg")
    else:
        apple_rx = re.compile(r"apple\.com/(\w\w)/album/.+/(\d+)")
        region, id = apple_rx.search(link).groups()
        res = get(f"https://itunes.apple.com/lookup?id={id}&country={region}&lang=en_us").json()
        return res["results"][0]["collectionName"].replace('/','-') + " [iTunes][aac].zip", res["results"][0]["artworkUrl100"].replace("100x100bb.jpg", "300x300bb.jpg")
 
    
def cnty2name(country_code):
    country = con.get(alpha_2=country_code).name
    return country if country else "Country not found"


print(f"The cookies loaded." if os.path.exists('./cookies') else f"Cookies not loaded, please retry")
  
print("utils loaded", flush=True)