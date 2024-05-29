import subprocess
def copy2clip(_txt):
    txt = str(_txt)

    safe_text = txt.replace("\n", ' ') #traceback má v sobě \n, takže zatím je nrahzeno mezerou, ale lze použít tmp file
    print(safe_text)
    cmd = 'echo ' + safe_text.strip() +' | clip'#+ '|clip'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy to clipboard: {e}")

import os
import bpy
import bpy.utils.previews
from bpy import data

from os import listdir
from os.path import isfile, join
custom_icons = None
list_raw = []
img = None
def loadImages():
    directory   = os.getcwd()+"/imgs/"
    
    onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]

    for f in onlyfiles:
        if f[-4:] == ".jpg":
            list_raw.append(f)
    print(list_raw)

    global custom_icons
    custom_icons = bpy.utils.previews.new()
    for filename in list_raw:
        custom_icons.load(filename[:-4], os.path.join(directory, filename), 'IMAGE')


    