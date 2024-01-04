import os,shutil,zipfile
from subprocess import Popen
from time import sleep,time
from pyrogram import Client ,filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from main.utils import *
from main.display_progress import progress_bar
app = Client("amdl_bot",api_id=APP_ID,api_hash=API_HASH,bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start_command(client:Client, message):
    client.send_message(message.chat.id, text =f"Hello {message.from_user.first_name},\n I'm a Apple Music Downloder Bot!, you can send song/album/playlist URLs\n\nI can download from **de,gb,jp,us** regions ;)")


@app.on_message(lambda _, message: re.match(r'https://music\.apple\.com/[^/]+/(album|music-video|playlist)/+', message.text))
def main_processer(client: Client, message: Message):
    zipname = ""
    download_dir = ''
    try:
        msg = app.send_message(message.chat.id, "Processing")
        url = message.text
        cookies_path,cnty = get_cookies_path(url)
        zipname, artlink = art_name(url)
        if cookies_path != '':            
            chat_id = message.chat.id
            app.edit_message_text(chat_id=message.chat.id,message_id=msg.id, text=f"Downloading...!\n\nWith **{cnty2name(cnty)}** Region Account.")
            download_dir = f"downloads/{chat_id}"
            
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
                
            temp_dir = f"temps/{chat_id}"
            
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            Popen(['gamdl', '-c', cookies_path, '-f', download_dir, 
                '-t', temp_dir, '--config-location', './main/config.json', url]).wait()
            
            app.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text="Downloaded, Processing to send")
            music_files = []
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    if file.endswith(".m4v") or file.endswith(".m4a") or file.endswith(".png") or file.endswith(".jpg") or file.endswith(".lrc"):
                        filepath = os.path.join(root, file)
                        music_files.append(filepath)
                        
            if not music_files:
                app.edit_message_text(chat_id=message.chat.id, message_id=msg.id,
                    text="This is most likely give url in the bot account region, try again or ask **admin** to do so.")
                    
                shutil.rmtree(download_dir)
                shutil.rmtree(temp_dir)
                return
            c_time = time()
            app.edit_message_text(chat_id=message.chat.id,message_id=msg.id,text="Trying to send files")
            if any(f.endswith(".m4v") for f in music_files):
                for file in music_files:
                    fileN = os.path.basename(file) 
                    app.send_document(chat_id=message.chat.id,document=file,progress=progress_bar,progress_args=(fileN,msg,c_time))
            elif len(music_files) < 4:
                tot = len(music_files)
                for file in music_files:
                    fileN = os.path.basename(file)
                    try:
                        app.send_document(chat_id=message.chat.id,document=file,progress=progress_bar,progress_args=(fileN,msg,c_time))
                        sleep(2)
                    except FloodWait as e:
                        sleep(e.value)
                        app.send_document(chat_id=message.chat.id,document=file,progress=progress_bar,progress_args=(fileN,msg,c_time))
                        sleep(2)
            else:
                app.edit_message_text(chat_id=message.chat.id,message_id=msg.id,text="Zipping files to send")
                with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                    for filepath in music_files:
                        zipf.write(filepath, os.path.basename(filepath))
                sleep(1)
                fileN = os.path.basename(zipname)
                try: app.send_document(chat_id=message.chat.id,document=zipname,progress=progress_bar,progress_args=(fileN,msg,c_time))
                except FloodWait as e:
                        sleep(e.value)
                        app.send_document(chat_id=message.chat.id,document=zipname,progress=progress_bar,progress_args=(fileN,msg,c_time))
                os.remove(zipname)
            shutil.rmtree(download_dir)
            print("Sent successfully,Files sent and folder removed.",flush=True)
            app.delete_messages(chat_id=message.chat.id,message_ids=msg.id)
            app.send_message(chat_id=message.chat.id,reply_to_message_id=message.id, text="**Downloaded!**")
            print("Completed",flush=True)
        else:
            app.send_message(chat_id=message.chat.id, text="Invalid link")
    except Exception as e:
        app.send_message(chat_id=message.chat.id,text=f"Something went wrong like:\n{e}")
        if zipname or download_dir:
            if os.path.exists(zipname):
                os.remove(zipname)
            if os.path.exists(download_dir):  
                shutil.rmtree(download_dir)
print("AMDL bot started!", flush=True)
app.run()
