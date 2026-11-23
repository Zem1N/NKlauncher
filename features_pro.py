import os
import json
import socket
import struct
import threading
import time
from tkinter import messagebox
import customtkinter as ctk
import engine

CFG_FILE = os.path.join(engine.MINECRAFT_DIR, "pro_config.json")

THEMES = {
    "Emerald Green": ("#2ecc71", "#27ae60", "#111111"),
    "Cyber Purple": ("#9b59b6", "#8e44ad", "#ffffff"),
    "Crimson Red": ("#e74c3c", "#c0392b", "#ffffff"),
    "Ocean Blue": ("#3498db", "#2980b9", "#ffffff"),
    "Gold Edition": ("#f1c40f", "#f39c12", "#111111")
}

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "theme": "Emerald Green",
        "fps_boost": True,
        "servers": list(("mc.reallyworld.me", "play.reallyworld.ru")),
        "proxy": "",
        "proxy_enabled": False
    }

def save_cfg(data):
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_accent():
    cfg = load_cfg()
    return THEMES.get(cfg.get("theme", "Emerald Green"), THEMES.get("Emerald Green"))

def _pack_varint(val):
    out = bytearray()
    while True:
        b = val & 0x7F
        val >>= 7
        out.append(b | (0x80 if val > 0 else 0))
        if val == 0:
            break
    return bytes(out)

def _read_varint(sock):
    num = 0
    for i in range(5):
        b = sock.recv(1)
        if not b:
            return 0
        val = ord(b)
        num |= (val & 0x7F) << (7 * i)
        if not (val & 0x80):
            break
    return num

def ping_mc_server(host_str):
    parts = host_str.split(":", 1)
    host = parts.__getitem__(0)
    port = int(parts.__getitem__(1)) if len(parts) > 1 else 25565
    try:
        t0 = time.time()
        s = socket.create_connection((host, port), timeout=3.0)
        ms = int((time.time() - t0) * 1000)

        hb = host.encode("utf-8")
        pkt = b"\x00" + _pack_varint(765) + _pack_varint(len(hb)) + hb + struct.pack(">H", port) + b"\x01"
        s.sendall(_pack_varint(len(pkt)) + pkt)
        s.sendall(b"\x01\x00")

        _read_varint(s)
        _read_varint(s)
        slen = _read_varint(s)
        raw = b""
        while len(raw) < slen:
            chunk = s.recv(slen - len(raw))
            if not chunk:
                break
            raw += chunk
        s.close()
        info = json.loads(raw.decode("utf-8", errors="ignore"))
        pl = info.get("players", {})
        return True, ms, f"{pl.get('online', 0)}/{pl.get('max', 0)}"
    except Exception:
        return False, 0, "Offline"

def build_server_monitor_widget(parent, app):
    ac, hv, tc = get_accent()
    box = ctk.CTkFrame(parent, fg_color="#181818", corner_radius=12, border_width=1, border_color="#2b2b2b")
    box.pack(fill="x", padx=20, pady=(10, 10))

    hdr = ctk.CTkFrame(box, fg_color="transparent")
    hdr.pack(fill="x", padx=15, pady=(8, 4))
    ctk.CTkLabel(hdr, text="📡 QUICK-JOIN SERVER MONITOR", font=ctk.CTkFont(size=12, weight="bold"), text_color=ac).pack(side="left")

    add_ent = ctk.CTkEntry(hdr, placeholder_text="Add IP...", width=140, height=26)
    add_ent.pack(side="right", padx=(6, 0))

    slist = ctk.CTkFrame(box, fg_color="transparent")
    slist.pack(fill="x", padx=15, pady=(0, 8))

    def refresh():
        for w in slist.winfo_children():
            w.destroy()
        cfg = load_cfg()
        for ip in cfg.get("servers", list()):
            row = ctk.CTkFrame(slist, fg_color="#222222", corner_radius=8)
            row.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(row, text=f"🟡  {ip}  •  Pinging...", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(side="left", padx=10, pady=5)

            ctk.CTkButton(row, text="✕", width=24, height=22, fg_color="transparent", hover_color="#e74c3c", command=lambda x=ip: [cfg.get("servers").remove(x), save_cfg(cfg), refresh()]).pack(side="right", padx=(2, 6))
            ctk.CTkButton(row, text="Join ▶", width=64, height=22, fg_color=ac, hover_color=hv, text_color=tc, font=ctk.CTkFont(size=11, weight="bold"), command=lambda x=ip: app.quick_join_server(x)).pack(side="right", padx=4)

            def chk(t=ip, l=lbl):
                ok, ms, onl = ping_mc_server(t)
                try:
                    if l.winfo_exists():
                        l.after(0, lambda: l.configure(text=f"🟢  {t}  •  {onl}  |  {ms} ms" if ok else f"🔴  {t}  •  Offline"))
                except Exception: pass

            threading.Thread(target=chk, daemon=True).start()

    def add_s():
        ip = add_ent.get().strip()
        if ip:
            c = load_cfg()
            c.get("servers").append(ip)
            save_cfg(c)
            add_ent.delete(0, "end")
            refresh()

    ctk.CTkButton(hdr, text="+", width=26, height=26, fg_color=ac, text_color=tc, command=add_s).pack(side="right", padx=4)
    ctk.CTkButton(hdr, text="↻", width=26, height=26, fg_color="#2b2b2b", command=refresh).pack(side="right")
    refresh()

def build_pro_settings_section(parent, app):
    ac, hv, tc = get_accent()
    cfg = load_cfg()

    tc1 = ctk.CTkFrame(parent, corner_radius=14, fg_color="#222222")
    tc1.pack(fill="x", padx=35, pady=8)
    ctk.CTkLabel(tc1, text="🎨 ACCENT THEME", font=ctk.CTkFont(size=14, weight="bold"), text_color=ac).pack(anchor="w", padx=20, pady=(12, 6))

    def on_th(c):
        d = load_cfg()
        d["theme"] = c
        save_cfg(d)
        app.apply_theme_colors()

    sm = ctk.CTkSegmentedButton(tc1, values=list(THEMES.keys()), selected_color=ac, text_color=tc, command=on_th)
    sm.set(cfg.get("theme", "Emerald Green"))
    sm.pack(fill="x", padx=20, pady=(0, 14))

    fc = ctk.CTkFrame(parent, corner_radius=14, fg_color="#222222")
    fc.pack(fill="x", padx=35, pady=8)
    ctk.CTkLabel(fc, text="🚀 FPS BOOSTER & CACHE CLEANER", font=ctk.CTkFont(size=14, weight="bold"), text_color=ac).pack(anchor="w", padx=20, pady=(12, 6))

    def clean():
        rem = 0
        for r, _, fs in os.walk(engine.MINECRAFT_DIR):
            for fn in fs:
                if fn.endswith((".log.gz", ".txt")) and ("crash-" in fn or "logs" in r):
                    try:
                        os.remove(os.path.join(r, fn))
                        rem += 1
                    except Exception:
                        pass
        messagebox.showinfo("Cache Cleaned", f"Cleaned {rem} old log & crash files!")

    ctk.CTkButton(fc, text="🧹 Clean Logs & Crash Reports", height=34, fg_color="#2b2b2b", hover_color=ac, command=clean).pack(anchor="w", padx=20, pady=(4, 14))

    pc = ctk.CTkFrame(parent, corner_radius=14, fg_color="#222222")
    pc.pack(fill="x", padx=35, pady=8)
    ctk.CTkLabel(pc, text="🌐 BUILT-IN PROXY TUNNEL (FOR MODRINTH & GAME)", font=ctk.CTkFont(size=14, weight="bold"), text_color=ac).pack(anchor="w", padx=20, pady=(12, 6))

    pr = ctk.CTkFrame(pc, fg_color="transparent")
    pr.pack(fill="x", padx=20, pady=(0, 14))

    pe = ctk.CTkEntry(pr, placeholder_text="socks5h://127.0.0.1:1080 or http://ip:port", height=34)
    pe.insert(0, cfg.get("proxy", ""))
    pe.pack(side="left", fill="x", expand=True, padx=(0, 10))

    pv = ctk.BooleanVar(value=cfg.get("proxy_enabled", False))
    def spx():
        c = load_cfg()
        c["proxy"] = pe.get().strip()
        c["proxy_enabled"] = pv.get()
        save_cfg(c)
        messagebox.showinfo("Proxy Saved", "Proxy tunnel settings updated!")

    ctk.CTkCheckBox(pr, text="Active", variable=pv, fg_color=ac, command=spx).pack(side="left", padx=(0, 10))
    ctk.CTkButton(pr, text="Save", width=70, height=34, fg_color=ac, text_color=tc, font=ctk.CTkFont(weight="bold"), command=spx).pack(side="right")
