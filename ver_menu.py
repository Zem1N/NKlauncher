import customtkinter as ctk
import engine

class ScrollableVersionMenu(ctk.CTkFrame):
    def __init__(self, master, values, command=None, width=145, height=38):
        super().__init__(master, fg_color="transparent", width=width, height=height)
        self.groups = getattr(engine, "VERSION_GROUPS", {"release": values or ["26.3"]})
        self.active_tab = "release"
        self.values = self.groups.get("release") or values or ["26.3"]
        self.current = next(iter(self.values))
        self.command = command
        self.popup = None

        self.btn = ctk.CTkButton(
            self,
            text=f"{self.current}  ▼",
            width=width,
            height=height,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2ecc71",
            text_color="#111111",
            hover_color="#27ae60",
            command=self.toggle
        )
        self.btn.pack()

        top = self.winfo_toplevel()
        top.bind("<Button-1>", self._on_global_click, add="+")
        top.bind("<Unmap>", lambda _: self.close(), add="+")
        top.bind("<Configure>", lambda _: self.close(), add="+")

    def get(self):
        return self.current

    def set(self, val):
        self.current = val
        self.btn.configure(text=f"{val}  ▼")

    def close(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None

    def _on_global_click(self, event):
        if not self.popup or not self.popup.winfo_exists():
            return
        w = event.widget
        if w is self.btn or str(w).startswith(str(self.btn)) or str(w).startswith(str(self.popup)):
            return
        self.close()

    def toggle(self):
        if self.popup and self.popup.winfo_exists():
            self.close()
            return

        self.popup = ctk.CTkToplevel(self)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        x, y = self.winfo_rootx() - 45, self.winfo_rooty() - 355
        self.popup.geometry(f"250x345+{max(10, x)}+{max(10, y)}")

        box = ctk.CTkFrame(self.popup, fg_color="#151c18", border_width=2, border_color="#2ecc71", corner_radius=12)
        box.pack(fill="both", expand=True)

        # Вкладки категорий версий: Release | Snapshot | Beta | Alpha
        tabs_row = ctk.CTkFrame(box, fg_color="#1d2721", corner_radius=8)
        tabs_row.pack(fill="x", padx=8, pady=(8, 6))

        tab_defs = [
            ("release", "Release"),
            ("snapshot", "Snap"),
            ("old_beta", "Beta"),
            ("old_alpha", "Alpha")
        ]
        tab_btns = {}

        qvar = ctk.StringVar()
        ent = ctk.CTkEntry(
            box,
            textvariable=qvar,
            placeholder_text="Search version...",
            height=30,
            fg_color="#1d2721",
            border_color="#28382f"
        )
        ent.pack(fill="x", padx=8, pady=(0, 6))
        ent.focus_set()

        scr = ctk.CTkScrollableFrame(box, fg_color="#19221d", corner_radius=8)
        scr.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        def draw(*_):
            for w in scr.winfo_children():
                w.destroy()
            q = qvar.get().strip().lower()
            src = self.groups.get(self.active_tab, [])
            filtered = [x for x in src if q in x.lower()][:150]
            if not filtered:
                ctk.CTkLabel(scr, text="No versions found", text_color="#8fa396", font=ctk.CTkFont(size=12)).pack(pady=20)
                return
            for v in filtered:
                cur = (v == self.current)
                ctk.CTkButton(
                    scr,
                    text=v,
                    height=28,
                    anchor="w",
                    fg_color="#2ecc71" if cur else "transparent",
                    hover_color="#27ae60" if cur else "#26332c",
                    text_color="#111111" if cur else "#ffffff",
                    font=ctk.CTkFont(size=12, weight="bold" if cur else "normal"),
                    command=lambda val=v: self.pick(val)
                ).pack(fill="x", pady=1)

        def switch_cat(cat_key):
            self.active_tab = cat_key
            for k, b in tab_btns.items():
                active = (k == cat_key)
                b.configure(
                    fg_color="#2ecc71" if active else "transparent",
                    text_color="#111111" if active else "#cde0d4"
                )
            draw()

        for k, label in tab_defs:
            active = (k == self.active_tab)
            b = ctk.CTkButton(
                tabs_row,
                text=label,
                width=52,
                height=26,
                corner_radius=6,
                fg_color="#2ecc71" if active else "transparent",
                hover_color="#27ae60" if active else "#26332c",
                text_color="#111111" if active else "#cde0d4",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda key=k: switch_cat(key)
            )
            b.pack(side="left", expand=True, padx=2, pady=2)
            tab_btns[k] = b

        qvar.trace_add("write", draw)
        draw()

    def pick(self, val):
        self.set(val)
        self.close()
        if self.command:
            self.command(val)
