import os
import sys
import json
import uuid
import subprocess
import minecraft_launcher_lib as mllib

if sys.platform == "win32":
    MINECRAFT_DIR = r"C:\MyMinecraftLauncherData"
elif sys.platform == "darwin":
    MINECRAFT_DIR = os.path.expanduser("~/Library/Application Support/NKLauncher")
else:
    MINECRAFT_DIR = os.path.expanduser("~/.nklauncher")

PACKS_DIR = os.path.join(MINECRAFT_DIR, "packs")

os.makedirs(MINECRAFT_DIR, exist_ok=True)
os.makedirs(PACKS_DIR, exist_ok=True)

def open_folder(path):
    os.makedirs(path, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def _load_versions_by_type():
    cats = {"release": [], "snapshot": [], "old_beta": [], "old_alpha": []}
    try:
        for v in mllib.utils.get_version_list():
            vtype = v.get("type", "release")
            vid = v.get("id")
            if vtype in cats and vid:
                cats[vtype].append(vid)
    except Exception:
        pass
    if not cats["release"]:
        cats["release"] = [
            "26.3", "26.1.2", "1.21.5", "1.21.4", "1.21.1", "1.20.6",
            "1.20.4", "1.20.1", "1.19.4", "1.19.2", "1.18.2", "1.16.5", "1.12.2", "1.8.9"
        ]
    return cats

VERSION_GROUPS = _load_versions_by_type()
AVAILABLE_VERSIONS = VERSION_GROUPS["release"]

def get_active_game_dir(pack_name):
    if pack_name and pack_name not in ("Default", "Default Profile"):
        p = os.path.join(PACKS_DIR, pack_name)
        os.makedirs(p, exist_ok=True)
        return p
    return MINECRAFT_DIR

def get_active_mods_dir(pack_name):
    d = os.path.join(get_active_game_dir(pack_name), "mods")
    os.makedirs(d, exist_ok=True)
    return d

def _install_loader(mc_ver, loader, callback):
    if loader == "Fabric":
        mllib.fabric.install_fabric(mc_ver, MINECRAFT_DIR, callback=callback)
        for v in mllib.utils.get_installed_versions(MINECRAFT_DIR):
            if "fabric-loader" in v["id"] and v["id"].endswith(mc_ver):
                return v["id"]
    elif loader == "Quilt":
        mllib.quilt.install_quilt(mc_ver, MINECRAFT_DIR, callback=callback)
        for v in mllib.utils.get_installed_versions(MINECRAFT_DIR):
            if "quilt-loader" in v["id"] and v["id"].endswith(mc_ver):
                return v["id"]
    elif loader == "Forge":
        fver = mllib.forge.find_forge_version(mc_ver)
        if not fver:
            raise Exception(f"Forge is not available for Minecraft {mc_ver}")
        mllib.forge.install_forge_version(fver, MINECRAFT_DIR, callback=callback)
        for v in mllib.utils.get_installed_versions(MINECRAFT_DIR):
            if "forge" in v["id"].lower() and mc_ver in v["id"]:
                return v["id"]
    elif loader == "NeoForge":
        nf_vers = mllib.neoforge.get_neoforge_versions(mc_ver)
        if not nf_vers:
            raise Exception(f"NeoForge is not available for Minecraft {mc_ver}")
        mllib.neoforge.install_neoforge_version(nf_vers[0], MINECRAFT_DIR, callback=callback)
        for v in mllib.utils.get_installed_versions(MINECRAFT_DIR):
            if "neoforge" in v["id"].lower() and mc_ver in v["id"]:
                return v["id"]
    return mc_ver

def _get_acc_options(nick):
    acc_file = os.path.join(MINECRAFT_DIR, "accounts.json")
    if os.path.exists(acc_file):
        try:
            data = json.load(open(acc_file, "r", encoding="utf-8"))
            items = data.values() if isinstance(data, dict) else data
            for acc in items:
                if isinstance(acc, dict) and acc.get("name") == nick and acc.get("access_token"):
                    return {
                        "username": nick,
                        "uuid": acc.get("uuid") or str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{nick}")),
                        "token": acc.get("access_token")
                    }
        except Exception:
            pass
    return {
        "username": nick,
        "uuid": str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{nick}")),
        "token": "0"
    }

def launch_task(app):
    raw_ver = app.version_menu.get()
    mc_ver = raw_ver.replace("OptiFine ", "", 1).strip()
    loader = app.loader_menu.get()
    nick = app.nick_entry.get().strip()
    pack_name = app.pack_menu.get()
    ram = int(app.ram_gb) if hasattr(app, "ram_gb") else int(app.ram_var.get())

    callback = {
        "setStatus": lambda text: app.set_status(text),
        "setProgress": lambda val: app.set_progress(val),
        "setMax": lambda val: app.set_max(val)
    }

    try:
        app.set_status(f"Installing Minecraft {mc_ver}...")
        mllib.install.install_minecraft_version(mc_ver, MINECRAFT_DIR, callback=callback)

        launch_id = mc_ver
        if loader and loader != "Vanilla":
            app.set_status(f"Installing {loader} for {mc_ver}...")
            launch_id = _install_loader(mc_ver, loader, callback)

        game_dir = get_active_game_dir(pack_name)
        options = _get_acc_options(nick)
        options["gameDirectory"] = game_dir
        options["jvmArguments"] = [f"-Xmx{ram}G", f"-Xms{max(1, ram // 2)}G"]

        if getattr(app, "fullscreen_var", None) and app.fullscreen_var.get():
            options["customResolution"] = False
            options["fullscreen"] = True

        if getattr(app, "join_server_ip", None):
            ip = app.join_server_ip
            app.join_server_ip = None
            if ":" in ip:
                host, port = ip.split(":", 1)
                options["server"] = host
                options["port"] = port
            else:
                options["server"] = ip

        app.set_status(f"Launching {launch_id}...")
        cmd = mllib.command.get_minecraft_command(launch_id, MINECRAFT_DIR, options)
        if sys.platform == "win32":
            cmd = [c.replace("java.exe", "javaw.exe") if c.lower().endswith("java.exe") else c for c in cmd]
            subprocess.Popen(cmd, cwd=game_dir, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(cmd, cwd=game_dir)

        app.set_status(f"Running Minecraft {mc_ver} ({loader})")
        app.set_progress(1.0)
        if hasattr(app, "reset_play_btn"):
            app.after(0, app.reset_play_btn)
    except Exception as e:
        if hasattr(app, "show_error"):
            app.after(0, lambda err=e: app.show_error(mc_ver, err))
        else:
            app.set_status(f"Error: {e}")

def list_packs():
    os.makedirs(PACKS_DIR, exist_ok=True)
    res = sorted(d for d in os.listdir(PACKS_DIR) if os.path.isdir(os.path.join(PACKS_DIR, d)))
    return res if res else ["Default"]
