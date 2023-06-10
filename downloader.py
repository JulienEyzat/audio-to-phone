# Internal libs
import argparse
import os
# External libs
import yt_dlp

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", '--title', default=None, help='Title of the music')
    parser.add_argument("-a", '--author', default=None, help='Author of the music')
    parser.add_argument("-l", '--links', nargs='+', required=True, help='Links of the audio files')
    parser.add_argument("-d", "--dir", required=True, choices=["playlists", "podcasts"], help="Type of audio file")

    args = parser.parse_args()

    return args.title, args.author, args.links, args.dir

def init_folders(computer_playlist_directory, computer_podcast_directory):
    if not os.path.isdir(computer_playlist_directory):
        os.mkdir(computer_playlist_directory)
    
    if not os.path.isdir(computer_podcast_directory):
        os.mkdir(computer_podcast_directory)

def download_audio(links, title, author, output_directory):
    if title and author:
        base_name = f"{title} - {author}"
    else:
        base_name = "%(title)s"
    output_file_path = os.path.join("data", output_directory, f"{base_name}.%(ext)s")

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
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(links)
        ydl.download(links)

def main(title, author, links, output_directory):
    playlists_directory = os.path.join("data", "playlists")
    podcasts_directory = os.path.join("data", "podcasts")
    init_folders(playlists_directory, podcasts_directory)

    download_audio(links, title, author, output_directory)

if __name__ == "__main__":
    title, author, links, output_directory = parse_args()
    main(title, author, links, output_directory)