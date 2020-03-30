# Tool 

### migrate_and_merge_json.py

Previously InstaStories used to save a json every day for every users processed based on the time of the execution. 
This was not great and created bugs in the metadata only options as it was relying on the media filename to handle duplicates. 

This tool convert from the old format to the new one:
A single json file for each user + a .txt file for quick indexing of already saved metadatas. 

Just run it and specify the media folder root as BASE_FOLDER in the script. 

```python3 migrate_and_merge_json.py```