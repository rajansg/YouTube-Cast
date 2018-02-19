import pychromecast
import pytube
import google_search
import socket
import os
import SimpleHTTPServer
import SocketServer
import threading

def webserver(server_ip,server_port,server_root_dir):
    try:
        server_port = int(server_port)
        os.chdir(server_root_dir)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        httpd = SocketServer.TCPServer(('',server_port),Handler)

        httpd.handle_request()
    except:
        return False

    return True

def get_video(video_to_search):
    global server_root_dir
    global video_name
    global video_url
    
    video_name = ''
    index = 1
    while video_name == '' and index < 20:
        video = google_search.search(video_to_search,'video',no_of_results=index)
        if '- YouTube' in video.keys()[-1] and 'watch?' in video.values()[-1]:
            video_name = video.keys()[-1]
            video_url = video.values()[-1]
            return True
        else:
            index += 1

    return False

def download_video():
    global server_root_dir
    global video_name
    global video_url

    try:
        yt = pytube.YouTube(video_url)
        yt.streams.filter(subtype='mp4').first().download(server_root_dir,filename=video_name)
    except:
        return False

    return True

def send_to_chromecast(cast_url):
    try:
        cast = pychromecast.get_chromecasts()[0]
        mc = cast.media_controller
        mc.play_media(cast_url,'video/mp4')
        mc.block_until_active()
    except:
        return False

def cast_video(video_to_search,server_ip='',server_port=''):
    global server_root_dir
    global video_name
    global video_url
    
    if server_ip == '':
        server_ip = socket.gethostbyname(socket.gethostname())

    if server_port == '':
        server_port = '55555'

    server_root_dir = os.path.join(os.getcwd(),'cast')
    if not os.path.exists(server_root_dir):
        os.makedirs(server_root_dir)

    threading.Thread(target=webserver,args=(server_ip,server_port,server_root_dir,)).start()

    if get_video(video_to_search):
        video_name = pytube.helpers.safe_filename(video_name, max_length=255)

        if not os.path.exists(os.path.join(server_root_dir,video_name+'.mp4')):
            downloaded = download_video()
        else:
            downloaded = True

        if downloaded:
            cast_url = 'http://'+server_ip+':'+server_port+'/'+video_name+'.mp4'
            send_to_chromecast(cast_url)
        else:
            return False
    else:
        return False

    return True

#cast_video('family guy first episode')
