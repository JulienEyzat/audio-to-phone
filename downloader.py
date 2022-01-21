import argparse
import eyed3
import os
import youtube_dl

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", '--links', nargs='+', required=True, help='Links of the audio files')
    parser.add_argument("-d", "--dir", required=True, choices=["playlists", "podcasts"], help="Type of audio file")

    args = parser.parse_args()

    return args.links, args.dir

def init_folders(computer_playlist_directory, computer_podcast_directory):
    if not os.path.isdir(computer_playlist_directory):
        os.mkdir(computer_playlist_directory)
    
    if not os.path.isdir(computer_podcast_directory):
        os.mkdir(computer_podcast_directory)

def download_audio(links, output_directory):
    output_file_path = os.path.join("data", output_directory, "%(title)s.%(ext)s")

    ydl_opts = {
        "writethumbnail": True,
        'format': 'bestaudio/best',
        'outtmpl': output_file_path,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            },
            {
                'key': 'EmbedThumbnail'
            }
        ]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(links)

def update_metadata(podcasts_directory):
    for podcast in os.listdir(podcasts_directory):
        podcast_path = os.path.join(podcasts_directory, podcast)
        podcast_name = os.path.splitext(podcast)[0]
        audiofile = eyed3.load(podcast_path)
        if not audiofile.tag.album:
            audiofile.tag.album = podcast_name
            audiofile.tag.save()

if __name__ == "__main__":
    playlists_directory = os.path.join("data", "playlists")
    podcasts_directory = os.path.join("data", "podcasts")
    init_folders(playlists_directory, podcasts_directory)

    links, output_directory = parse_args()
    download_audio(links, output_directory)

    update_metadata(podcasts_directory)