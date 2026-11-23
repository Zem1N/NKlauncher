import random
import customtkinter as ctk
import lang, ui_theme

C = ui_theme.PALETTE

class LauncherSplash(ctk.CTkFrame):
    def __init__(self, master, on_done=None):
        super().__init__(master, fg_color=C["bg"], corner_radius=0)
        self.on_done = on_done
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lift()

        card = ctk.CTkFrame(
            self,
            width=540,
            height=300,
            fg_color=C["card"],
            corner_radius=18,
            border_width=2,
            border_color=C["accent"]
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        logo_row = ctk.CTkFrame(card, fg_color="transparent")
        logo_row.pack(pady=(34, 6))
        ctk.CTkLabel(
            logo_row,
            text="NK",
            font=ctk.CTkFont("Arial Black", 36, "bold"),
            text_color=C["accent"]
        ).pack(side="left")
        ctk.CTkLabel(
            logo_row,
            text="Launcher",
            font=ctk.CTkFont("Arial Black", 36, "bold"),
            text_color="#ffffff"
        ).pack(side="left")

        ctk.CTkLabel(
            card,
            text="PRO MINECRAFT EDITION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["accent"]
        ).pack(pady=(0, 18))

        tip_box = ctk.CTkFrame(
            card,
            fg_color=C["pill"],
            corner_radius=12,
            border_width=1,
            border_color=C["border"]
        )
        tip_box.pack(fill="x", padx=32, pady=(0, 18))

        tips = lang.get_tips() if hasattr(lang, "get_tips") else [
            "Tip: Switch Modrinth and CurseForge right in the Catalog tab!"
        ]
        self.tip_lbl = ctk.CTkLabel(
            tip_box,
            text=random.choice(tips),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#d0e3d7",
            wraplength=440,
            justify="center"
        )
        self.tip_lbl.pack(padx=14, pady=12)

        self.step = 0
        self.stages = (
            "Loading UI modules...",
            "Checking modpack profiles...",
            "Initializing 3D Skin Studio...",
            "Connecting to Modrinth & CurseForge...",
            "Ready!"
        )
        self.status_lbl = ctk.CTkLabel(
            card,
            text=self.stages,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["muted"]
        )
        self.status_lbl.pack(pady=(0, 6))

        self.bar = ctk.CTkProgressBar(
            card,
            width=440,
            height=10,
            corner_radius=5,
            fg_color="#111814",
            progress_color=C["accent"]
        )
        self.bar.set(0.0)
        self.bar.pack(pady=(0, 20))

        self.after(40, self._animate)

    def _animate(self):
        self.step += 1
        prog = min(1.0, self.step / 100.0)
        self.bar.set(prog)

        idx = min(len(self.stages) - 1, int(prog * len(self.stages)))
        self.status_lbl.configure(text=self.stages[idx])

        if self.step == 50 and hasattr(lang, "get_tips"):
            tips = lang.get_tips()
            if len(tips) > 1:
                cur = self.tip_lbl.cget("text")
                others = [t for t in tips if t != cur]
                if others:
                    self.tip_lbl.configure(text=random.choice(others))

        if self.step < 100:
            self.after(32, self._animate)
        else:
            self.after(250, self._finish)

    def _finish(self):
        self.destroy()
        if self.on_done:
            self.on_done()
