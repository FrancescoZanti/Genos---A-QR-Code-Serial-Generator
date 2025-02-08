import os
import qrcode
from PIL import Image, ImageDraw

# Definisci il filtro di ridimensionamento in base alla versione di Pillow
try:
    resample_filter = Image.Resampling.LANCZOS
except AttributeError:
    resample_filter = Image.LANCZOS

def genera_adesivi(
    logo_path="logo.png",
    seriali_file="seriali.txt",
    output_dir="adesivi_output",
    combina_in_a4=True
):
    # Dimensioni approssimative in pixel per A6 (300 dpi): 1240x1748
    larghezza, altezza = 1240, 1748

    # Dimensioni approssimative in pixel per A4 (300 dpi): 2480x3508
    larghezza_a4, altezza_a4 = 2480, 3508

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(seriali_file, "r", encoding="utf-8") as f:
        seriali = [line.strip() for line in f if line.strip()]

    # Per salvare i percorsi dei file dei singoli adesivi
    adesivi_generati = []

    for i, sr in enumerate(seriali, start=1):
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(sr)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Forza una dimensione fissa, ad esempio 300×300
        qr_w_fixed, qr_h_fixed = 300, 300
        qr_img = qr_img.resize((qr_w_fixed, qr_h_fixed), resample_filter)

        adesivo = Image.new("RGB", (larghezza, altezza), "white")
        draw = ImageDraw.Draw(adesivo)

        if os.path.isfile(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo_w, logo_h = logo.size
            max_logo_width = int(larghezza * 1.8)
            if logo_w > max_logo_width:
                ratio = max_logo_width / float(logo_w)
                logo = logo.resize((max_logo_width, int(logo_h * ratio)))
            logo_w, logo_h = logo.size
            logo_x = (larghezza - logo_w) // 2
            adesivo.paste(logo, (logo_x, 50), logo)

        qr_w, qr_h = qr_img.size
        qr_x = (larghezza - qr_w) // 2
        qr_y = int(altezza * 0.55)  # Spostato più in basso
        qr_box = (qr_x, qr_y, qr_x + qr_w, qr_y + qr_h)
        if qr_img.mode != "RGBA":
            qr_img = qr_img.convert("RGBA")
        adesivo.paste(qr_img, qr_box, qr_img)

        output_path = os.path.join(output_dir, f"adesivo_{i}.png")
        adesivo.save(output_path)
        adesivi_generati.append(output_path)

    if combina_in_a4:
        combina_adesivi_in_a4(adesivi_generati, output_dir, larghezza, altezza, larghezza_a4, altezza_a4)

    print(f"Adesivi generati in: {output_dir}")

def combina_adesivi_in_a4(adesivi_paths, output_dir, larghezza, altezza, larghezza_a4, altezza_a4):
    per_pagina = 4
    for idx in range(0, len(adesivi_paths), per_pagina):
        subset = adesivi_paths[idx:idx + per_pagina]
        foglio = Image.new("RGB", (larghezza_a4, altezza_a4), "white")
        posizioni = [(0, 0), (larghezza, 0), (0, altezza), (larghezza, altezza)]

        for i, path in enumerate(subset):
            adesivo = Image.open(path)
            foglio.paste(adesivo, posizioni[i])

        # Indicatori di taglio più sottili e discreti
        draw = ImageDraw.Draw(foglio)
        # Linea verticale al centro (piccola)
        draw.line((larghezza, 10, larghezza, altezza_a4 - 10), fill="gray", width=1)
        # Linea orizzontale al centro (piccola)
        draw.line((10, altezza, larghezza_a4 - 10, altezza), fill="gray", width=1)

        output_a4 = os.path.join(output_dir, f"adesivi_a4_{idx//4+1}.png")
        foglio.save(output_a4)

if __name__ == "__main__":
    genera_adesivi(combina_in_a4=True)