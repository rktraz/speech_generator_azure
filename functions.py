import re
from pathlib import Path


def get_voice_name(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        pattern = r"\"ShortName\":\"([^\"]+)\""
        match = re.search(pattern, file_content)
        if match:
            voice_name = match.group(1)
            voice_name = voice_name.split("-")[-1]
            return voice_name
        else:
            raise Exception
        
        
def generate_voice_configurations(base_folder):
    voice_configurations = {}

    base_path = Path(base_folder)
    subfolders = [subfolder for subfolder in base_path.iterdir() if subfolder.is_dir()]

    for subfolder in subfolders:
        voice_configurations[subfolder.name] = {}

        files = [file for file in subfolder.glob("*.txt") if file.is_file()]

        for file in files:
            voice_name = get_voice_name(str(file))
            voice_configurations[subfolder.name][voice_name] = file

    return voice_configurations


def modify_ssml(ssml_string, new_text):
    pattern1 = r"<prosody([^>]*)>.*?<\/prosody>"
    pattern2 = r"<mstts:express-as([^>]*)>.*?<\/mstts:express-as>"
    pattern3 = r"<s />.*?<s />"
    pattern4 = r"<voice([^>]*)>.*?</voice>"

    match1 = re.search(pattern1, ssml_string)
    match2 = re.search(pattern2, ssml_string)
    match3 = re.search(pattern3, ssml_string)
    match4 = re.search(pattern4, ssml_string)
    if match1: 
        return re.sub(pattern1, f"<prosody\\1>{new_text}</prosody>", ssml_string)
    elif match2:
        return re.sub(pattern2, f"<mstts:express-as\\1>{new_text}</mstts:express-as>", ssml_string)
    elif match3:
        return re.sub(pattern3, f"<s />{new_text}<s />", ssml_string)
    elif match4:
        return re.sub(pattern4, f"<voice\\1>{new_text}</voice>", ssml_string)
