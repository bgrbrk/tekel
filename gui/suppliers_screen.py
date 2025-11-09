# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

class SuppliersScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self._build()
        self._load_suppliers()

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="TOPTANCILAR (CARİ)", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        mid = ttk.Frame(self); mid.grid(row=1, column=0, sticky="nsew", pady=6)
        self.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        # ---------- TOPTANCI TABLOSU ----------
        self.lst = ttk.Treeview(mid, columns=("ID","TOPTANCI","BAKİYE"), show="headings", height=12)

        self.lst.heading("ID", text="ID")
        self.lst.heading("TOPTANCI", text="TOPTANCI")
        self.lst.heading("BAKİYE", text="BAKİYE")

        self.lst.column("ID", width=32, anchor="center")            # ✅ 2 rakam sığacak şekilde küçültüldü
        self.lst.column("TOPTANCI", width=260, anchor="w")          # ✅ genişletildi
        self.lst.column("BAKİYE", width=100, anchor="e")

        self.lst.pack(side="left", fill="both", expand=True)

        # ---------- CARİ HAREKET TABLOSU ----------
        self.ledger = ttk.Treeview(mid, columns=("TARİH","HAREKET","TUTAR","NOT"), show="headings", height=12)

        self.ledger.heading("TARİH", text="TARİH")
        self.ledger.heading("HAREKET", text="HAREKET")
        self.ledger.heading("TUTAR", text="TUTAR")
        self.ledger.heading("NOT", text="NOT")

        self.ledger.column("TARİH", width=140, anchor="w")
        self.ledger.column("HAREKET", width=140, anchor="w")
        self.ledger.column("TUTAR", width=100, anchor="e")
        self.ledger.column("NOT", width=200, anchor="w")

        self.ledger.pack(side="left", fill="both", expand=True)

        # ---------- ALT ALAN ----------
        bottom = ttk.Frame(self); bottom.grid(row=2, column=0, sticky="ew", pady=6)

        ttk.Label(bottom, text="Ödeme Tutarı:").pack(side="left")
        self.e_amt = ttk.Entry(bottom, width=12); self.e_amt.pack(side="left", padx=6)

        ttk.Label(bottom, text="Not (zorunlu):").pack(side="left")
        self.e_note = ttk.Entry(bottom, width=30); self.e_note.pack(side="left", padx=6)

        tk.Button(bottom, text="Ödeme Gir", bg="#28a745", fg="white",
                  font=("Segoe UI", 12, "bold"), height=2,
                  command=self._odeme).pack(side="left", padx=6)

        tk.Button(bottom, text="Cari Raporu", bg="#6c757d", fg="white",
                  font=("Segoe UI", 12, "bold"), height=2,
                  command=self._rapor).pack(side="left", padx=6)

        self.lst.bind("<<TreeviewSelect>>", lambda e: self._load_ledger())

    def _load_suppliers(self):
        for i in self.lst.get_children(): self.lst.delete(i)
        for sid,name,balance in database.tedarikci_listesi():
            self.lst.insert("", "end", values=(sid,name,f"{balance:.2f}"))

    def _get_selected_supplier(self):
        sel = self.lst.selection()
        if not sel: return None
        v = self.lst.item(sel[0], "values")
        return int(v[0])

    def _load_ledger(self):
        sid = self._get_selected_supplier()
        if not sid: return
        for i in self.ledger.get_children(): self.ledger.delete(i)
        for d,t,a,n in database.ledger_for_supplier(sid):
            self.ledger.insert("", "end", values=(d,t,f"{a:.2f}",n))

    def _odeme(self):
        sid = self._get_selected_supplier()
        if not sid:
            messagebox.showwarning("Seçim", "Toptancı seçin.")
            return
        note = self.e_note.get().strip()
        if not note:
            messagebox.showerror("Zorunlu", "Not alanı zorunludur.")
            return
        try:
            amt = float(self.e_amt.get().strip())
        except:
            messagebox.showerror("Hata", "Tutar sayı olmalıdır.")
            return

        database.cari_odeme_ekle(sid, amt, note)
        self._load_suppliers()
        self._load_ledger()
        messagebox.showinfo("Ödeme", "Ödeme kaydedildi.")

    def _rapor(self):
        sid = self._get_selected_supplier()
        if not sid:
            messagebox.showwarning("Seçim", "Toptancı seçin.")
            return

        win = tk.Toplevel(self); win.title("Cari Raporu")

        ttk.Label(win, text="Başlangıç (YYYY-MM-DD):").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        e_s = ttk.Entry(win, width=20); e_s.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(win, text="Bitiş (YYYY-MM-DD):").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        e_e = ttk.Entry(win, width=20); e_e.grid(row=1, column=1, padx=6, pady=4)

        tv = ttk.Treeview(win, columns=("TARİH","HAREKET","TUTAR","NOT"), show="headings", height=14)
        for c in ("TARİH","HAREKET","TUTAR","NOT"):
            tv.heading(c, text=c); tv.column(c, width=140, anchor="w")
        tv.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        win.columnconfigure(1, weight=1); win.rowconfigure(2, weight=1)

        def run():
            rows = database.ledger_for_supplier(sid, e_s.get().strip() or None, e_e.get().strip() or None)
            for i in tv.get_children(): tv.delete(i)
            borc = alacak = 0
            for d,t,a,n in rows:
                tv.insert("", "end", values=(d,t,f"{a:.2f}",n))
                if t=="purchase": borc += abs(a)
                elif t=="payment": alacak += abs(a)
            color = "red" if borc>alacak else "green"
            tk.Label(win, text=f"BORÇ: {borc:.2f} | ALACAK: {alacak:.2f}", fg=color,
                     font=("Segoe UI", 12, "bold")).grid(row=3, column=0, columnspan=2, pady=6)

        tk.Button(win, text="Getir", bg="#007bff", fg="white",
                  font=("Segoe UI", 12, "bold"), height=2,
                  command=run).grid(row=0, column=2, rowspan=2, padx=6, pady=4, sticky="ns")
