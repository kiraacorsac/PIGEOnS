import os
import pathlib
import bpy
import bpy.utils.previews  # this is needed, otherwise previews won't be available via bpy
import subprocess

import tempfile
import subprocess

import functools
import time


def copy_to_clipboard(string: str) -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(string.encode())
        tmp.close()
        cmd = "type " + tmp.name + "|clip"
        subprocess.check_call(cmd, shell=True)


# this is not very util, let's move this to another file
pigeon_collection = bpy.utils.previews.new()


def loadImages():
    pigeon_collection.clear()
    pigeon_names = ["hello", "ok", "warning", "error", "crash", "brb"]
    image_format = ".png"
    relative_dir = pathlib.Path(os.path.dirname(__file__)) / "imgs"

    for pigeon in pigeon_names:
        pigoen_filename = f"{pigeon}{image_format}"
        pigeon_collection.load(
            pigeon.upper(), str(relative_dir / pigoen_filename), "IMAGE"
        )


def filter_used_datablocks(datablocks: list[bpy.types.ID]):
    return list(
        filter(lambda d: d.users > 0, datablocks)
    )  # materialize becuase we need len() almost always


def time_cache(max_age, maxsize=128, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.

    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator
