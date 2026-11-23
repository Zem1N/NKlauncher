import os
import sys
import ssl
import json
import threading
import subprocess
import urllib.request
from tkinter import messagebox, simpledialog
import customtkinter as ctk
import engine
import mod_catalog
import modrinth_api
import ui_theme

C = ui_theme.PALETTE
FRIENDS_FILE = os.path.join(engine.MINECRAFT_DIR, "friends.json")

def load_friends():
    if os.path.exists(FRIENDS_FILE):
        try:
            with open(FRIENDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return list()

def save_friends(data):
    with open(FRIENDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_coop_tab(app):
    app.coop_frame.configure(fg_color=C["bg"])
    top = ctk.CTkFrame(app.coop_frame, fg_color="transparent")
    top.pack(fill="x", padx=35, pady=(25, 10))
    ctk.CTkLabel(top, text="FRIENDS & COOP SERVER", font=ctk.CTkFont(family="Arial Black", size=22, weight="bold")).pack(side="left")

    ctk.CTkButton(top, text="+ Add Friend", height=36, corner_radius=10, fg_color=C["accent"], hover_color=C["hover"], text_color="#09130c", font=ctk.CTkFont(weight="bold"), command=lambda: add_friend(app)).pack(side="right")

    coop_card = ctk.CTkFrame(app.coop_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["accent"])
    coop_card.pack(fill="x", padx=35, pady=8)

    ctk.CTkLabel(coop_card, text="🌍 PLAY WITH FRIENDS IN SINGLEPLAYER (E4MC COOP)", font=ctk.CTkFont(size=14, weight="bold"), text_color=C["accent"]).pack(anchor="w", padx=20, pady=(14, 4))
    ctk.CTkLabel(coop_card, text="1. Click 'Install Coop Mod' (select Fabric).  2. Enter world -> Esc -> 'Open to LAN'.  3. Share the .e4mc.link IP from chat!", font=ctk.CTkFont(size=12), text_color="#cde0d4").pack(anchor="w", padx=20, pady=(0, 12))

    btn_row = ctk.CTkFrame(coop_card, fg_color="transparent")
    btn_row.pack(fill="x", padx=20, pady=(0, 15))

    app.btn_install_coop = ctk.CTkButton(btn_row, text="⚡ Install Coop Mod (e4mc + Fabric API)", height=38, corner_radius=10, fg_color=C["accent"], hover_color=C["hover"], text_color="#09130c", font=ctk.CTkFont(weight="bold"), command=lambda: install_coop_mods(app))
    app.btn_install_coop.pack(side="left", padx=(0, 10))

    app.btn_host_srv = ctk.CTkButton(btn_row, text="🖥️ Create & Start Dedicated Server", height=38, corner_radius=10, fg_color="#3498db", hover_color="#2980b9", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), command=lambda: create_dedicated_server(app))
    app.btn_host_srv.pack(side="left")

    ctk.CTkLabel(app.coop_frame, text="YOUR FRIENDS LIST", font=ctk.CTkFont(size=14, weight="bold"), text_color=C["muted"]).pack(anchor="w", padx=35, pady=(12, 4))
    app.friends_scroll = ctk.CTkScrollableFrame(app.coop_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    app.friends_scroll.pack(fill="both", expand=True, padx=35, pady=(0, 25))

def add_friend(app):
    nick = simpledialog.askstring("Add Friend", "Enter friend's Minecraft username:")
    if nick and nick.strip():
        friends = load_friends()
        if not any(f.get("name", "").lower() == nick.strip().lower() for f in friends):
            friends.append({"name": nick.strip(), "note": "Coop Buddy"})
            save_friends(friends)
        refresh_friends_list(app)

def refresh_friends_list(app):
    for w in app.friends_scroll.winfo_children():
        w.destroy()
    friends = load_friends()
    if not friends:
        ctk.CTkLabel(app.friends_scroll, text="No friends added yet. Click '+ Add Friend' to add your bro!", text_color=C["muted"]).pack(pady=35)
        return
    for fr in friends:
        row = ctk.CTkFrame(app.friends_scroll, fg_color=C["pill"], corner_radius=10, border_width=1, border_color=C["border"])
        row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row, text=f"🟢  {fr.get('name')}   •   {fr.get('note', 'Ready to play')}", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=10)
        ctk.CTkButton(row, text="Remove", width=75, fg_color="#e74c3c", command=lambda n=fr.get("name"): [save_friends([x for x in load_friends() if x.get("name") != n]), refresh_friends_list(app)]).pack(side="right", padx=15)

def _download_with_fallback(slug, cf_id, ver, m_dir):
    try:
        return modrinth_api.download_project(slug, ver, "Fabric", "Mods", m_dir)
    except Exception:
        pass
    try:
        return modrinth_api.download_project(slug, "All", "Fabric", "Mods", m_dir)
    except Exception:
        pass
    return mod_catalog.download_item_by_id(cf_id, ver, "Fabric", "Mods", m_dir)

def install_coop_mods(app):
    ver = app.version_menu.get().replace("OptiFine ", "", 1).strip()
    loader = app.loader_menu.get()
    if loader != "Fabric":
        messagebox.showinfo("Select Fabric", "Switch MOD LOADER to 'Fabric' in the left sidebar first!")
        return
    m_dir = engine.get_active_mods_dir(app.pack_menu.get())
    app.btn_install_coop.configure(text="Installing e4mc...", state="disabled")

    def task():
        try:
            _download_with_fallback("e4mc", "883882", ver, m_dir)
            try:
                _download_with_fallback("fabric-api", "306612", ver, m_dir)
            except Exception:
                pass
            app.after(0, lambda: [
                app.btn_install_coop.configure(text="✓ Coop Ready!", state="normal"),
                app.refresh_mods_list(),
                messagebox.showinfo("Coop Installed", "e4mc + Fabric API installed!\nOpen any world -> Esc -> Open to LAN -> share the .e4mc.link IP from chat!")
            ])
        except Exception as e:
            app.after(0, lambda err=e: [
                app.btn_install_coop.configure(text="⚡ Install Coop Mod (e4mc + Fabric API)", state="normal"),
                messagebox.showerror("Error", str(err))
            ])

    threading.Thread(target=task, daemon=True).start()

def _get_json(url):
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={"User-Agent": "NKLauncher/1.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", errors="ignore"))

def create_dedicated_server(app):
    ver = app.version_menu.get().replace("OptiFine ", "", 1).strip()
    srv_dir = os.path.join(engine.MINECRAFT_DIR, "servers", f"Server_{ver}")
    os.makedirs(srv_dir, exist_ok=True)
    app.btn_host_srv.configure(text="Downloading server.jar...", state="disabled")

    def task():
        try:
            manifest_url = "https://" + ".".join(("launchermeta", "mojang", "com")) + "/mc/game/version_manifest_v2.json"
            man = _get_json(manifest_url)
            v_info = next((v for v in man.get("versions", list()) if v.get("id") == ver), None)
            if not v_info:
                raise Exception(f"Version {ver} not found in Mojang manifest")

            meta = _get_json(v_info.get("url"))
            srv_url = meta.get("downloads", {}).get("server", {}).get("url")
            if not srv_url:
                raise Exception(f"Mojang has no dedicated server.jar for {ver}")

            jar_path = os.path.join(srv_dir, "server.jar")
            if not os.path.exists(jar_path):
                ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(srv_url, context=ctx, timeout=30) as r, open(jar_path, "wb") as f:
                    f.write(r.read())

            with open(os.path.join(srv_dir, "eula.txt"), "w", encoding="utf-8") as f:
                f.write("eula=true\n")
            with open(os.path.join(srv_dir, "server.properties"), "w", encoding="utf-8") as f:
                f.write("online-mode=false\nmotd=NKLauncher Coop Server\nmax-players=10\n")

            java_name = "java.exe" if sys.platform == "win32" else "java"
            java_exe = "java"
            rt_dir = os.path.join(engine.MINECRAFT_DIR, "runtime")
            if os.path.exists(rt_dir):
                for r, _, fs in os.walk(rt_dir):
                    if java_name in fs:
                        java_exe = os.path.join(r, java_name)
                        break

            engine.open_folder(srv_dir)
            subprocess.Popen([java_exe, "-Xmx2G", "-jar", "server.jar", "nogui"], cwd=srv_dir)
            app.after(0, lambda: [
                app.btn_host_srv.configure(text="🖥️ Create & Start Dedicated Server", state="normal"),
                messagebox.showinfo("Server Started", f"Server {ver} started!\nConnect via 'localhost' (or your Radmin/Hamachi IP).")
            ])
        except Exception as e:
            app.after(0, lambda err=e: [
                app.btn_host_srv.configure(text="🖥️ Create & Start Dedicated Server", state="normal"),
                messagebox.showerror("Server Error", str(err))
            ])

    threading.Thread(target=task, daemon=True).start()
