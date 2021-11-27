import argparse
import os
import youtube_dl

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", '--links', nargs='+', required=True, help='Links of the audio files')
    parser.add_argument("-d", "--dir", required=True, choices=["playlist", "podcast"], help="Type of audio file")

    args = parser.parse_args()

    return args.links, args.dir

def download_audio(links, output_directory):
    output_file_path = os.path.join("data", "%s_not_phone" %(output_directory), "%(title)s.%(ext)s")

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
        ydl.download(args.links)

if __name__ == "__main__":
    links, output_directory = parse_args()
    download_audio(links, output_directory)