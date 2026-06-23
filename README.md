# ⬛ QR Generator Dashboard

A modern, full-screen QR code generator desktop app built with Python and CustomTkinter. Features a dark-themed dashboard UI with a live preview, color customization, and one-click export.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-blue?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat)

---

## Features

- **Full-screen dashboard** — top nav bar, scrollable sidebar, large centered QR preview
- **Live generation** — QR updates instantly on every setting change or Enter key press
- **Color customization** — 6 foreground and 6 background swatches with visual selection
- **Size control** — slider from 160 px to 500 px with live label
- **Error correction** — Low (7%), Medium (15%), Quartile (25%), High (30%)
- **Live stat cards** — resolution, error correction level, and colors displayed in real time
- **Auto-scaling preview** — QR resizes dynamically when the window is resized
- **Export options** — Save as PNG via file dialog, or copy to clipboard
- **Cross-platform** — works on Windows, macOS, and Linux

---

## Screenshots

> Coming soon — run the app and take a screenshot to add here!

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ajithramb/qr-generator-dashboard.git
cd qr-generator-dashboard
```

### 2. Install dependencies

```bash
pip install customtkinter qrcode[pil] pillow
```

> **Linux only:** If you get a `tkinter` error, install it via:
> ```bash
> sudo apt install python3-tk
> ```

### 3. Run the app

```bash
python qr_dashboard.py
```

---

## Usage

1. Type any **URL or text** into the input field in the sidebar
2. Press **Enter** or click **⚡ Generate QR Code**
3. Adjust **size**, **error correction**, and **colors** — preview updates live
4. Click **↓ Save PNG** to download, or **⧉ Copy** to copy to clipboard

---

## Project Structure

```
qr-generator-dashboard/
│
├── qr_dashboard.py     # Main app (single file, no extra modules needed)
└── README.md
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Modern dark-themed UI widgets |
| `qrcode[pil]` | QR code generation engine |
| `Pillow` | Image processing and display |

---

## How It Works

The app uses the `qrcode` library to generate QR codes from any text or URL, then renders the output as a `PIL` image. CustomTkinter handles the full GUI — a 320 px scrollable sidebar holds all controls, and the right panel shows a live, auto-scaled preview. Export uses Python's built-in `filedialog` for saving and platform-specific clipboard APIs for copying.

---

## Author

**Ajith Ram**
- GitHub: [@ajithram41-cricket](https://github.com/ajithram41-cricket)
- LinkedIn: [linkedin.com/in/ajith-ram](https://linkedin.com/in/ajith-ram)

---

## License

This project is licensed under the MIT License — feel free to use, modify, and distribute.
