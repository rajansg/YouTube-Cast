import pychromecast
import pytube
import google_search
import socket
import os

def cast_video(video_to_search,server_root_folder,server_ip='',server_port=''):
    if server_ip == '':
        server_ip = socket.gethostbyname(socket.gethostname())

    if server_port == '':
        server_port = '80'
        
    video_name = ''
    while video_name == '':
        try:
            video = google_search.search(video_to_search+' Youtube','video',no_of_results=1)
            video_name = video.keys()[-1].split('- YouTube')[0].strip()+'.mp4'
            video_url = video.values()[-1]
        except:
            pass

    if os.name == 'nt':
        path_separator = '\\'
    else:
        path_separator = '/'

    full_path = server_root_folder+path_separator+video_name
        
    if not os.path.exists(full_path):
        try:
            yt = pytube.YouTube(video_url)
            print 'Downloading...'
            yt.streams.filter(subtype='mp4').first().download(server_root_folder)
        except:
            print 'There was a problem fetching the video. Please try another one. Sorry..'

    cast = pychromecast.get_chromecasts()[0]
                
    mc = cast.media_controller
    cast_url = 'http://'+server_ip+':'+server_port+''+full_path.replace(server_root_folder,'').replace(path_separator,'/')
    mc.play_media(cast_url,'video/mp4')
    mc.block_until_active()

#cast_video('google chromecast','C:\\xampp\\htdocs\\CastVideo')
