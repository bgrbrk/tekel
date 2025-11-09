# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

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

def big_button(master, text, bg, fg="white", cmd=None, width=20, height=5):
    return tk.Button(master, text=text, bg=bg, fg=fg,
                     font=("Segoe UI", 18, "bold"), height=height, width=width,
                     command=cmd, bd=2, relief="raised", cursor="hand2")

def currency_line(kurlar: dict):
    try:
        usd = float(kurlar.get("USD",{}).get("rate_to_tl",0))
        eur = float(kurlar.get("EUR",{}).get("rate_to_tl",0))
        gbp = float(kurlar.get("GBP",{}).get("rate_to_tl",0))
        if usd<=0 or eur<=0 or gbp<=0:
            return "Kur yok"
        return f"1 USD = {1/usd:.2f} TL | 1 EUR = {1/eur:.2f} TL | 1 GBP = {1/gbp:.2f} TL"
    except Exception:
        return "Kur yok"
