import json
import tempfile
import zipfile
from pathlib import Path
from tkinter import Tk, filedialog

import requests


MODRINTH_API = "https://api.modrinth.com/v2"

def get_single_author(project: dict):
    team_id = project.get("team")

    if not team_id:
        return None

    r = requests.get(f"{MODRINTH_API}/team/{team_id}/members")
    if r.status_code != 200:
        return None

    members = r.json()

    # Prefer owner only
    owner = next((m for m in members if m.get("role") == "owner"), None)

    if owner:
        return owner.get("user", {}).get("username")

    # fallback: first member only (still single)
    if members:
        return members[0].get("user", {}).get("username")

    return None
def resolve_mod_from_hash(sha1: str):
    try:
        r = requests.post(
            f"{MODRINTH_API}/version_files",
            json={"hashes": [sha1], "algorithm": "sha1"}
        )

        if r.status_code != 200:
            return None

        data = r.json()
        return data.get(sha1)

    except Exception:
        return None

def get_modrinth_project(project_id: str):
    r = requests.get(f"{MODRINTH_API}/project/{project_id}")
    if r.status_code != 200:
        return None
    return r.json()


def open_mrpack_and_extract_mods():
    root = Tk()
    root.withdraw()

    path = filedialog.askopenfilename(filetypes=[("MRPack", "*.mrpack")])
    if not path:
        return None

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(path, "r") as z:
        z.extractall(temp_dir)

    manifest_path = Path(temp_dir) / "modrinth.index.json"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    mods_output = []

    for file in manifest.get("files", []):
        hashes = file.get("hashes", {})
        sha1 = hashes.get("sha1")

        if not sha1:
            continue

        resolved = resolve_mod_from_hash(sha1)
        if not resolved:
            continue

        project = get_modrinth_project(resolved["project_id"])
        if not project:
            continue

        links = project.get("links", {}) or {}

        mods_output.append({
            "Name": project.get("title"),
            "Author": get_single_author(project),
            "Icon": project.get("icon_url"),
            "Link": f"https://modrinth.com/mod/{project.get('slug')}"
        })

    return mods_output

Repo = input("Github Repo Release with config folder in it link: ") # example: https://github.com/AllTheMods/ATM-10/archive/refs/tags/2.29.zip
Name = input("Modpack Name: ")             # example: ALL The Mods 10
id =   input("Modpack Id(ASCII Only): ")   # example: ATM10
Author = input("Modpack Author: ")         # example: ATMTeam
mascot = input("Modpack Mascot(as link): ")# example: https://media.forgecdn.net/avatars/thumbnails/1182/438/64/64/638755918649288941.png
link=input("Link To Github for Discovery: ")#example: https://github.com/AllTheMods/ATM-10
version = input("This Modpack Version: ")  # example: 2.29
latestornot=input("is that version latest? 1) Yes 2) No: ")
latestversion= version if latestornot==1 else input("What is the Latest Version: ")
minecraftversion = input("What is the Modpack Version: ")
loadertype=input("what loader do you use? ")
loaderversion=input("what version is the loader? ")
manifest_options= input("1) Add to Registry 2) Update Modpack")
launcher= input("Where Do You want to export your modpack from? Options: 1.Modrinth 2.MultiMC-Based Choose by number: ")
mod_list = None
manifest={}
if launcher == "1":
    mods = open_mrpack_and_extract_mods()
    print(mods)
    mod_list = json.dumps(mods, indent=2)
    print(json.dumps(mods, indent=2))
    exit()
elif launcher == "2":
    pass
else:
    print("Invalid Choose")
    exit(1)
if manifest_options == 1:
    manifest= {
        "id":id,
        "name":Name,
        "Authors":Author,
        "icon":mascot,
        "Repo":Repo,
        "Mods":json.dumps(open_mrpack_and_extract_mods(), indent=2),
        "latest":version if latestornot==1 else latestversion
    }
elif manifest_options == 2:
    manifest= {
        "Mods":json.dumps(open_mrpack_and_extract_mods(), indent=2),
        "minecraft":minecraftversion,
        "loader":{
            "type":loadertype,
            "version":loaderversion
        },
        "files":[
            {
                "path":"mods/cleanroommc.jar",
                "url":"https://mediafilez.forgecdn.net/files/8073/312/%21cleanroom-relauncher-0.5.0.jar",
                "checksum":"b754a47c430f26e6eb13483ca4f6e849", "_comment":"md5_checksum"
            }
        ]
    }
else:
    print("Invalid Choose")
    exit(1)
