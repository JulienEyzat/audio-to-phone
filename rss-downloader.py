# Internal libs
import datetime
import json
import os
import time
import unicodedata
# External libs
import feedparser
import requests
import tqdm

DATES_FILE_PATH = "already_dl.json"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_lim_dates():
    if not os.path.isfile(DATES_FILE_PATH):
        begin_date = datetime.datetime.now()
        end_date = datetime.datetime.now()
    else:
        with open(DATES_FILE_PATH) as f:
            lim_dates = json.load(f)
        begin_date = datetime.datetime.strptime(lim_dates["begin_date"], DATETIME_FORMAT)
        end_date = datetime.datetime.strptime(lim_dates["end_date"], DATETIME_FORMAT)
    return begin_date, end_date

def get_thinkerview_infos():
    thinkerview_infos = []
    feed = feedparser.parse("https://www.thinkerview.com/feed/")
    for entry in feed.entries:
        if entry["author"] != "veilleur":
            title = entry["link"].replace("https://www.thinkerview.com/", "").replace("/", "")
            interview_id = entry["id"].replace("https://www.thinkerview.com/?p=", "")
            link = f"https://www.thinkerview.com/podcast-download/{interview_id}/{title}.mp3?ref=download"
            date = datetime.datetime.fromtimestamp(time.mktime(entry["published_parsed"]))
            thinkerview_info = {
                "title": title,
                "link": link,
                "date": date
            }
            thinkerview_infos.append(thinkerview_info)
    return thinkerview_infos

def filter_sort_infos(thinkerview_infos, begin_date, end_date, n_last):
    # Filter by dates
    thinkerview_infos = [ info for info in thinkerview_infos if info["date"] < begin_date or end_date < info["date"] ]
    # Sort by dates
    thinkerview_infos.sort(key=lambda info:info['date'], reverse=True)
    # Get n last
    thinkerview_infos = thinkerview_infos[:n_last]
    return thinkerview_infos

def download(thinkerview_infos, output_directory):
    for info in thinkerview_infos:
        print(info["title"])
        output_path = os.path.join(output_directory, f"{info['title']}.mp3")
        requests_downloader(info["link"], output_path)

def requests_downloader(link, output_path):
    file_stream = requests.get(link, stream=True)
    total_size = int(file_stream.headers.get('content-length', 0)) # Total size in bytes.
    block_size = 1024 #1 Kibibyte
    with tqdm.tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
        with open(output_path, 'wb') as file:
            for data in file_stream.iter_content(block_size):
                pbar.update(len(data))
                file.write(data)

def update_dates(old_begin_date, old_end_date, thinkerview_infos):
    # Get date to write
    new_begin_date = thinkerview_infos[0]["date"]
    new_end_date = thinkerview_infos[-1]["date"]
    if old_begin_date > new_begin_date:
        kept_begin_date = new_begin_date
    else:
        kept_begin_date = old_begin_date
    if old_end_date < new_end_date:
        kept_end_date = new_end_date
    else:
        kept_end_date = old_end_date
    # Write dates
    kept_dates = {
        "begin_date": kept_begin_date.strftime(DATETIME_FORMAT),
        "end_date": kept_end_date.strftime(DATETIME_FORMAT)
    }
    with open(DATES_FILE_PATH, 'w') as f:
        json.dump(kept_dates, f)
    
def main():
    # Get thinkerview infos from rss feed
    thinkerview_infos = get_thinkerview_infos()
    # Get previous lim dates
    begin_date, end_date = get_lim_dates()
    # Filter podcasts with dates
    thinkerview_infos = filter_sort_infos(thinkerview_infos, begin_date, end_date, n_last=5)
    # Download
    output_directory = os.path.join("data", "podcasts")
    download(thinkerview_infos, output_directory)
    # Update lim dates
    update_dates(begin_date, end_date, thinkerview_infos)

if __name__ == "__main__":
    main()
