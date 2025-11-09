# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

CATEGORIES = ["Alkollü","Alkolsüz","Sigara","Market"]

class StockScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self._build(); self._load()

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="STOK YÖNETİMİ", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        cols = ("BARKOD","ÜRÜN","STOK","FİYAT","TOPTANCI","ID")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c in cols: self.tree.heading(c, text=c); self.tree.column(c, width=140, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=6)

        btn_fr = ttk.Frame(self); btn_fr.grid(row=2, column=0, sticky="ew")
        tk.Button(btn_fr, text="Ürün Ekle/Düzenle", bg="#17a2b8", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._open_form).pack(side="left", padx=6)
        tk.Button(btn_fr, text="Stok Raporu (Barkod + Tarih)", bg="#6c757d", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._open_report).pack(side="left", padx=6)

        self.columnconfigure(0, weight=1); self.rowconfigure(1, weight=1)

    def _load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for bc,name,st,sp,pid,sname in database.tree_rows_for_stock():
            self.tree.insert("", "end", values=(bc,name,st,sp,sname,pid))

    def _open_form(self):
        win = tk.Toplevel(self); win.title("Ürün Formu")
        ttk.Label(win, text="Barkod:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        e_bar = ttk.Entry(win, width=30, justify="left"); e_bar.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="Ad:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        e_name = ttk.Entry(win, width=30, justify="left"); e_name.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="Fiyat (TL):").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        e_price = ttk.Entry(win, width=30, justify="left"); e_price.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="KDV (%):").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        e_kdv = ttk.Entry(win, width=30, justify="left"); e_kdv.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="Kategori:").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        cmb_cat = ttk.Combobox(win, values=CATEGORIES, state="readonly", width=28, justify="left")
        cmb_cat.grid(row=4, column=1, sticky="w", padx=6, pady=4); cmb_cat.current(0)

        sups = database.tedarikci_listesi()
        ttk.Label(win, text="Toptancı:").grid(row=5, column=0, sticky="w", padx=6, pady=4)
        cmb_sup = ttk.Combobox(win, values=[f"{sid} - {name}" for sid,name,_ in sups], state="readonly", width=28, justify="left")
        cmb_sup.grid(row=5, column=1, sticky="w", padx=6, pady=4)

        def save():
            try:
                barcode = e_bar.get().strip()
                name = e_name.get().strip()
                price = float(e_price.get().strip())
                kdv = int(e_kdv.get().strip())
                cat = cmb_cat.get()
                try: sup_id = int(cmb_sup.get().split(" - ")[0])
                except Exception: sup_id = None
            except Exception:
                messagebox.showerror("Hata", "Alanları doğru doldurun."); return
            database.urun_kaydet_veya_guncelle(barcode, name, price, kdv, cat, supplier_id=sup_id)
            messagebox.showinfo("Kayıt", "Ürün kaydedildi.")
            win.destroy(); self._load()

        tk.Button(win, text="Kaydet", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=save).grid(row=6, column=0, columnspan=2, sticky="ew", padx=6, pady=10)

    def _open_report(self):
        win = tk.Toplevel(self); win.title("Stok Raporu")
        ttk.Label(win, text="Barkod:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        e_bar = ttk.Entry(win, width=30, justify="left"); e_bar.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="Başlangıç (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        e_s = ttk.Entry(win, width=30, justify="left"); e_s.grid(row=1, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(win, text="Bitiş (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        e_e = ttk.Entry(win, width=30, justify="left"); e_e.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        tv = ttk.Treeview(win, columns=("TARİH","HAREKET TÜRÜ","ADET","REF","NOT"), show="headings", height=12)
        for c in ("TARİH","HAREKET TÜRÜ","ADET","REF","NOT"): tv.heading(c, text=c); tv.column(c, width=150, anchor="w")
        tv.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=6, pady=6); win.columnconfigure(1, weight=1); win.rowconfigure(3, weight=1)
        def run():
            rows = database.stok_raporu(e_bar.get().strip(), e_s.get().strip() or None, e_e.get().strip() or None)
            for i in tv.get_children(): tv.delete(i)
            giris=cikis=duz=0
            for d,t,qty,ref,note in rows:
                tv.insert("", "end", values=(d,t,qty,ref,note))
                if t=="in": giris += qty
                elif t=="out": cikis += qty
                else: duz += qty
            messagebox.showinfo("Özet", f"GİRİŞ: {giris} | ÇIKIŞ: {cikis} | DÜZELTME: {duz}")
        tk.Button(win, text="Getir", bg="#007bff", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=run).grid(row=0, column=2, rowspan=3, sticky="ns", padx=6, pady=4)
