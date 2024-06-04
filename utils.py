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
from bpy.app.handlers import persistent
from bpy import data

from os import listdir
from os.path import isfile, join
custom_icons = None
list_raw = []
img = None
@persistent
def loadImages():
    directory   = os.getcwd()+"/imgs/"
    
    loadAndSetTexture(directory+"artpigeon_001.webp",'helloPigeon')
    loadAndSetTexture(directory+"artpigeon_004.webp",'okPigeon')
    loadAndSetTexture(directory+"artpigeon_007.webp",'warningPigeon')
    loadAndSetTexture(directory+"artpigeon_005.webp",'errorPigeon')
    loadAndSetTexture(directory+"artpigeon_014.webp",'crashPigeon')
    loadAndSetTexture(directory+"artpigeon_017.webp",'brbPigeon')
    bpy.context.scene["updater"] = True



def loadAndSetTexture(path,textureName):
    img = bpy.data.images.load(path)

    texture = bpy.data.textures.new(name=textureName, type="IMAGE")
    texture.image = img
    tex = bpy.data.textures[textureName]
    tex.extension = 'REPEAT'