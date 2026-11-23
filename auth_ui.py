from tkinter import messagebox
import customtkinter as ctk
import accounts, ui_theme

C = ui_theme.PALETTE

def build_accounts_tab(app):
    app.accounts_frame.configure(fg_color=C["bg"])
    app.accounts_frame.grid_columnconfigure(0, weight=1)
    app.accounts_frame.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        app.accounts_frame,
        text="PROFILES & ACCOUNTS",
        font=ctk.CTkFont(family="Arial Black", size=22, weight="bold"),
        text_color="#ffffff"
    ).grid(row=0, column=0, padx=35, pady=(26, 15), sticky="w")

    main_area = ctk.CTkFrame(app.accounts_frame, fg_color="transparent")
    main_area.grid(row=1, column=0, padx=35, pady=(0, 30), sticky="nsew")
    main_area.grid_columnconfigure(0, weight=1)
    main_area.grid_rowconfigure(0, weight=1)

    # Left column: saved profiles
    left_card = ctk.CTkFrame(main_area, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    left_card.grid(row=0, column=0, padx=(0, 15), sticky="nsew")

    ctk.CTkLabel(
        left_card,
        text="YOUR ACCOUNTS (CLICK SELECT TO CHOOSE)",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=C["muted"]
    ).pack(anchor="w", padx=20, pady=(15, 10))

    app.acc_scroll = ctk.CTkScrollableFrame(left_card, fg_color="transparent")
    app.acc_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))

    # Right column: login / registration form
    right_card = ctk.CTkFrame(main_area, width=320, corner_radius=16, fg_color=C["card"], border_width=1, border_color=C["border"])
    right_card.grid(row=0, column=1, sticky="ns")
    right_card.grid_propagate(False)

    ctk.CTkLabel(
        right_card,
        text="AUTHORIZATION",
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color=C["accent"]
    ).pack(pady=(25, 15))

    app.acc_nick_entry = ctk.CTkEntry(
        right_card,
        placeholder_text="Username",
        height=40,
        corner_radius=10,
        fg_color=C["input"],
        border_color=C["border"],
        font=ctk.CTkFont(size=13)
    )
    app.acc_nick_entry.pack(fill="x", padx=25, pady=(0, 10))

    app.acc_pwd_entry = ctk.CTkEntry(
        right_card,
        placeholder_text="Password (if set)",
        show="*",
        height=40,
        corner_radius=10,
        fg_color=C["input"],
        border_color=C["border"],
        font=ctk.CTkFont(size=13)
    )
    app.acc_pwd_entry.pack(fill="x", padx=25, pady=(0, 20))

    def do_login():
        nick = app.acc_nick_entry.get().strip()
        pwd = app.acc_pwd_entry.get()
        accs = accounts.load_accounts()

        if not nick:
            messagebox.showwarning("Login", "Enter a username or select a profile from the list on the left!")
            return
        if nick not in accs:
            messagebox.showerror("Error", f"Account '{nick}' not found. Click 'CREATE ACCOUNT'!")
            return
        if accounts.verify_password(nick, pwd):
            app.acc_pwd_entry.delete(0, "end")
            app.set_active_account(nick)
            app.show_home()
        else:
            messagebox.showerror("Error", "Incorrect password!")

    def do_create():
        try:
            created = accounts.register_account(app.acc_nick_entry.get(), app.acc_pwd_entry.get())
            app.acc_pwd_entry.delete(0, "end")
            refresh_accounts_tab(app)
            app.set_active_account(created)
            app.show_home()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ctk.CTkButton(
        right_card,
        text="LOGIN",
        height=44,
        corner_radius=10,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=C["accent"],
        text_color="#09130c",
        hover_color=C["hover"],
        command=do_login
    ).pack(fill="x", padx=25, pady=(0, 10))

    ctk.CTkButton(
        right_card,
        text="CREATE ACCOUNT",
        height=40,
        corner_radius=10,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color="#26332c",
        hover_color="#314239",
        command=do_create
    ).pack(fill="x", padx=25, pady=(0, 20))

    ctk.CTkButton(
        right_card,
        text="Switch to Offline Mode",
        height=38,
        corner_radius=8,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C["input"],
        hover_color="#25332b",
        command=lambda: [app.set_active_account(None), app.show_home()]
    ).pack(side="bottom", fill="x", padx=25, pady=20)

    refresh_accounts_tab(app)

def refresh_accounts_tab(app):
    for w in app.acc_scroll.winfo_children():
        w.destroy()
    accs = accounts.load_accounts()
    if not accs:
        ctk.CTkLabel(
            app.acc_scroll,
            text="No saved accounts yet.\nEnter a username on the right and click 'CREATE ACCOUNT'.",
            text_color=C["muted"],
            font=ctk.CTkFont(size=13)
        ).pack(pady=50)
        return

    for name in accs:
        row = ctk.CTkFrame(app.acc_scroll, fg_color=C["pill"], corner_radius=10, border_width=1, border_color=C["border"])
        row.pack(fill="x", pady=5, padx=5)
        lock = "🔒 " if accounts.has_password(name) else "👤 "
        ctk.CTkLabel(row, text=f"{lock}{name}", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15, pady=12)

        def select_profile(n=name):
            app.acc_nick_entry.delete(0, "end")
            app.acc_nick_entry.insert(0, n)
            app.acc_pwd_entry.delete(0, "end")
            if not accounts.has_password(n):
                app.set_active_account(n)
                app.show_home()
            else:
                app.acc_pwd_entry.focus()

        def del_click(n=name):
            if messagebox.askyesno("Delete Account", f"Delete account '{n}' and all its saved worlds?"):
                accounts.delete_account(n)
                if app.current_account == n:
                    app.set_active_account(None)
                refresh_accounts_tab(app)

        ctk.CTkButton(row, text="Delete", width=75, height=30, fg_color="#c0392b", hover_color="#e74c3c", command=del_click).pack(side="right", padx=10)
        ctk.CTkButton(row, text="Select", width=85, height=30, font=ctk.CTkFont(size=12, weight="bold"), fg_color=C["accent"], text_color="#09130c", hover_color=C["hover"], command=select_profile).pack(side="right", padx=5)
