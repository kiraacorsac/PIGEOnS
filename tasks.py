import os
import invoke
import dotenv

dotenv.load_dotenv(verbose=True)


@invoke.task
def build(c, blender_path=None):
    blender_path = blender_path or os.getenv("BLENDER_PATH")

    if blender_path is None:
        print(f"BLENDER_PATH = {blender_path}. Check your .env file.")
        return

    print(f"Using BLENDER_PATH = {blender_path}")

    command = f'"{blender_path}" --command extension build --valid-tags=""'
    c.run(command)


@invoke.task
def release(c, blender_path=None, extension_repo_path=None):
    blender_path = blender_path or os.getenv("BLENDER_PATH")
    extension_repo_path = extension_repo_path or os.getenv("EXTENSION_REPO_PATH")

    if blender_path is None or extension_repo_path is None:
        print(
            f"BLENDER_PATH = {blender_path} or EXTENSION_REPO_PATH = {extension_repo_path}. Check your .env file."
        )
        return

    print(
        f"Using BLENDER_PATH = {blender_path} or EXTENSION_REPO_PATH = {extension_repo_path}"
    )

    command = f'"{blender_path}" --command extension server-generate --repo-dir={extension_repo_path} --html'
    c.run(command)
