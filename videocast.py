import time
import google_search
import socket
import os
import threading
import pychromecast
import pytube
import SimpleHTTPServer
import SocketServer

def create_dir(dir_name):
    try:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    except:
        pass
    

def host_server(hosting_port,server_root_dir):
    global server_port
    create_dir(server_root_dir)

    try:
        server_port = int(hosting_port)
        os.chdir(server_root_dir)

        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        httpd = SocketServer.TCPServer(('',server_port),Handler)
        server_port = str(httpd.server_address[1])
        httpd.handle_request()
        return True
    except:
        return False

def download_youtube_video(video_to_search,dest_folder=os.path.join(os.path.split(os.path.realpath(__file__))[0],'Videos')):
    create_dir(dest_folder)

    video_name = ''
    index = 1
    while video_name == '' and index < 20:
        video = google_search.search(video_to_search,'video',no_of_results=index)

        if '- YouTube' in video.keys()[-1] and 'watch?' in video.values()[-1]:
            video_name = pytube.helpers.safe_filename(video.keys()[-1], max_length=255)
            video_url = video.values()[-1]

            if not os.path.exists(os.path.join(dest_folder,video_name+'.mp4')):
                try:
                    yt = pytube.YouTube(video_url)
                    yt.streams.filter(subtype='mp4').first().download(dest_folder,filename=video_name)
                    return video_name+'.mp4'
                except:
                    index += 1
                    video_name = ''
            else:
                return video_name+'.mp4'
        else:
            index += 1
 
    return False

def get_cc(cc_name=''):
    if cc_name == '':
        try:
            return pychromecast.get_chromecasts()[0]
        except:
            return None
    else:
        for cc in pychromecast.get_chromecasts():
            if cc.device.friendly_name == cc_name:
                return cc

    return None

def send_to_chromecast(cast_url,cc_name=''):
    global mc
    cast = get_cc(cc_name)

    if cast is not None:
        mc = cast.media_controller
        mc.play_media(cast_url,'video/mp4')
        mc.block_until_active()
        return True
    else:
        return False

def pause_cast_video():
    global mc
    try:
        mc.pause()
        return True
    except:
        return False

def play_cast_video():
    global mc
    try:
        mc.play()
        return True
    except:
        return False

def cast_video(video_to_search,cc_name=''):
    if get_cc(cc_name) is None:
        return False
    else:
        global server_port
        server_host = socket.gethostbyname(socket.gethostname())
        server_port = 0
        server_root_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0],'cast')
       
        threading.Thread(target=host_server,args=(server_port,server_root_dir,)).start()
       
        video_name = download_youtube_video(video_to_search,server_root_dir)

        if video_name is not False:
            cast_url = 'http://'+server_host+':'+server_port+'/'+video_name
            send_to_chromecast(cast_url,cc_name)
            return True
        else:
            return False


'''
cast_video('family guy unaired pilot')
time.sleep(20)
pause_cast_video()
time.sleep(20)
play_cast_video()

'''
