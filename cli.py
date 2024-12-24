import dotenv
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Run pigeons in headless mode")
parser.add_argument(
    "--hw",
    type=str,
    help="The homework to run",
    required=True,
)
parser.add_argument(
    "--homework-file",
    type=str,
    help="The file containing the homework",
    required=True,
)

args = parser.parse_args()

dotenv.load_dotenv()
blender_path = os.getenv("BLENDER_PATH", "")
subprocess.run(
    [
        blender_path,
        "--background",
        "--python",
        "headless.py",
        "--",
        f"--hw={args.hw}",
        f"--homework-file={args.homework_file}",
    ]
)
