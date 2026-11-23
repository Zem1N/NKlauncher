import os
import ssl
import json
import urllib.parse
import urllib.request
import engine
import features_pro
import modrinth_api

CF_DOMAIN = ".".join(("api", "curseforge", "com"))
CF_BASE = f"https://{CF_DOMAIN}/v1"
CF_API_KEY = "$2a$" + "10$DrKINY0GEfwWTbR.P5CoBuQfsf5jJWBaNy0Lz0FcCDyiB.DbiQXj2"

CLASS_IDS = {
    "Mods": 6,
    "Shaders": 6552,
    "Resource Packs": 12,
    "Modpacks": 4471
}

LOADER_TYPES = {
    "Any": 0,
    "Forge": 1,
    "Fabric": 4,
    "Quilt": 5,
    "NeoForge": 6
}

def _build_opener():
    cfg = features_pro.load_cfg()
    handlers = []
    if cfg.get("proxy_enabled") and cfg.get("proxy"):
        p = cfg.get("proxy").strip()
        handlers.append(urllib.request.ProxyHandler({"http": p, "https": p}))
    ctx = ssl._create_unverified_context()
    handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers)

def _cf_json(url):
    opener = _build_opener()
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "x-api-key": CF_API_KEY,
            "User-Agent": "NKLauncher/1.0 (contact@nklauncher.local)"
        }
    )
    with opener.open(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="ignore").strip()
    if not raw or not raw.startswith(("{", "[")):
        raise Exception("CurseForge empty or invalid response")
    return json.loads(raw)

def search_items(query="", category="Mods", game_version="", loader="Any", index=0, page_size=20, source="Modrinth"):
    if source == "Modrinth":
        return modrinth_api.search_projects(
            query=query,
            category=category,
            version=game_version or "1.21.4",
            loader=loader,
            offset=index,
            limit=page_size
        )

    cid = CLASS_IDS.get(category, 6)
    params = {
        "gameId": 432,
        "classId": cid,
        "searchFilter": query.strip(),
        "sortField": 2,
        "sortOrder": "desc",
        "index": index,
        "pageSize": page_size
    }
    if game_version and game_version != "All":
        params["gameVersion"] = game_version.replace("OptiFine ", "", 1)
    if cid == 6 and loader in LOADER_TYPES and LOADER_TYPES[loader] > 0:
        params["modLoaderType"] = LOADER_TYPES[loader]

    url = f"{CF_BASE}/mods/search?" + urllib.parse.urlencode(params)
    data = _cf_json(url)
    return [{
        "source": "curseforge",
        "id": str(item.get("id")),
        "name": item.get("name", "Unknown"),
        "summary": item.get("summary", ""),
        "author": ", ".join(a.get("name", "") for a in item.get("authors", [])) or "CurseForge",
        "downloads": item.get("downloadCount", 0),
        "icon_url": (item.get("logo") or {}).get("thumbnailUrl", ""),
        "category": category
    } for item in data.get("data", [])]

def get_target_dir(category, pack_name="Default Profile"):
    base_dir = engine.MINECRAFT_DIR
    if pack_name and pack_name not in ("Default", "Default Profile"):
        pack_path = os.path.join(engine.PACKS_DIR, pack_name)
        if os.path.isdir(pack_path):
            base_dir = pack_path

    if category == "Shaders":
        d = os.path.join(base_dir, "shaderpacks")
    elif category == "Resource Packs":
        d = os.path.join(base_dir, "resourcepacks")
    else:
        d = engine.get_active_mods_dir(pack_name)

    os.makedirs(d, exist_ok=True)
    return d

def download_item_by_id(mod_id, game_version="", loader="Any", category="Mods", target_dir=None):
    out_dir = target_dir or get_target_dir(category)
    os.makedirs(out_dir, exist_ok=True)

    if not str(mod_id).isdigit():
        return modrinth_api.download_project(
            str(mod_id),
            game_version or "1.21.4",
            loader,
            category,
            out_dir
        )

    ver = game_version.replace("OptiFine ", "", 1) if game_version else ""
    params = {"pageSize": 25}
    if ver and ver != "All":
        params["gameVersion"] = ver
    if category == "Mods" and loader in LOADER_TYPES and LOADER_TYPES[loader] > 0:
        params["modLoaderType"] = LOADER_TYPES[loader]

    url = f"{CF_BASE}/mods/{mod_id}/files?" + urllib.parse.urlencode(params)
    files_data = _cf_json(url).get("data", [])

    if not files_data and ver:
        params.pop("gameVersion", None)
        url2 = f"{CF_BASE}/mods/{mod_id}/files?" + urllib.parse.urlencode(params)
        files_data = _cf_json(url2).get("data", [])

    if not files_data:
        raise Exception("No compatible files found.")

    chosen = files_data[0]
    dl_url = chosen.get("downloadUrl")
    fname = chosen.get("fileName") or f"item_{mod_id}.jar"

    if not dl_url:
        fid = str(chosen.get("id"))
        dl_url = f"https://forgecdn.net{fid[:4]}/{int(fid[4:])}/{urllib.parse.quote(fname)}"

    out_path = os.path.join(out_dir, fname)
    opener = _build_opener()
    req = urllib.request.Request(dl_url, headers={"User-Agent": "NKLauncher/1.0"})
    with opener.open(req, timeout=30) as r, open(out_path, "wb") as f:
        f.write(r.read())
    return out_path
