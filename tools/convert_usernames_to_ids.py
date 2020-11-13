import os
import json
from collections import defaultdict
import shutil


def get_user_id_and_nickname(username_folder_path):

    username = os.path.basename(username_folder_path)
    json_file = os.path.join(username_folder_path, f"{username}.json")

    if not os.path.exists(json_file):
        return None, None

    with open(json_file, 'r') as f:
        user_file = json.load(f)
        for story in user_file:
            if 'user' in story and 'pk' in story['user'] and 'username' in story['user']:
                return [str(story['user']['pk']), story['user']['username']]
        raise ValueError('No ID/Nickname Found')


def create_id_folder_mapping(base_folder):
    id_to_path_mapping = defaultdict(list)
    for username_folder in os.listdir(base_folder):
        username_folder_path = os.path.join(base_folder, username_folder)
        user_id, _ = get_user_id_and_nickname(username_folder_path)
        if user_id:
            id_to_path_mapping[user_id].append(username_folder_path)
    return id_to_path_mapping


def move_all_subfolders(source, destination):
    for file in os.listdir(source):
        source_path = os.path.join(source, file)
        destination_path = os.path.join(destination, file)
        if os.path.isfile(source_path):
            continue
        elif not os.path.exists(destination_path):
            shutil.move(source_path, destination_path)
        else:
            # If the date folder already exists then just move the subfiles, avoid duplicate files by checking the id.
            for source_file in os.listdir(source_path):
                source_file_path = os.path.join(source_path, source_file)
                destination_file_path = os.path.join(
                    destination_path, source_file)
                if os.path.exists(destination_file_path):
                    continue
                shutil.move(source_file_path, destination_file_path)


def rename_existing_files_and_folder(username_folder_path, username, id_folder_path, user_id):
    nickname_json_file_name = f"{username}.json"
    id_json_file_name = f"{user_id}.json"
    os.rename(username_folder_path, id_folder_path)
    os.rename(os.path.join(id_folder_path, nickname_json_file_name),
              os.path.join(id_folder_path, id_json_file_name))


def create_and_merge_files_in_new_folder(username_folder_paths, id_folder_path, user_id):

    if not (os.path.isdir(id_folder_path)):
        # Create the id based directory if it's missing
        os.mkdir(id_folder_path)

    saved_files = set()
    json_files = []
    json_files_seen = set()

    for username_folder_path in username_folder_paths:

        saved_file_path = os.path.join(username_folder_path, "saved.txt")
        if os.path.isfile(saved_file_path):
            with open(saved_file_path, 'r') as f:
                for line in f.read().splitlines():
                    saved_files.add(line)

        username = os.path.basename(username_folder_path)
        json_file_path = os.path.join(
            username_folder_path, f"{username}.json")

        if os.path.isfile(json_file_path):
            with open(json_file_path, 'r') as f:
                json_stories = json.load(f)
                for json_story in json_stories:
                    story_id = json_story['id']
                    if story_id in json_files_seen:
                        continue
                    json_files_seen.add(story_id)
                    json_files.append(json_story)

    with open(os.path.join(id_folder_path, "saved.txt"), "w") as f:
        for saved_file in sorted(list(saved_files)):
            f.write(f"{saved_file.strip()}\n")

    with open(os.path.join(id_folder_path, f"{user_id}.json"), "w") as f:
        json.dump(json_files, f)

    for username_folder_path in username_folder_paths:

        try:
            move_all_subfolders(username_folder_path, id_folder_path)
            shutil.rmtree(username_folder_path)
        except Exception as e:
            print(f"Error while processing {username_folder_path}")
            print(e)

    return username


def extract_and_update_id_to_nickname_mapping(ids_to_nickname_path, base_folder_path):
    ids_to_names_file = {}
    if os.path.exists(ids_to_nickname_path):
        with open(ids_to_nickname_path, 'r') as f:
            ids_to_names_file = json.load(f)

    for id_folder in os.listdir(base_folder_path):
        id_folder_path = os.path.join(base_folder_path, id_folder)
        user_id, nickname = get_user_id_and_nickname(id_folder_path)
        if user_id and nickname:
            ids_to_names_file[user_id] = nickname

    # Save the ids_to_names mapping file.
    with open(ids_to_nickname_path, 'w') as f:
        json.dump(ids_to_names_file, f)


if __name__ == '__main__':
    BASE_FOLDER = "ig_media"
    IDS_TO_NICKNAME_PATH = 'ids_to_nick.json'

    id_to_path_mapping = create_id_folder_mapping(BASE_FOLDER)

    for user_id, username_folder_paths in id_to_path_mapping.items():

        id_folder_path = os.path.join(BASE_FOLDER, user_id)

        # If the user only had a single nickname it's cheaper to rename the directory and the .json file.
        if len(username_folder_paths) == 1:
            username_folder_path = username_folder_paths[0]
            username = os.path.basename(username_folder_path)
            rename_existing_files_and_folder(
                username_folder_path, username, id_folder_path, user_id)
        else:
            create_and_merge_files_in_new_folder(
                username_folder_paths, id_folder_path, user_id)

    extract_and_update_id_to_nickname_mapping(
        IDS_TO_NICKNAME_PATH, BASE_FOLDER)
