import os
import invoke
import dotenv

dotenv.load_dotenv(verbose=True)


@invoke.task
def build(c, blender_path=None):
    blender_path = blender_path or os.getenv("BLENDER_PATH")

    if blender_path is None:
        print("BLENDER_PATH not provided. Check your .env file.")
        return

    print(f"Using blender found in: {blender_path}")

    command = f'"{blender_path}" --command extension build --valid-tags=""'
    c.run(command)
