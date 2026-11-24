import os, re, shutil
from tkinter import filedialog
from PIL import Image
import customtkinter as ctk
import engine, accounts, ui_theme

C = ui_theme.PALETTE
SKINS_DIR = os.path.join(engine.MINECRAFT_DIR, "account_skins")
os.makedirs(SKINS_DIR, exist_ok=True)

def build_accounts_tab(app):
    app.accounts_frame.configure(fg_color=C["bg"])
    top = ctk.CTkFrame(app.accounts_frame, fg_color="transparent")
    top.pack(fill="x", padx=32, pady=(24, 12))
    ctk.CTkLabel(top, text="NKLAUNCHER ACCOUNTS", font=ctk.CTkFont("Arial Black", 21, "bold")).pack(side="left")
    card = ctk.CTkFrame(app.accounts_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    card.pack(fill="x", padx=32, pady=(0, 14))
    ctk.CTkLabel(card, text="CREATE NKLAUNCHER PROFILE", font=ctk.CTkFont(size=12, weight="bold"), text_color=C["accent"]).pack(anchor="w", padx=20, pady=(14, 6))
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=20, pady=(0, 8))
    app.acc_nick_in = ctk.CTkEntry(row, placeholder_text="Enter username (3-16 chars: letters, numbers, _)...", height=40, corner_radius=10, fg_color=C["input"], border_color=C["border"], font=ctk.CTkFont(size=13, weight="bold"))
    app.acc_nick_in.pack(side="left", fill="x", expand=True, padx=(0, 10))
    ctk.CTkButton(row, text="Check Name", width=120, height=40, corner_radius=10, fg_color=C["pill"], hover_color="#26352d", border_width=1, border_color=C["border"], font=ctk.CTkFont(size=13, weight="bold"), command=lambda: _check_nick(app)).pack(side="left", padx=(0, 8))
    ctk.CTkButton(row, text="+ Create Account", width=155, height=40, corner_radius=10, fg_color=C["accent"], hover_color=C["hover"], text_color="#09130c", font=ctk.CTkFont(size=13, weight="bold"), command=lambda: _create_acc(app)).pack(side="left")
    app.acc_status_lbl = ctk.CTkLabel(card, text="Create your local NKLauncher profile with a unique UUID and custom skin.", font=ctk.CTkFont(size=12), text_color=C["muted"])
    app.acc_status_lbl.pack(anchor="w", padx=20, pady=(0, 14))
    app.acc_scroll = ctk.CTkScrollableFrame(app.accounts_frame, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    app.acc_scroll.pack(fill="both", expand=True, padx=32, pady=(0, 24))
    refresh_accounts_tab(app)

def _valid(nick):
    c = nick.strip()
    if not re.match(r"[A-Za-z0-9_]{3,16}$", c):
        return False, "Username must be 3-16 chars (letters, numbers, _)"
    if c in accounts.load_accounts():
        return False, f"Account {c} already exists in NKLauncher!"
    return True, f"[OK] Username {c} is available!"

def _check_nick(app):
    ok, msg = _valid(app.acc_nick_in.get())
    app.acc_status_lbl.configure(text=msg, text_color="#2ecc71" if ok else "#e67e22")

def _create_acc(app):
    nick = app.acc_nick_in.get().strip()
    ok, msg = _valid(nick)
    if not ok:
        app.acc_status_lbl.configure(text=msg, text_color="#e67e22")
        return
    accounts.save_account(nick, "")
    app.acc_nick_in.delete(0, "end")
    app.acc_status_lbl.configure(text=f"[OK] Profile {nick} created and activated!", text_color="#2ecc71")
    _select_acc(app, nick)

def _select_acc(app, name):
    if hasattr(app, "set_active_account"):
        app.set_active_account(name)
    elif hasattr(app, "nick_entry"):
        app.nick_entry.delete(0, "end")
        app.nick_entry.insert(0, name)
    sp = os.path.join(SKINS_DIR, f"{name}.png")
    if os.path.exists(sp) and hasattr(app, "update_skin_preview"):
        dst = os.path.join(engine.MINECRAFT_DIR, "custom_skin.png")
        shutil.copy2(sp, dst)
        app.update_skin_preview(dst)
    refresh_accounts_tab(app)

def _set_skin(app, name):
    path = filedialog.askopenfilename(filetypes=[("PNG Skin", "*.png")])
    if not path:
        return
    shutil.copy2(path, os.path.join(SKINS_DIR, f"{name}.png"))
    app.acc_status_lbl.configure(text=f"[OK] Skin bound to {name}!", text_color="#2ecc71")
    _select_acc(app, name)

def refresh_accounts_tab(app):
    if not hasattr(app, "acc_scroll"):
        return
    for w in app.acc_scroll.winfo_children():
        w.destroy()
    accs = accounts.load_accounts()
    if not isinstance(accs, dict) or not accs:
        ctk.CTkLabel(app.acc_scroll, text="No profiles yet. Create your first NKLauncher account above!", text_color=C["muted"]).pack(pady=40)
        return
    cur = app.nick_entry.get().strip() if hasattr(app, "nick_entry") else ""
    for name, info in accs.items():
        act = (cur == name)
        uid = info.get("uuid", "") if isinstance(info, dict) else ""
        c = ctk.CTkFrame(app.acc_scroll, fg_color=C["pill"], corner_radius=12, border_width=1, border_color=C["accent"] if act else C["border"])
        c.pack(fill="x", padx=12, pady=5)
        ctk.CTkLabel(c, text=name[:2].upper(), width=38, height=38, fg_color=C["card"], text_color=C["accent"], corner_radius=8, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(12, 10), pady=10)
        ib = ctk.CTkFrame(c, fg_color="transparent")
        ib.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(ib, text=f"{name}   [NK ACCOUNT]", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(ib, text=f"NK-UUID: {uid[:18]}...", font=ctk.CTkFont(size=11), text_color=C["muted"]).pack(anchor="w")
        bs = ctk.CTkFrame(c, fg_color="transparent")
        bs.pack(side="right", padx=12)
        ctk.CTkButton(bs, text="Skin", width=64, height=32, corner_radius=8, fg_color=C["card"], hover_color="#25332b", border_width=1, border_color=C["border"], font=ctk.CTkFont(size=11, weight="bold"), command=lambda n=name: _set_skin(app, n)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(bs, text="Active" if act else "Select", width=84, height=32, corner_radius=8, fg_color=C["accent"] if act else "#23322a", hover_color=C["hover"], text_color="#09130c" if act else "#fff", font=ctk.CTkFont(size=12, weight="bold"), command=lambda n=name: _select_acc(app, n)).pack(side="left", padx=(0, 6))
        ctk.CTkButton(bs, text="X", width=32, height=32, corner_radius=8, fg_color="#3a1d1d", hover_color="#c0392b", text_color="#ff8a80", font=ctk.CTkFont(size=12, weight="bold"), command=lambda n=name: [accounts.delete_account(n), refresh_accounts_tab(app)]).pack(side="left")

refresh_accounts_list = refresh_accounts_tab
