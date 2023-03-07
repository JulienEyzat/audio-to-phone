import os
import shutil
import tqdm

import my_pymtp as pymtp

def init_mtp():
    mtp = pymtp.MTP()
    mtp.connect() # Opening session
    mtp.create_files_tree()
    return mtp

def disconnect_mtp(mtp):
    mtp.disconnect()

def init_phone_folders(mtp, phone_base_path, phone_playlists_directory_path, phone_podcasts_directory_path):
    # Create the directory containing all data from the computer
    if not mtp.exists_folder(folder_path=phone_base_path):
        mtp.create_folder(folder_path=phone_base_path)

    # Create the playlist directory
    if not mtp.exists_folder(folder_path=phone_playlists_directory_path):
        mtp.create_folder(folder_path=phone_playlists_directory_path)

    # Create the podcasts directory
    if not mtp.exists_folder(folder_path=phone_podcasts_directory_path):
        mtp.create_folder(folder_path=phone_podcasts_directory_path)

def copy_files_to_phone(mtp, computer_directory, phone_directory, do_delete=True):
    # # Get files
    # computer_files = set(os.listdir(computer_directory))
    # phone_files = set(list(mtp.listdir(phone_directory)))
    # delete_files = phone_files - computer_files
    # copy_files = computer_files - phone_files

    # # Delete files in the phone directory that are not in the computer directory
    # if do_delete:
    #     for file_name in tqdm.tqdm(delete_files, desc="Deleting"):
    #         phone_file_path = os.path.join(phone_directory, file_name)
    #         mtp.delete_file(phone_file_path)
    
    # # Copy
    # for file_name in tqdm.tqdm(copy_files, desc="Copying"):
    #     computer_file_path = os.path.join(computer_directory, file_name)
    #     phone_file_path = os.path.join(phone_directory, file_name)
    #     mtp.copy_file_from_file(computer_file_path, phone_file_path)

    # Copy
    for to_copy_file in tqdm.tqdm(os.listdir(computer_directory)):
        # Paths
        computer_file_path = os.path.join(computer_directory, to_copy_file)
        phone_file_path = os.path.join(phone_directory, to_copy_file)
        # Copy files on phone
        if not mtp.exists_file(phone_file_path):
            mtp.copy_file_from_file(computer_file_path, phone_file_path)

    # Delete files in the phone directory that are not in the computer directory
    # To fix
    if do_delete:
        computer_files = os.listdir(computer_directory)
        for phone_file_name in mtp.listdir(phone_directory):
            if phone_file_name not in computer_files:
                phone_file_path = os.path.join(phone_directory, phone_file_name)
                mtp.delete_file(phone_file_path)


if __name__ == "__main__":
    # Init variables
    phone_base_path = os.path.join("Download", "FromComputer")
    phone_playlists_directory_path = os.path.join(phone_base_path, "Playlists")
    phone_podcasts_directory_path = os.path.join(phone_base_path, "Podcasts")
    computer_data_directory = "data"
    computer_playlist_directory = os.path.join(computer_data_directory, "playlists")
    computer_podcast_directory = os.path.join(computer_data_directory, "podcasts")

    # Init
    mtp = init_mtp()
    init_phone_folders(mtp, phone_base_path, phone_playlists_directory_path, phone_podcasts_directory_path)

    # Copy files
    copy_files_to_phone(mtp, computer_playlist_directory, phone_playlists_directory_path, do_delete=False)
    copy_files_to_phone(mtp, computer_podcast_directory, phone_podcasts_directory_path)

    # Disconnect
    disconnect_mtp(mtp)