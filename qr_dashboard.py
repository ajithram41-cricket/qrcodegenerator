import customtkinter as ctk
import qrcode
from PIL import Image, ImageTk
import os, sys, tempfile, subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Palette ────────────────────────────────────────────────────────────────────
BG_MAIN   = "#0f0f0f"
BG_SIDE   = "#161616"
BG_CARD   = "#1e1e1e"
BG_INPUT  = "#252525"
BORDER    = "#2a2a2a"
ACCENT    = "#3a5fd9"
ACCENT_HV = "#2e4dbf"
TEXT_PRI  = "#f0f0f0"
TEXT_SEC  = "#888888"
TEXT_MUT  = "#444444"
SUCCESS   = "#1D9E75"

FG_SWATCHES = [
    ("#000000", "Black"),
    ("#1D9E75", "Teal"),
    ("#185FA5", "Blue"),
    ("#993556", "Pink"),
    ("#534AB7", "Purple"),
    ("#993C1D", "Rust"),
]
BG_SWATCHES = [
    ("#ffffff", "White"),
    ("#F1EFE8", "Cream"),
    ("#E1F5EE", "Mint"),
    ("#E6F1FB", "Sky"),
    ("#EEEDFE", "Lavender"),
    ("#1a1a1a", "Dark"),
]
EC_OPTIONS = {
    "Low  · 7%":       qrcode.constants.ERROR_CORRECT_L,
    "Medium  · 15%":   qrcode.constants.ERROR_CORRECT_M,
    "Quartile  · 25%": qrcode.constants.ERROR_CORRECT_Q,
    "High  · 30%":     qrcode.constants.ERROR_CORRECT_H,
}


# ── Swatch ─────────────────────────────────────────────────────────────────────
class Swatch(ctk.CTkButton):
    def __init__(self, master, color, label, cmd):
        super().__init__(master, width=32, height=32, corner_radius=8,
                         text="", fg_color=color, hover_color=color,
                         border_width=2, border_color=color, command=cmd)
        self._col = color
        self._label = label

    def select(self):   self.configure(border_color="#ffffff")
    def deselect(self): self.configure(border_color=self._col)


# ── Stat card ──────────────────────────────────────────────────────────────────
def stat_card(parent, title, var):
    f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10,
                     border_width=1, border_color=BORDER)
    f.pack(fill="x", pady=(0, 8))
    ctk.CTkLabel(f, text=title, font=ctk.CTkFont(size=10),
                 text_color=TEXT_SEC).pack(anchor="w", padx=14, pady=(10, 0))
    ctk.CTkLabel(f, textvariable=var, font=ctk.CTkFont(size=14, weight="bold"),
                 text_color=TEXT_PRI).pack(anchor="w", padx=14, pady=(2, 10))
    return f


# ── App ────────────────────────────────────────────────────────────────────────
class QRDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QR Generator  ·  Dashboard")
        self.configure(fg_color=BG_MAIN)

        # Fullscreen
        self.after(0, lambda: self.state("zoomed"))
        self.minsize(1024, 640)

        self._fg_val = "#000000"
        self._bg_val = "#ffffff"
        self._qr_img: Image.Image | None = None
        self._tk_img = None
        self._fg_sw: list[Swatch] = []
        self._bg_sw: list[Swatch] = []

        # StringVars for stat cards
        self.sv_size   = ctk.StringVar(value="—")
        self.sv_ec     = ctk.StringVar(value="—")
        self.sv_fg     = ctk.StringVar(value="—")
        self.sv_bg     = ctk.StringVar(value="—")
        self.sv_status = ctk.StringVar(value="Enter a URL to generate your QR code")

        self._build()
        self.bind("<Configure>", self._on_resize)
        self._generate()

    # ── Layout ─────────────────────────────────────────────────────────────────
    def _build(self):
        # Top nav bar
        nav = ctk.CTkFrame(self, height=52, fg_color=BG_SIDE,
                           corner_radius=0, border_width=0)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        ctk.CTkLabel(nav, text="⬛  QR Dashboard",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_PRI).pack(side="left", padx=24)

        self.nav_status = ctk.CTkLabel(nav, textvariable=self.sv_status,
                                       font=ctk.CTkFont(size=12),
                                       text_color=TEXT_SEC)
        self.nav_status.pack(side="right", padx=24)

        # Separator line under nav
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0)
        sep.pack(fill="x", side="top")

        # Body: sidebar + preview
        body = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        self._build_preview(body)

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        sb = ctk.CTkFrame(parent, width=320, fg_color=BG_SIDE,
                          corner_radius=0, border_width=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Right border
        div = ctk.CTkFrame(parent, width=1, fg_color=BORDER, corner_radius=0)
        div.pack(side="left", fill="y")

        scroll = ctk.CTkScrollableFrame(sb, fg_color=BG_SIDE, corner_radius=0,
                                        scrollbar_button_color=BORDER,
                                        scrollbar_button_hover_color="#3a3a3a")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        pad = ctk.CTkFrame(scroll, fg_color=BG_SIDE, corner_radius=0)
        pad.pack(fill="both", expand=True, padx=20, pady=20)

        # ── Section: Input
        self._section_label(pad, "INPUT")

        ctk.CTkLabel(pad, text="URL or text", anchor="w",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(fill="x", pady=(0,4))
        self.url_var = ctk.StringVar(value="https://github.com/ajithramb")
        self.url_entry = ctk.CTkEntry(pad, textvariable=self.url_var, height=40,
                                      corner_radius=8, font=ctk.CTkFont(size=13),
                                      fg_color=BG_INPUT, border_color=BORDER,
                                      text_color=TEXT_PRI,
                                      placeholder_text="https://example.com")
        self.url_entry.pack(fill="x", pady=(0, 12))
        self.url_entry.bind("<Return>", lambda e: self._generate())

        ctk.CTkButton(pad, text="⚡  Generate QR Code", height=42, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=ACCENT, hover_color=ACCENT_HV,
                      command=self._generate).pack(fill="x", pady=(0, 20))

        # ── Section: Settings
        self._section_label(pad, "SETTINGS")

        # Size
        ctk.CTkLabel(pad, text="Size", anchor="w", font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC).pack(fill="x", pady=(0, 4))
        size_row = ctk.CTkFrame(pad, fg_color=BG_SIDE, corner_radius=0)
        size_row.pack(fill="x", pady=(0, 2))
        self.size_slider = ctk.CTkSlider(size_row, from_=160, to=500,
                                         number_of_steps=17, command=self._on_size)
        self.size_slider.set(320)
        self.size_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.size_lbl = ctk.CTkLabel(size_row, text="320 px", width=54,
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color=TEXT_PRI, anchor="e")
        self.size_lbl.pack(side="left")

        # Error correction
        ctk.CTkLabel(pad, text="Error correction", anchor="w",
                     font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(fill="x", pady=(12, 4))
        self.ec_var = ctk.StringVar(value="High  · 30%")
        ctk.CTkOptionMenu(pad, variable=self.ec_var, values=list(EC_OPTIONS.keys()),
                          height=38, corner_radius=8,
                          fg_color=BG_INPUT, button_color=BORDER,
                          button_hover_color="#3a3a3a", text_color=TEXT_PRI,
                          font=ctk.CTkFont(size=12),
                          command=lambda _: self._generate()).pack(fill="x", pady=(0, 20))

        # ── Section: Colors
        self._section_label(pad, "COLORS")

        self._color_row(pad, "Foreground", FG_SWATCHES, self._fg_sw, self._set_fg)
        self._color_row(pad, "Background", BG_SWATCHES, self._bg_sw, self._set_bg)

        # ── Section: Stats
        self._section_label(pad, "STATS", top=20)
        stat_card(pad, "Resolution",         self.sv_size)
        stat_card(pad, "Error Correction",   self.sv_ec)
        stat_card(pad, "Foreground Color",   self.sv_fg)
        stat_card(pad, "Background Color",   self.sv_bg)

        # ── Actions
        self._section_label(pad, "EXPORT", top=8)
        act = ctk.CTkFrame(pad, fg_color=BG_SIDE, corner_radius=0)
        act.pack(fill="x", pady=(4, 20))
        act.columnconfigure((0, 1), weight=1, uniform="col")

        self.copy_btn = ctk.CTkButton(act, text="⧉  Copy", height=38, corner_radius=8,
                                      font=ctk.CTkFont(size=12),
                                      fg_color=BG_CARD, hover_color="#2a2a2a",
                                      border_width=1, border_color=BORDER,
                                      text_color=TEXT_PRI, state="disabled",
                                      command=self._copy)
        self.copy_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.dl_btn = ctk.CTkButton(act, text="↓  Save PNG", height=38, corner_radius=8,
                                    font=ctk.CTkFont(size=12),
                                    fg_color=BG_CARD, hover_color="#2a2a2a",
                                    border_width=1, border_color=BORDER,
                                    text_color=TEXT_PRI, state="disabled",
                                    command=self._download)
        self.dl_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _section_label(self, parent, text, top=0):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_MUT).pack(anchor="w", pady=(top, 8))

    def _color_row(self, parent, label, swatches, swatch_list, cmd):
        ctk.CTkLabel(parent, text=label, anchor="w", font=ctk.CTkFont(size=11),
                     text_color=TEXT_SEC).pack(fill="x", pady=(0, 6))
        row = ctk.CTkFrame(parent, fg_color=BG_SIDE, corner_radius=0)
        row.pack(fill="x", pady=(0, 14))
        for color, lbl in swatches:
            sw = Swatch(row, color, lbl, lambda c=color, f=cmd: f(c))
            sw.pack(side="left", padx=(0, 6))
            swatch_list.append(sw)
        swatch_list[0].select()

    # ── Preview area ───────────────────────────────────────────────────────────
    def _build_preview(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_MAIN, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        # Preview card
        self.preview_card = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=16,
                                         border_width=1, border_color=BORDER)
        self.preview_card.place(relx=0.5, rely=0.5, anchor="center")

        self.ph_label = ctk.CTkLabel(self.preview_card,
                                     text="⬛\n\nEnter a URL and hit Generate",
                                     font=ctk.CTkFont(size=14), text_color=TEXT_MUT,
                                     justify="center")
        self.ph_label.pack(padx=60, pady=60)

        self.qr_lbl = ctk.CTkLabel(self.preview_card, text="")

        # Info bar below card
        self.info_bar = ctk.CTkFrame(right, fg_color=BG_SIDE,
                                     corner_radius=10, border_width=1,
                                     border_color=BORDER)
        self.info_bar.place(relx=0.5, rely=0.88, anchor="center")

        self.info_var = ctk.StringVar(value="")
        ctk.CTkLabel(self.info_bar, textvariable=self.info_var,
                     font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(padx=20, pady=8)

        self._right = right

    # ── Resize handler ─────────────────────────────────────────────────────────
    def _on_resize(self, event):
        if self._qr_img:
            self._show_qr(self._qr_img)

    # ── Colour setters ─────────────────────────────────────────────────────────
    def _set_fg(self, color):
        self._fg_val = color
        for sw in self._fg_sw:
            sw.select() if sw._col == color else sw.deselect()
        self._generate()

    def _set_bg(self, color):
        self._bg_val = color
        for sw in self._bg_sw:
            sw.select() if sw._col == color else sw.deselect()
        self._generate()

    def _on_size(self, val):
        px = int(round(val / 20) * 20)
        self.size_lbl.configure(text=f"{px} px")
        self._generate()

    # ── QR generation ──────────────────────────────────────────────────────────
    def _generate(self):
        url = self.url_var.get().strip()
        if not url:
            self._clear_preview()
            return

        size = int(round(self.size_slider.get() / 20) * 20)
        ec   = EC_OPTIONS[self.ec_var.get()]
        fg   = self._fg_val
        bg   = self._bg_val

        try:
            qr = qrcode.QRCode(version=1, error_correction=ec,
                               box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color=fg, back_color=bg).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            self._qr_img = img

            self.sv_size.set(f"{size} × {size} px")
            self.sv_ec.set(self.ec_var.get())
            self.sv_fg.set(fg.upper())
            self.sv_bg.set(bg.upper())

            self._show_qr(img)
            self.sv_status.set(f"✓  Generated  ·  {size}×{size} px  ·  {self.ec_var.get()}")
            self.copy_btn.configure(state="normal")
            self.dl_btn.configure(state="normal")

        except Exception as e:
            self.sv_status.set(f"Error: {e}")

    def _show_qr(self, img: Image.Image):
        # Scale to fit available preview area (max 70% of right panel)
        rw = self._right.winfo_width()
        rh = self._right.winfo_height()
        if rw < 100 or rh < 100:
            rw, rh = 700, 600

        max_px = min(int(rw * 0.65), int(rh * 0.70), 520)
        max_px = max(max_px, 200)

        display = img.copy()
        display.thumbnail((max_px, max_px), Image.LANCZOS)
        dw, dh = display.size

        self._tk_img = ImageTk.PhotoImage(display)
        self.ph_label.pack_forget()
        self.qr_lbl.configure(image=self._tk_img, text="")
        self.qr_lbl.pack(padx=32, pady=32)

        self.info_var.set(f"{dw} × {dh} px  ·  {self._fg_val.upper()} on {self._bg_val.upper()}")

    def _clear_preview(self):
        self.qr_lbl.pack_forget()
        self.ph_label.pack(padx=60, pady=60)
        self._qr_img = None
        self.copy_btn.configure(state="disabled")
        self.dl_btn.configure(state="disabled")

    # ── Export ─────────────────────────────────────────────────────────────────
    def _download(self):
        if not self._qr_img:
            return
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG image", "*.png")],
                                            initialfile="qrcode.png")
        if path:
            self._qr_img.save(path)
            self.sv_status.set(f"✓  Saved → {os.path.basename(path)}")

    def _copy(self):
        if not self._qr_img:
            return
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            self._qr_img.save(tmp.name)
            tmp.close()
            if sys.platform == "darwin":
                subprocess.run(["osascript", "-e",
                    f'set the clipboard to (read (POSIX file "{tmp.name}") as TIFF picture)'])
            elif sys.platform == "win32":
                import win32clipboard, win32con
                from io import BytesIO
                buf = BytesIO()
                self._qr_img.convert("RGB").save(buf, "BMP")
                data = buf.getvalue()[14:]
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_DIB, data)
                win32clipboard.CloseClipboard()
            else:
                subprocess.run(["xclip", "-selection", "clipboard",
                                "-t", "image/png", "-i", tmp.name])
            self.sv_status.set("✓  Copied to clipboard")
        except Exception:
            self.sv_status.set("Copy unavailable — use Save PNG instead")


if __name__ == "__main__":
    app = QRDashboard()
    app.mainloop()
