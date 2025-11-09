# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from utils.barcode_reader import fatura_qr_coz
import database

class PurchaseScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=8)
        self.on_back = on_back; self.items = []
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="ALIŞ (FATURA/QR)", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        entry = ttk.Frame(self); entry.grid(row=1, column=0, sticky="ew", pady=6)
        ttk.Label(entry, text="Fatura QR/Payload:").pack(side="left")
        self.e_payload = ttk.Entry(entry, width=60); self.e_payload.pack(side="left", padx=6, expand=True, fill="x")
        tk.Button(entry, text="Yükle", bg="#17a2b8", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._parse).pack(side="left", padx=6)

        cols = ("BARKOD","ÜRÜN","ADET","FİYAT","KDV","KATEGORİ")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=120, anchor="w")
        self.tree.grid(row=2, column=0, sticky="nsew", pady=6)

        bottom = ttk.Frame(self); bottom.grid(row=3, column=0, sticky="ew")
        ttk.Label(bottom, text="Toptancı ID:").pack(side="left")
        self.e_sup = ttk.Entry(bottom, width=8); self.e_sup.pack(side="left", padx=6)
        tk.Button(bottom, text="Kaydet", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._save).pack(side="right")

        self.columnconfigure(0, weight=1); self.rowconfigure(2, weight=1)

    def _parse(self):
        payload = self.e_payload.get().strip()
        if not payload: messagebox.showwarning("Eksik", "Payload giriniz."); return
        self.items = fatura_qr_coz(payload)
        for i in self.tree.get_children(): self.tree.delete(i)
        for it in self.items:
            self.tree.insert("", "end", values=(it["barcode"], it["name"], it["qty"], it["price"], it["kdv"], it["category"]))

    def _save(self):
        if not self.items: messagebox.showwarning("Boş", "Listede ürün yok."); return
        try: sid = int(self.e_sup.get().strip())
        except Exception: sid = 1
        total = sum(it["qty"]*it["price"] for it in self.items)
        pid = database.satınalma_kaydet_ve_cari_guncelle(sid, self.items, total)
        messagebox.showinfo("Alış", f"Alış kaydedildi. Fatura #{pid}")
        self.items.clear(); [self.tree.delete(i) for i in self.tree.get_children()]
