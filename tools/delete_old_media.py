import os
import shutil


def run(base_folder, delete_older_then, count_only_run):
    deleted_folder, deleted_media = 0, 0
    for username_folder in os.listdir(base_folder):
        username_folder_path = os.path.join(base_folder, username_folder)
        for date_folder in os.listdir(username_folder_path):
            date_folder_path = os.path.join(username_folder_path, date_folder)
            if not os.path.isdir(date_folder_path):
                continue
            if date_folder < delete_older_then:
                deleted_media += len(list(os.scandir(date_folder_path)))
                if not count_only_run:
                    shutil.rmtree(date_folder_path)
                deleted_folder += 1
    return deleted_folder, deleted_media


def main():
    BASE_FOLDER = "ig_media"
    DELETE_OLDER_THEN = "2020-10-31"

    deleted_folder, deleted_media = run(
        BASE_FOLDER, DELETE_OLDER_THEN, count_only_run=True)

    if (input(f"""We will delete folders older then {DELETE_OLDER_THEN} in {BASE_FOLDER}
                \nThat's {deleted_media} files in {deleted_folder} folders.
                \nDo you wish to proceed? [yes/NO]\n""").strip().lower() not in ["y", "yes"]):
        return

    deleted_folder, deleted_media = run(
        BASE_FOLDER, DELETE_OLDER_THEN, count_only_run=False)
    print(f"Deleted {deleted_folder} folders with {deleted_media} medias")


if __name__ == '__main__':
    main()
