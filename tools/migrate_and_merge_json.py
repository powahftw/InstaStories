import os, json

def get_story_id(metadata):
    return metadata["id"]

def convert_metadata_file(fake_json):
    opening_parenthesis = 0
    stories = []
    json_buffer = ""
    for c in fake_json:
        if c == "{": opening_parenthesis += 1
        if c == "}": opening_parenthesis -= 1
        json_buffer += c
        if opening_parenthesis == 0: # Top level, well parenthesized json.
            stories.append(json_buffer)
            json_buffer = ""
    return [json.loads(chunk) for chunk in stories                                                                ]  

def convert_user_json(username_folder_path):
    stories_json, stories_id = [], []
    for date_folder in os.listdir(username_folder_path):
        date_folder_path = os.path.join(username_folder_path, date_folder)
        if not os.path.isdir(date_folder_path): continue # Skip non-folder files at this level
        for file_name in os.listdir(date_folder_path):
            _, extension = os.path.splitext(file_name)
            if extension != ".json": continue
            with open(os.path.join(date_folder_path, file_name), 'r') as f:
                metadatas = convert_metadata_file(f.read())
                stories_json.extend(metadatas)
                stories_id.extend([get_story_id(story) for story in metadatas])
            #TODO Delete Json file. 
    with open(os.path.join(username_folder_path, "saved.txt"), "w") as f:
          for id in stories_id:
            f.write(f"{id}\n")
    username = os.path.basename(username_folder_path)
    with open(os.path.join(username_folder_path, f"{username}.json"), "w") as f:
        json.dump(stories_json, f)

if __name__ == '__main__':
    BASE_FOLDER =  "ig_media"
    for username_folder in os.listdir(BASE_FOLDER):
        username_folder_path = os.path.join(BASE_FOLDER, username_folder)
        convert_user_json(username_folder_path)
