import multiprocessing.dummy
import sys
import warnings
from pathlib import Path

import pandas as pd
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL

warnings.filterwarnings('ignore')
# raw = False
# part = False
download_videos = True

NUMS = 100  # maximal items you can download
iMaxDuration = 1200  # maximal duration in seconds
iMinDuration  = 0
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
}
YDL_OPTIONS_EXTRACT = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    "extractor-args":"youtube:player-client=web",
    #"age-limit":12,
}


YDL_OPTIONS_AUDIO_ONLY = {
    'format': 'bestaudio[ext=m4a]',
}


def search(arg, nums):

    with YoutubeDL(YDL_OPTIONS_EXTRACT) as ydl:
        videos=None
        tag=True
        while tag:
            try:
                # print("nums",nums)
                videos = ydl.extract_info(f"ytsearch{nums}:{arg}", download=False)['entries']
                tag = False
            except:

                if nums >6:
                    nums -= 5
                elif nums <=5:
                    nums-=2
                if nums<1:
                    return "network link failed"
    return videos


def download(index):
    print("index", index)
    arg, title, folder, action, name = download_information[index]

    path = Path(folder) / 'videos'
    path.mkdir(exist_ok=True, parents=True)

    YDL_OPTIONS['outtmpl'] = str(path / (arg + ".mp4"))
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
            YDL_OPTIONS_AUDIO_ONLY['outtmpl'] = str(path / ( arg + ".m4a"))
            with YoutubeDL(YDL_OPTIONS_AUDIO_ONLY) as ydl_audio:
                audio = ydl_audio.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=True)
                return True
        except Exception:
            video = ydl.extract_info("https://www.youtube.com/watch?v={}".format(arg), download=False)
            return False

def filter(arg):
    try:
        if arg["duration"] > iMaxDuration:
            return None
        if arg["duration"] < iMinDuration:
            return None
        else:
            return arg
    except Exception:
        return None


def mut_download(folder, animals):
    download_information = []
    dir_name = 'b'
    dir_name2 = 'a'
    ll = []
    for animal in animals.split("/"):
        
        rm_animal = animal
        dir_name = animal.replace(' ','')
        args = f"{animal}"
        print(args)
        retry = 0
        while True:
            try:
                video_infos = search(args, NUMS)
                for info in video_infos:
                    video = filter(info)
                    try:
                        title = info['title']
                    except Exception:
                        continue
                    if video is None:
                        continue
                    
            
                    times = info['duration']
                    url = info['requested_formats'][0]['url']
                    id = info['id']
                    size = info['requested_formats'][0]['filesize']
                    title = info['title']
                    format_note = info['requested_formats'][0]['format_note']
                    ll.append([ id,times, size, title, format_note])
                    download_information.append([info["id"], info["title"], folder, dir_name2, dir_name])
                break
            except Exception:
                retry += 1
                if retry > 10:
                    break

        path = Path(folder) 
        path.mkdir(exist_ok=True, parents=True)
        
        print("the number o f download inforamtion", len(download_information))

    file_name = path / f'{path}.csv'
    df1 = pd.DataFrame(ll, columns=['id', 'time', 'file_size', 'title', 'Clarity'])
    df1.to_csv(file_name,encoding='utf-8')
    return download_information


CPU = 1
filename = './qingguangyan.xlsx'
thyroidData=pd.read_excel(filename,sheet_name="Sheet1")
for index,item in thyroidData.iterrows():
    animal_name = item[0]
    folder = animal_name.split('/')[0].replace(' ','')
    # print(folder)
    download_information = mut_download(folder, animal_name)

    print(download_information)
    num_videos = len(download_information)
    video_index = [i for i in range(0, num_videos)]
    print(video_index)
    print("the number of videos", num_videos)

    if download_videos:
        with multiprocessing.dummy.Pool(CPU) as pool:       
            pool.map(download, video_index)



