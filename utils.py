import os
import pathlib
import bpy
import bpy.utils.previews # this is needed, otherwise it won't be available
import subprocess

def copy_to_clipboard(_txt):
    """Wow this function is high grade bullshit, can we do it better?"""
    txt = str(_txt)

    safe_text = txt.replace("\n", ' ') #traceback má v sobě \n, takže zatím je nrahzeno mezerou, ale lze použít tmp file
    print(safe_text)
    cmd = 'echo ' + safe_text.strip() +' | clip'#+ '|clip'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy to clipboard: {e}")

pigeon_collection = bpy.utils.previews.new()

def loadImages():
    pigeon_names = ["hello", "ok", "warn", "error", "crash", "brb"]
    image_format = ".png"
    relative_dir = pathlib.Path(os.path.dirname(__file__)) / "imgs"
    
    for pigeon in pigeon_names:
        pigoen_filename = f"{pigeon}{image_format}"
        pigeon_collection.load(pigeon.upper(), str(relative_dir/pigoen_filename), 'IMAGE')
    