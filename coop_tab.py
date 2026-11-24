import os, sys, ssl, json, threading, subprocess, urllib.request
from tkinter import messagebox
import customtkinter as ctk
import engine, modrinth_api, ui_theme

C = ui_theme.PALETTE
FRIENDS_FILE = os.path.join(engine.MINECRAFT_DIR, "friends.json")
ACC_FILE = os.path.join(engine.MINECRAFT_DIR, "accounts.json")

def load_friends():
    if os.path.exists(FRIENDS_FILE):
        try: return json.load(open(FRIENDS_FILE, "r", encoding="utf-8"))
        except Exception: pass
    return []

def save_friends(data):
    json.dump(data, open(FRIENDS_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

def check_nk_friend_exists(nick):
    clean = nick.strip().lower()
    if os.path.exists(ACC_FILE):
        try:
            d = json.load(open(ACC_FILE, "r", encoding="utf-8"))
            items = list(d.values()) if isinstance(d, dict) else (d if isinstance(d, list) else [])
            for a in items:
                if isinstance(a, dict) and a.get("name", "").lower() == clean: return True, a
        except Exception: pass
    return False, None

def build_coop_tab(app):
    app.coop_frame.configure(fg_color=C["bg"])
    top = ctk.CTkFrame(app.coop_frame, fg_color="transparent")
    top.pack(fill="x", padx=32, pady=(22, 10))
    ctk.CTkLabel(top, text="FRIENDS & COOP SERVER", font=ctk.CTkFont("Arial Black", 21, "bold")).pack(side="left")
    cc = ctk.CTkFrame(app.coop_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["accent"])
    cc.pack(fill="x", padx=32, pady=(0, 12))
    ctk.CTkLabel(cc, text="PLAY WITH FRIENDS IN SINGLEPLAYER (E4MC COOP)", font=ctk.CTkFont(size=13, weight="bold"), text_color=C["accent"]).pack(anchor="w", padx=20, pady=(12, 3))
    ctk.CTkLabel(cc, text="1. Install Coop Mod (Fabric) - Open world - - to LAN - Share .e4mc.link IP from chat!", font=ctk.CTkFont(size=12), text_color="#cde0d4").pack(anchor="w", padx=20, pady=(0, 10))
    br = ctk.CTkFrame(cc, fg_color="transparent")
    br.pack(fill="x", padx=20, pady=(0, 14))
    app.btn_install_coop = ctk.CTkButton(br, text="Install Coop Mod (e4mc + Fabric API)", height=36, corner_radius=10, fg_color=C["accent"], hover_color=C["hover"], text_color="#09130c", font=ctk.CTkFont(weight="bold"), command=lambda: install_coop_mods(app))
    app.btn_install_coop.pack(side="left", padx=(0, 10))
    app.btn_host_srv = ctk.CTkButton(br, text="Create & Start Dedicated Server", height=36, corner_radius=10, fg_color="#3498db", hover_color="#2980b9", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), command=lambda: create_dedicated_server(app))
    app.btn_host_srv.pack(side="left")
    ab = ctk.CTkFrame(app.coop_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    ab.pack(fill="x", padx=32, pady=(0, 12))
    ctk.CTkLabel(ab, text="ADD FRIEND (CHECK NKLAUNCHER ACCOUNT)", font=ctk.CTkFont(size=12, weight="bold"), text_color=C["accent"]).pack(anchor="w", padx=20, pady=(12, 6))
    fr = ctk.CTkFrame(ab, fg_color="transparent")
    fr.pack(fill="x", padx=20, pady=(0, 6))
    app.friend_nick_in = ctk.CTkEntry(fr, placeholder_text="Friend username in NKLauncher...", height=38, corner_radius=10, fg_color=C["input"], border_color=C["border"], font=ctk.CTkFont(size=13, weight="bold"))
    app.friend_nick_in.pack(side="left", fill="x", expand=True, padx=(0, 8))
    app.friend_note_in = ctk.CTkEntry(fr, placeholder_text="Note (e.g. Fabric 1.21.4)", width=190, height=38, corner_radius=10, fg_color=C["input"], border_color=C["border"], font=ctk.CTkFont(size=12))
    app.friend_note_in.pack(side="left", padx=(0, 8))
    ctk.CTkButton(fr, text="Check", width=105, height=38, corner_radius=10, fg_color=C["pill"], hover_color="#26352d", border_width=1, border_color=C["border"], font=ctk.CTkFont(size=12, weight="bold"), command=lambda: _check_friend_ui(app)).pack(side="left", padx=(0, 8))
    ctk.CTkButton(fr, text="+ Add Friend", width=120, height=38, corner_radius=10, fg_color=C["accent"], hover_color=C["hover"], text_color="#09130c", font=ctk.CTkFont(size=12, weight="bold"), command=lambda: add_friend(app)).pack(side="left")
    app.friend_status_lbl = ctk.CTkLabel(ab, text="Enter friend username to verify if their NKLauncher account exists.", font=ctk.CTkFont(size=12), text_color=C["muted"])
    app.friend_status_lbl.pack(anchor="w", padx=20, pady=(0, 12))
    app.friends_scroll = ctk.CTkScrollableFrame(app.coop_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    app.friends_scroll.pack(fill="both", expand=True, padx=32, pady=(0, 22))

def _check_friend_ui(app):
    nick = app.friend_nick_in.get().strip()
    if not nick:
        app.friend_status_lbl.configure(text="Enter friend username first!", text_color="#e67e22")
        return
    exists, acc = check_nk_friend_exists(nick)
    app.friend_status_lbl.configure(text=f"[OK] Account {acc.get('name')} exists in NKLauncher!" if exists else f"Account {nick} not found in local NKLauncher database (External Player)", text_color="#2ecc71" if exists else "#e67e22")

def add_friend(app):
    nick = app.friend_nick_in.get().strip()
    if not nick:
        return
    note = app.friend_note_in.get().strip() or "Coop Buddy"
    exists, acc = check_nk_friend_exists(nick)
    rname = acc.get("name", nick) if exists else nick
    friends = [f for f in load_friends() if f.get("name", "").lower() != rname.lower()]
    friends.insert(0, {"name": rname, "note": note, "nk_exists": exists, "uuid": acc.get("uuid", "") if exists else "", "skin": acc.get("skin", "") if exists else ""})
    save_friends(friends)
    app.friend_nick_in.delete(0, "end")
    app.friend_note_in.delete(0, "end")
    refresh_friends_list(app)

def refresh_friends_list(app):
    for w in app.friends_scroll.winfo_children():
        w.destroy()
    friends = load_friends()
    if not friends:
        ctk.CTkLabel(app.friends_scroll, text="Your friends list is empty. Add a friend above!", text_color=C["muted"]).pack(pady=35)
        return
    for fr in friends:
        name = fr.get("name", "Friend")
        exists, acc = check_nk_friend_exists(name)
        row = ctk.CTkFrame(app.friends_scroll, fg_color=C["pill"], corner_radius=12, border_width=1, border_color=C["accent"] if exists else C["border"])
        row.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(row, text=name[:2].upper(), width=38, height=38, fg_color=C["card"], text_color=C["accent"] if exists else "#9aa5b4", corner_radius=8, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(12, 10), pady=10)
        ib = ctk.CTkFrame(row, fg_color="transparent")
        ib.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(ib, text=f"{name}   [{'NK ACCOUNT EXISTS' if exists else 'EXTERNAL PLAYER'}]", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(ib, text=fr.get("note", "Coop Buddy"), font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(anchor="w")
        ctk.CTkButton(row, text="Remove", width=82, height=32, corner_radius=8, fg_color="#3a1d1d", hover_color="#c0392b", text_color="#ff8a80", font=ctk.CTkFont(size=12, weight="bold"), command=lambda n=name: [save_friends([x for x in load_friends() if x.get("name") != n]), refresh_friends_list(app)]).pack(side="right", padx=14)

def install_coop_mods(app):
    ver = app.version_menu.get().replace("OptiFine ", "", 1).strip()
    if app.loader_menu.get() != "Fabric":
        messagebox.showinfo("Select Fabric", "Switch MOD LOADER to Fabric in the left sidebar first!")
        return
    m_dir = engine.get_active_mods_dir(app.pack_menu.get())
    app.btn_install_coop.configure(text="Installing e4mc...", state="disabled")
    def task():
        try:
            modrinth_api.download_project("e4mc", ver, "Fabric", "Mods", m_dir)
            modrinth_api.download_project("fabric-api", ver, "Fabric", "Mods", m_dir)
            app.after(0, lambda: [app.btn_install_coop.configure(text="Coop Ready!", state="normal"), app.refresh_mods_list(), messagebox.showinfo("Coop Installed", "e4mc + Fabric API installed!")])
        except Exception as e:
            app.after(0, lambda err=e: [app.btn_install_coop.configure(text="Install Coop Mod (e4mc + Fabric API)", state="normal"), messagebox.showerror("Error", str(err))])
    threading.Thread(target=task, daemon=True).start()

def create_dedicated_server(app):
    ver = app.version_menu.get().replace("OptiFine ", "", 1).strip()
    srv_dir = os.path.join(engine.MINECRAFT_DIR, "servers", f"Server_{ver}")
    os.makedirs(srv_dir, exist_ok=True)
    app.btn_host_srv.configure(text="Downloading server.jar...", state="disabled")
    def task():
        try:
            ctx = ssl._create_unverified_context()
            man = json.loads(urllib.request.urlopen("https://mojang.com", context=ctx, timeout=15).read().decode())
            v_info = next((v for v in man.get("versions", []) if v.get("id") == ver), None)
            meta = json.loads(urllib.request.urlopen(v_info.get("url"), context=ctx, timeout=15).read().decode())
            jar_path = os.path.join(srv_dir, "server.jar")
            if not os.path.exists(jar_path):
                open(jar_path, "wb").write(urllib.request.urlopen(meta.get("downloads", {}).get("server", {}).get("url"), context=ctx, timeout=30).read())
            open(os.path.join(srv_dir, "eula.txt"), "w").write("eula=true\n")
            open(os.path.join(srv_dir, "server.properties"), "w").write("online-mode=false\nmotd=NKLauncher Coop Server\nmax-players=10\n")
            jname = "java.exe" if sys.platform == "win32" else "java"
            jexe = next((os.path.join(r, jname) for r, _, fs in os.walk(os.path.join(engine.MINECRAFT_DIR, "runtime")) if jname in fs), "java")
            engine.open_folder(srv_dir)
            subprocess.Popen([jexe, "-Xmx2G", "-jar", "server.jar", "nogui"], cwd=srv_dir)
            app.after(0, lambda: [app.btn_host_srv.configure(text="Create & Start Dedicated Server", state="normal"), messagebox.showinfo("Server Started", f"Server {ver} started!")])
        except Exception as e:
            app.after(0, lambda err=e: [app.btn_host_srv.configure(text="Create & Start Dedicated Server", state="normal"), messagebox.showerror("Server Error", str(err))])
    threading.Thread(target=task, daemon=True).start()
