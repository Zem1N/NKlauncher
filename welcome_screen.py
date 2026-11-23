import customtkinter as ctk
import accounts

def show_welcome_overlay(app):
    overlay = ctk.CTkFrame(app, fg_color="#121212", corner_radius=0)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
    card = ctk.CTkFrame(overlay, width=440, fg_color="#1c1c1c", corner_radius=20, border_width=2, border_color="#2ecc71")
    card.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(card, text="NKLauncher", font=ctk.CTkFont(family="Arial Black", size=32, weight="bold"), text_color="#2ecc71").pack(pady=(30, 4), padx=45)
    ctk.CTkLabel(card, text="WELCOME BACK • CHOOSE OR CREATE ACCOUNT", font=ctk.CTkFont(size=11, weight="bold"), text_color="#888888").pack(pady=(0, 20))
    saved = accounts.load_accounts()
    if saved:
        ctk.CTkLabel(card, text="SAVED PROFILES:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaaaaa").pack(anchor="w", padx=35)
        for acc in (list(saved.keys())[:4] if isinstance(saved, dict) else saved[:4]):
            name = acc if isinstance(acc, str) else acc.get("name", "Player")
            ctk.CTkButton(card, text=f"🟢  Continue as {name}", height=38, corner_radius=10, fg_color="#262626", hover_color="#2ecc71", font=ctk.CTkFont(size=13, weight="bold"), command=lambda n=name: [app.set_active_account(n), overlay.destroy()]).pack(fill="x", padx=35, pady=4)
    ctk.CTkLabel(card, text="CREATE NEW ACCOUNT / OFFLINE NICK:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#aaaaaa").pack(anchor="w", padx=35, pady=(14, 4))
    nick_ent = ctk.CTkEntry(card, placeholder_text="Enter your nickname...", height=40, font=ctk.CTkFont(size=14)); nick_ent.pack(fill="x", padx=35, pady=(0, 12))
    def create_and_enter():
        n = nick_ent.get().strip()
        if not n: return
        accounts.add_offline_account(n); app.set_active_account(n); overlay.destroy()
    nick_ent.bind("<Return>", lambda _: create_and_enter())
    ctk.CTkButton(card, text="CREATE & ENTER LAUNCHER ▶", height=44, corner_radius=12, fg_color="#2ecc71", hover_color="#27ae60", text_color="#111111", font=ctk.CTkFont(size=14, weight="bold"), command=create_and_enter).pack(fill="x", padx=35, pady=(0, 10))
    ctk.CTkButton(card, text="Skip (Guest Mode)", height=30, fg_color="transparent", text_color="#777777", hover_color="#222222", command=overlay.destroy).pack(pady=(0, 22))
