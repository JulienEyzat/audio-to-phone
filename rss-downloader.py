import feedparser
import requests
import tqdm
import datetime
import json
import os
import eyed3

def get_lim_dates():
    with open("already_dl.json") as f:
        lim_dates = json.load(f)
    begin_date = datetime.datetime.strptime(lim_dates["begin_date"], "%Y-%m-%d %H:%M:%S%z")
    end_date = datetime.datetime.strptime(lim_dates["end_date"], "%Y-%m-%d %H:%M:%S%z")
    return begin_date, end_date

def get_titles():
    feed = feedparser.parse("https://www.thinkerview.com/feed/")

    titles = []
    dates = []
    for entry in feed.entries:
        categories = [ entry.tags[i].term for i in range(len(entry.tags)) ]
        if "Veille" not in categories:
            titles.append(entry.title)
            # Thu, 04 Jul 2013 17:11:48 +0000
            date = datetime.datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            dates.append(date)
    
    dates, titles = zip(*sorted(zip(dates, titles), reverse=True))
    return titles, dates

def get_recent_titles(begin_date, end_date, titles, dates, title_number):
    filtered_titles = []
    filtered_dates = []
    begin_or_end_dates = []
    for title, date in zip(titles, dates):
        if len(filtered_titles) < 5:
            if date > end_date or date < begin_date:
                filtered_titles.append(title)
                filtered_dates.append(date)
                if date > end_date:
                    begin_or_end_dates.append("end")
                else:
                    begin_or_end_dates.append("begin")
    return filtered_titles, filtered_dates, begin_or_end_dates

def get_download_link(title):
    feed = feedparser.parse("https://www.thinkerview.com/feed/")

    download_link = None
    for entry in feed.entries:
        categories = [ entry.tags[i].term for i in range(len(entry.tags)) ]
        if "Veille" not in categories:
            if entry.title == title:
                interview_id = entry.guid.split("p=")[1]
                interview_name = entry.link.replace("https://www.thinkerview.com/", "").replace("/", "")
                download_link = "https://www.thinkerview.com/podcast-download/%s/%s.mp3?ref=download" %(interview_id, interview_name)

    return download_link

def requests_downloader(audio_link, output_directory):
    audio = requests.get(audio_link, stream=True)
    # Total size in bytes.
    filename = audio.headers.get("content-disposition", 0).replace("attachment; filename=\"", "").replace("\";", "")
    output_file = os.path.join(podcasts_directory, filename)
    total_size = int(audio.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    t=tqdm.tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(output_file, 'wb') as file:
        for data in audio.iter_content(block_size):
            t.update(len(data))
            file.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print("ERROR, something went wrong")

def update_json(begin_date, end_date, date, begin_or_end_date):
    new_json = {}
    begin_date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S%z")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S%z")
    date_str = date.strftime("%Y-%m-%d %H:%M:%S%z")

    if begin_or_end_date == "begin":
        new_json["begin_date"] = date_str
        new_json["end_date"] = end_date_str
    else:
        new_json["begin_date"] = begin_date_str
        new_json["end_date"] = date_str
    
    with open('already_dl.json', 'w') as f:
        json.dump(new_json, f)

def update_metadata(podcasts_directory):
    for podcast in os.listdir(podcasts_directory):
        podcast_path = os.path.join(podcasts_directory, podcast)
        podcast_name = os.path.splitext(podcast)[0]
        audiofile = eyed3.load(podcast_path)
        print(audiofile)
        if audiofile:
            if not audiofile.tag.album:
                audiofile.tag.album = podcast_name
                audiofile.tag.save()


if __name__ == "__main__":
    podcasts_directory = os.path.join("data", "podcasts")
    begin_date, end_date = get_lim_dates()
    titles, dates = get_titles()
    filtered_titles, filtered_dates, begin_or_end_dates = get_recent_titles(begin_date, end_date, titles, dates, 5)
    for title, date, begin_or_end_date in zip(filtered_titles, filtered_dates, begin_or_end_dates):
        print(title, date)
        audio_link = get_download_link(title)
        requests_downloader(audio_link, podcasts_directory)
        update_json(begin_date, end_date, date, begin_or_end_date)
    
    update_metadata(podcasts_directory)