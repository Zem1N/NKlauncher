import os
import sys
import shutil
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    HAS_DND = False

import engine, lang, accounts, tabs, extra_tabs, catalog_ui, coop_tab, auth_ui, handlers, features_pro, ui_theme

try:
    import packs_ui
except Exception:
    packs_ui = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BaseApp = (ctk.CTk, TkinterDnD.DnDWrapper) if HAS_DND else (ctk.CTk,)

class ProMinecraftLauncher(*BaseApp):
    def __init__(self):
        super().__init__()
        if HAS_DND:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                pass

        self.title("NKLauncher — Minecraft Launcher")
        try:
            base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            if sys.platform == "win32":
                self.iconbitmap(os.path.join(base, "icon.ico"))
        except Exception:
            pass

        self.geometry("1040x650+100+60")
        self.minsize(920, 580)
        self.is_launching = False
        self._max_prog = 100
        self.active_account = None
        self.current_account = None
        self.join_server_ip = None
        self.fullscreen_var = ctk.BooleanVar(value=False)
        self.ram_var = ctk.IntVar(value=4)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        for name in ("home", "mods", "catalog", "packs", "coop", "accounts", "settings"):
            setattr(self, f"{name}_frame", ctk.CTkFrame(self, corner_radius=0, fg_color="#111613"))

        tabs.build_sidebar(self)
        tabs.build_home_tab(self)
        extra_tabs.build_mods_tab(self)
        catalog_ui.build_catalog_tab(self)

        if packs_ui and hasattr(packs_ui, "build_packs_tab"):
            packs_ui.build_packs_tab(self)
        elif hasattr(extra_tabs, "build_modpacks_tab"):
            extra_tabs.build_modpacks_tab(self)

        coop_tab.build_coop_tab(self)

        for fn in dir(auth_ui):
            if fn.startswith("build_"):
                getattr(auth_ui, fn)(self)
                break

        if hasattr(extra_tabs, "build_settings_tab"):
            extra_tabs.build_settings_tab(self)

        tabs.build_bottom_bar(self)

        if hasattr(handlers, "sync_packs_dropdown"):
            handlers.sync_packs_dropdown(self)

        self.show_home()
        self.acc_status_lbl.configure(text="⚪ Offline Mode", text_color="#888888")
        self.refresh_mods_list()
        coop_tab.refresh_friends_list(self)
        self.apply_theme_colors()

        if HAS_DND:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", lambda e: handlers.process_files(self, self.tk.splitlist(e.data)))
            except Exception:
                pass

    @property
    def ram_gb(self):
        return int(self.ram_var.get())

    def set_active_account(self, name):
        if name:
            self.active_account = name
            self.current_account = name
            self.nick_entry.delete(0, "end")
            self.nick_entry.insert(0, name)
            self.acc_status_lbl.configure(text=f"🟢 {name}", text_color="#2ecc71")
        else:
            self.active_account = None
            self.current_account = None
            self.acc_status_lbl.configure(text="⚪ Offline Mode", text_color="#888888")

    def _switch_tab(self, btn, frame):
        for f in (self.home_frame, self.mods_frame, self.catalog_frame, self.packs_frame, self.coop_frame, self.accounts_frame, self.settings_frame):
            f.place_forget()
            f.grid_forget()
        for b in self.nav_btns.values():
            b.configure(fg_color="transparent")
        btn.configure(fg_color="#1d2b22")
        frame.grid(row=0, column=1, sticky="nsew")
        self.after(10, lambda: ui_theme.slide_up_reveal(frame))

    def show_home(self):
        self._switch_tab(self.btn_home, self.home_frame)

    def show_mods(self):
        self._switch_tab(self.btn_mods, self.mods_frame)
        self.refresh_mods_list()

    def show_catalog(self):
        self._switch_tab(self.btn_catalog, self.catalog_frame)
        if not self.cat_scroll.winfo_children():
            catalog_ui.run_search(self, reset=True)

    def show_packs(self):
        self._switch_tab(self.btn_packs, self.packs_frame)
        if packs_ui and hasattr(packs_ui, "refresh_packs_list"):
            packs_ui.refresh_packs_list(self)
        elif hasattr(extra_tabs, "refresh_packs_list"):
            extra_tabs.refresh_packs_list(self)

    def show_coop(self):
        self._switch_tab(self.btn_coop, self.coop_frame)
        coop_tab.refresh_friends_list(self)

    def show_accounts(self):
        self._switch_tab(self.btn_accounts, self.accounts_frame)
        for fn in ("refresh_accounts_tab", "refresh_accounts_list", "render_accounts", "update_accounts_ui"):
            if hasattr(auth_ui, fn):
                getattr(auth_ui, fn)(self)
                break

    def show_settings(self):
        self._switch_tab(self.btn_settings, self.settings_frame)

    def on_loader_change(self, loader):
        self.set_status(f"Mod loader: {loader}")

    def refresh_mods_list(self):
        if hasattr(extra_tabs, "refresh_mods_list"):
            extra_tabs.refresh_mods_list(self)

    def update_ram_label(self, val):
        if hasattr(self, "ram_val_lbl"):
            self.ram_val_lbl.configure(text=f"{int(val)} GB")

    def add_mod_dialog(self):
        paths = filedialog.askopenfilenames(filetypes=[("Minecraft Files", "*.jar *.zip")])
        if paths:
            handlers.process_files(self, paths)

    def upload_skin_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Skin", "*.png")])
        if path:
            dst = os.path.join(engine.MINECRAFT_DIR, "custom_skin.png")
            shutil.copy2(path, dst)
            self.update_skin_preview(dst)

    def update_skin_preview(self, path):
        if os.path.exists(path):
            self.skin_viewer.set_skin(path)
            self.skin_info_lbl.configure(text=os.path.basename(path))

    def set_max(self, val):
        self._max_prog = max(1, int(val))

    def set_status(self, text):
        self.after(0, lambda: self.status_label.configure(text=text))

    def set_progress(self, val):
        ratio = min(1.0, max(0.0, float(val) / float(getattr(self, "_max_prog", 100))))
        self.after(0, lambda: self.progress_bar.set(ratio))

    def reset_play_btn(self):
        self.is_launching = False
        ac, hv, tc = features_pro.get_accent()
        self.play_btn.configure(text="▶   PLAY MINECRAFT", state="normal", fg_color=ac, hover_color=hv, text_color=tc)

    def show_error(self, ver, err):
        self.reset_play_btn()
        self.set_status(f"Error ({ver})")
        messagebox.showerror(f"Launch Error ({ver})", str(err))

    def quick_join_server(self, ip):
        self.join_server_ip = ip
        self.start_launch_thread()

    def apply_theme_colors(self):
        ac, hv, tc = features_pro.get_accent()
        self.play_btn.configure(fg_color=ac, hover_color=hv, text_color=tc)
        self.progress_bar.configure(progress_color=ac)
        self.version_menu.btn.configure(fg_color=ac, hover_color=hv, text_color=tc)
        self.btn_skin_up.configure(fg_color=ac, hover_color=hv, text_color=tc)

    def start_launch_thread(self):
        if self.is_launching:
            return
        nick = self.nick_entry.get().strip()
        if not nick:
            messagebox.showerror("Error", "Enter username!")
            return
        self.active_account = nick
        self.current_account = nick
        self.is_launching = True
        self.play_btn.configure(text="LOADING...", state="disabled", fg_color="#555555")
        threading.Thread(target=engine.launch_task, args=(self,), daemon=True).start()

    def __getattr__(self, name):
        if name == "open_game_folder":
            return lambda: engine.open_folder(engine.MINECRAFT_DIR)
        if name == "open_installed_folder":
            return lambda: engine.open_folder(engine.get_active_mods_dir(self.pack_menu.get()))
        for mod in (packs_ui, auth_ui, handlers, extra_tabs):
            if mod and hasattr(mod, name):
                return lambda *a, **kw: getattr(mod, name)(self, *a, **kw)
        raise AttributeError(name)

if __name__ == "__main__":
    import splash_ui
    app = ProMinecraftLauncher()
    if sys.platform == "win32":
        app.state("zoomed")
        app.after(150, lambda: app.state("zoomed"))
    splash_ui.LauncherSplash(app, on_done=lambda: ui_theme.slide_up_reveal(app.home_frame, distance=55, steps=14, delay=15))
    app.mainloop()
