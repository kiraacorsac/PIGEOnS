import tomllib
import http.client
import json
import urllib
import urllib.parse
from . import utils

version = None

try:
    manifest_file = "./blender_manifest.toml"
    with open(manifest_file, "rb") as f:
        manifest_data = tomllib.load(f)
        version = manifest_data.get("version", None)
        version = version.split(".") if version is not None else None
except Exception as e:
    print("Can't load current version number:", e)


@utils.time_cache(60 * 60 * 4)  # Cache results for 4 hours
def check_released_version():  # This function is crap, we need to make this non-blocking.
    url = "https://raw.githubusercontent.com/kiraacorsac/fi-extension-repository/refs/heads/main/index.json"
    parsed_url = urllib.parse.urlparse(url)

    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path)

    try:
        response = conn.getresponse()
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status}")

        data = json.loads(response.read().decode())
        addon_info = next(
            (item for item in data["data"] if item["id"] == "pigeons"), None
        )

        if addon_info:
            return addon_info["version"].split(".")

    except Exception as e:
        print("Unable to check updates:", e)
    finally:
        conn.close()

    return None
