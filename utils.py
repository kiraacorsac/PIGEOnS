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