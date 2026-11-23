import os
import ssl
import json
import urllib.parse
import urllib.request
import features_pro

MR_DOMAIN = ".".join(("api", "modrinth", "com"))
MR_BASE = f"https://{MR_DOMAIN}/v2"

TYPE_MAP = {
    "Mods": "mod",
    "Modpacks": "modpack",
    "Resource Packs": "resourcepack",
    "Shaders": "shader"
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

def _ps_json(url):
    opener = _build_opener()
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "NKLauncher/1.0 (contact@nklauncher.local)"
        }
    )
    with opener.open(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="ignore").strip()
    if not raw or not raw.startswith(("{", "[")):
        raise Exception("Modrinth returned invalid response")
    return json.loads(raw)

def search_projects(query="", category="Mods", version="26.3", loader="Fabric", offset=0, limit=18):
    ptype = TYPE_MAP.get(category, "mod")
    facets = [[f"project_type:{ptype}"]]
    if version and version != "All":
        clean_v = version.replace("OptiFine ", "", 1)
        facets.append([f"versions:{clean_v}"])
    if category == "Mods" and loader and loader not in ("Vanilla", "Any"):
        facets.append([f"categories:{loader.lower()}"])

    params = {
        "query": query,
        "facets": json.dumps(facets),
        "offset": offset,
        "limit": limit,
        "index": "relevance" if query else "downloads"
    }
    url = f"{MR_BASE}/search?" + urllib.parse.urlencode(params)
    data = _ps_json(url)

    results = []
    for hit in data.get("hits", []):
        results.append({
            "source": "modrinth",
            "id": hit.get("project_id"),
            "name": hit.get("title"),
            "summary": hit.get("description", ""),
            "author": hit.get("author", "Modrinth"),
            "downloads": hit.get("downloads", 0),
            "icon_url": hit.get("icon_url")
        })
    return results

def download_project(project_id, version, loader, category, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    clean_v = version.replace("OptiFine ", "", 1) if version else ""

    params = {}
    if clean_v and clean_v != "All":
        params["game_versions"] = json.dumps([clean_v])
    if category == "Mods" and loader and loader not in ("Vanilla", "Any"):
        params["loaders"] = json.dumps([loader.lower()])

    q = f"?{urllib.parse.urlencode(params)}" if params else ""
    url = f"{MR_BASE}/project/{project_id}/version{q}"
    versions = _ps_json(url)

    if not versions and clean_v and clean_v != "All":
        url2 = f"{MR_BASE}/project/{project_id}/version?" + urllib.parse.urlencode({"game_versions": json.dumps([clean_v])})
        versions = _ps_json(url2)

    if not versions and params:
        versions = _ps_json(f"{MR_BASE}/project/{project_id}/version")

    if not versions:
        raise Exception(f"No compatible Modrinth file found for {clean_v}")

    latest = next(iter(versions))
    files = latest.get("files", [])
    primary = next((f for f in files if f.get("primary")), next(iter(files)) if files else None)
    if not primary:
        raise Exception("Download file missing in Modrinth release")

    dl_url = primary.get("url")
    filename = primary.get("filename")
    out_path = os.path.join(target_dir, filename)

    opener = _build_opener()
    req = urllib.request.Request(dl_url, headers={"User-Agent": "NKLauncher/1.0"})
    with opener.open(req, timeout=30) as r, open(out_path, "wb") as f:
        f.write(r.read())
    return filename
