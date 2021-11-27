import os
import shutil

import my_pymtp as pymtp

download_directory_name = "Download"
from_computer_folder_name = "FromComputer"
playlists_directory_name = "Playlists"
podcasts_directory_name = "Podcasts"

computer_data_directory = "data"

computer_src_playlist_directory = os.path.join(computer_data_directory, "playlist_not_phone")
computer_dst_playlist_directory = os.path.join(computer_data_directory, "playlist_phone")

computer_src_podcast_directory = os.path.join(computer_data_directory, "podcast_not_phone")
computer_dst_podcast_directory = os.path.join(computer_data_directory, "podcast_phone")


def init_mtp():
    mtp = pymtp.MTP()
    mtp.connect() # Opening session
    return mtp

def disconnect_mtp(mtp):
    mtp.disconnect()

def init_phone_folders(mtp):
    download_directory_id = mtp.get_folder_id(download_directory_name, 0)

    # Create the directory containing all data from the computer
    if not mtp.exists_folder(name=from_computer_folder_name, parent_directory_id=download_directory_id):
        mtp.create_folder(name=from_computer_folder_name, parent=download_directory_id)
    from_computer_directory_id = mtp.get_folder_id(from_computer_folder_name, download_directory_id)

    # Create the playlist directory
    if not mtp.exists_folder(name=playlists_directory_name, parent_directory_id=from_computer_directory_id):
        mtp.create_folder(name=playlists_directory_name, parent=from_computer_directory_id)
    playlists_directory_id = mtp.get_folder_id(playlists_directory_name, from_computer_directory_id)

    # Create the podcasts directory
    if not mtp.exists_folder(name=podcasts_directory_name, parent_directory_id=from_computer_directory_id):
        mtp.create_folder(name=podcasts_directory_name, parent=from_computer_directory_id)
    podcasts_directory_id = mtp.get_folder_id(podcasts_directory_name, from_computer_directory_id)
    
    return download_directory_id, from_computer_directory_id, playlists_directory_id, podcasts_directory_id

def copy_files_to_phone(mtp, computer_src_directory, computer_dst_directory, phone_directory_id):
    for to_copy_file in os.listdir(computer_src_directory):
        src_file_path = os.path.join(computer_src_directory, to_copy_file)
        # Copy files on phone
        mtp.send_file_from_file(src_file_path, to_copy_file, phone_directory_id)
        # Move files on second directory
        dst_file_path = os.path.join(computer_dst_directory, to_copy_file)
        shutil.move(src_file_path, dst_file_path)

def copy_playlist(mtp, playlists_directory_id):
    copy_files_to_phone(mtp, computer_src_playlist_directory, computer_dst_playlist_directory, playlists_directory_id)

def copy_podcasts(mtp, podcasts_directory_id):
    copy_files_to_phone(mtp, computer_src_podcast_directory, computer_dst_podcast_directory, podcasts_directory_id)

if __name__ == "__main__":
    # Init
    mtp = init_mtp()
    download_directory_id, from_computer_directory_id, playlists_directory_id, podcasts_directory_id = init_phone_folders(mtp)

    # Copy files
    copy_playlist(mtp, playlists_directory_id)
    copy_podcasts(mtp, podcasts_directory_id)

    # Disconnect
    disconnect_mtp(mtp)