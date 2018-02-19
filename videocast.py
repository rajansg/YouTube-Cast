import pychromecast
import pytube
import google_search
import socket
import os
import SimpleHTTPServer
import SocketServer
import threading

def webserver(server_ip,server_port,server_root_dir):
    server_port = int(server_port)
    os.chdir(server_root_dir)

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(('',server_port),Handler)

    httpd.handle_request()

def cast_video(video_to_search,server_ip='',server_port=''):
    global start
    if server_ip == '':
        server_ip = socket.gethostbyname(socket.gethostname())

    if server_port == '':
        server_port = '80'

    server_root_dir = os.path.join(os.getcwd(),'cast')
    if not os.path.exists(server_root_dir):
        os.makedirs(server_root_dir)

    try:
        threading.Thread(target=webserver,args=(server_ip,server_port,server_root_dir,)).start()
    except:
        pass
    
    video_name = ''
    index = 1
    while video_name == '' and index < 20:
        video = google_search.search(video_to_search,'video',no_of_results=index)
        if '- YouTube' in video.keys()[-1] and 'watch?' in video.values()[-1]:
            video_name = video.keys()[-1]
            video_url = video.values()[-1]
        else:
            index += 1

    video_name = pytube.helpers.safe_filename(video_name, max_length=255)

    try:
        if not os.path.exists(os.path.join(server_root_dir,video_name+'.mp4')):
            yt = pytube.YouTube(video_url)
            yt.streams.filter(subtype='mp4').first().download(server_root_dir,filename=video_name)
    except:
        return None
        

    try:
        cast = pychromecast.get_chromecasts()[0]
        mc = cast.media_controller
        cast_url = 'http://'+server_ip+':'+server_port+'/'+video_name+'.mp4'
        mc.play_media(cast_url,'video/mp4')
        mc.block_until_active()
    except:
        return None

#cast_video('family guy first episode')
