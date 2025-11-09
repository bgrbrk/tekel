# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

class CashierScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self._build()

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="KASA", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        frm = ttk.Frame(self); frm.grid(row=1, column=0, sticky="ew", pady=6)
        ttk.Label(frm, text="Tutar:").pack(side="left")
        self.e_amt = ttk.Entry(frm, width=12); self.e_amt.pack(side="left", padx=6)
        ttk.Label(frm, text="Not (zorunlu):").pack(side="left")
        self.e_note = ttk.Entry(frm, width=30); self.e_note.pack(side="left", padx=6)
        tk.Button(frm, text="Gelir Ekle", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=lambda:self._ekle("income")).pack(side="left", padx=6)
        tk.Button(frm, text="Gider Ekle", bg="#dc3545", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=lambda:self._ekle("expense")).pack(side="left", padx=6)
        tk.Button(frm, text="Kasa Raporu", bg="#6c757d", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._rapor).pack(side="left", padx=6)
        tk.Button(frm, text="Gün Kapat (Z Raporu)", bg="#007bff", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=self._zraporu).pack(side="left", padx=6)

        self.tv = ttk.Treeview(self, columns=("TARİH","KASA HAREKETİ","TUTAR","NOT"), show="headings", height=14)
        for c in ("TARİH","KASA HAREKETİ","TUTAR","NOT"): self.tv.heading(c, text=c); self.tv.column(c, width=160, anchor="w")
        self.tv.grid(row=2, column=0, sticky="nsew", pady=6)
        self.columnconfigure(0, weight=1); self.rowconfigure(2, weight=1)
        self._list()

    def _ekle(self, tip):
        note = self.e_note.get().strip()
        if not note: messagebox.showerror("Zorunlu", "Not giriniz."); return
        try: amt = float(self.e_amt.get().strip())
        except Exception: messagebox.showerror("Hata", "Tutar sayı olmalıdır."); return
        if tip=="expense": amt = -abs(amt)
        database.kasa_hareket_ekle("income" if amt>0 else "expense", abs(amt) if amt>0 else -amt, note)
        self._list()

    def _list(self):
        rows, gelir, gider, net = database.kasa_raporu()
        for i in self.tv.get_children(): self.tv.delete(i)
        for d,t,a,n in rows:
            a = a if t=="income" else -a
            self.tv.insert("", "end", values=(d,t,f"{a:.2f}",n))

    def _rapor(self):
        win = tk.Toplevel(self); win.title("Kasa Raporu")
        ttk.Label(win, text="Başlangıç (YYYY-MM-DD):").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        e_s = ttk.Entry(win, width=20); e_s.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Label(win, text="Bitiş (YYYY-MM-DD):").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        e_e = ttk.Entry(win, width=20); e_e.grid(row=1, column=1, padx=6, pady=4, sticky="w")
        tv = ttk.Treeview(win, columns=("TARİH","KASA HAREKETİ","TUTAR","NOT"), show="headings", height=14)
        for c in ("TARİH","KASA HAREKETİ","TUTAR","NOT"): tv.heading(c, text=c); tv.column(c, width=140, anchor="w")
        tv.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6); win.columnconfigure(1, weight=1); win.rowconfigure(2, weight=1)
        def run():
            rows, gelir, gider, net = database.kasa_raporu(e_s.get().strip() or None, e_e.get().strip() or None)
            for i in tv.get_children(): tv.delete(i)
            for d,t,a,n in rows:
                a = a if t=="income" else -a
                tv.insert("", "end", values=(d,t,f"{a:.2f}",n))
            tk.Label(win, text=f"Gelir: {gelir:.2f} | Gider: {gider:.2f} | Net: {net:.2f}", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, columnspan=2, pady=6)
        tk.Button(win, text="Getir", bg="#007bff", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=run).grid(row=0, column=2, rowspan=2, padx=6, pady=4, sticky="ns")

    def _zraporu(self):
        path = database.z_raporu_yaz()
        messagebox.showinfo("Z Raporu", f"Oluşturuldu:\\n{path}")
