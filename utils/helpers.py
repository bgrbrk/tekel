# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

# ------------------------------- #
#  GENEL GÖRÜNÜM VE STİL AYARI   #
# ------------------------------- #
def setup_style(root: tk.Tk):
    try:
        root.tk.call('tk', 'scaling', 1.4)
    except Exception:
        pass
    root.option_add("*Font", ("Segoe UI", 12))
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview", rowheight=38, font=("Segoe UI", 12))
    style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"))


# ------------------------------- #
#   ANA EKRAN BÜYÜK BUTONLAR      #
# ------------------------------- #
def big_button(master, text, bg, fg="white", cmd=None, width=20, height=5):
    return tk.Button(
        master,
        text=text,
        bg=bg,
        fg=fg,
        font=("Segoe UI", 18, "bold"),
        height=height,
        width=width,
        command=cmd,
        bd=2,
        relief="raised",
        cursor="hand2"
    )

def currency_line(kurlar):
    """
    Kurların GUI'de düzgün ve renkli gösterilmesi için geliştirilmiş versiyon.
    - database.son_kurlar() [(code, rate), ...] veya eski dict formatlarını destekler.
    - Kurlar TL cinsine çevrilerek "💵 USD = 35.70 TL" gibi gösterilir.
    """
    try:
        # 🔹 Eğer veriler liste şeklindeyse
        if isinstance(kurlar, list):
            valid = [(c, r) for c, r in kurlar if r and float(r) > 0]
            if not valid:
                return "Kur yok"

            formatted = []
            for code, rate in valid:
                # 💵 💶 💷 simgelerini eşleştir
                symbol = ""
                if "USD" in code: symbol = "💵"
                elif "EUR" in code: symbol = "💶"
                elif "GBP" in code: symbol = "💷"

                formatted.append(f"{symbol} {code.replace(symbol, '').strip()} = {1/float(rate):.2f} TL")

            return " | ".join(formatted)

        # 🔹 Eğer sözlük formatındaysa (eski sistemle uyumlu)
        elif isinstance(kurlar, dict):
            usd = float(kurlar.get("$", {}).get("rate_to_tl", 0))
            eur = float(kurlar.get("€", {}).get("rate_to_tl", 0))
            gbp = float(kurlar.get("£", {}).get("rate_to_tl", 0))
            if usd <= 0 or eur <= 0 or gbp <= 0:
                return "Kur yok"
            return f"💵 USD={1/usd:.2f} TL | 💶 EUR={1/eur:.2f} TL | 💷 GBP={1/gbp:.2f} TL"

        else:
            return "Kur yok"

    except Exception as e:
        print("❌ currency_line hata:", e)
        return "Kur yok"

