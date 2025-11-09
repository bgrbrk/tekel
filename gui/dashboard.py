# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from utils.helpers import big_button, currency_line
import database

class Dashboard(ttk.Frame):
    def __init__(self, master, on_nav, user):
        super().__init__(master, padding=12)
        self.on_nav = on_nav
        self.user = user
        self._build()
        self.after(1000, self._load_rates)

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew", pady=(0,10))
        ttk.Label(top, text=f"Hoş geldiniz, {self.user['username']}", font=("Segoe UI",22,"bold")).pack(side="left")
        self.kur_lbl = ttk.Label(top, text="Kurlar yükleniyor...", font=("Segoe UI", 14))
        self.kur_lbl.pack(side="right")

        grid = ttk.Frame(self); grid.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        cols = 4
        buttons = [
            ("🛒 Satış", "#28a745", lambda: self.on_nav("sales")),
            ("📥 Alış (Fatura/QR)", "#17a2b8", lambda: self.on_nav("purchase")),
            ("📦 Stok", "#6c757d", lambda: self.on_nav("stock")),
            ("🧮 Sayım", "#20c997", lambda: self.on_nav("count")),
            ("🤝 Toptancılar", "#ffc107", lambda: self.on_nav("suppliers")),
            ("💵 Kasa", "#007bff", lambda: self.on_nav("cashier")),
            ("⚙️ Yönetici", "#343a40", lambda: self.on_nav("admin")),
            ("⏻ Çıkış", "#dc3545", lambda: self.on_nav("exit")),
        ]
        for i, (text, color, cmd) in enumerate(buttons):
            r, c = divmod(i, cols)
            big_button(grid, text, color, cmd=cmd, width=18, height=4).grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
        for i in range(cols): grid.columnconfigure(i, weight=1, uniform="col")
        for i in range((len(buttons)+cols-1)//cols): grid.rowconfigure(i, weight=1, uniform="row")
        self.columnconfigure(0, weight=1); self.rowconfigure(1, weight=1)

    def _load_rates(self):
        self.kur_lbl.config(text=currency_line(database.son_kurlar()))
