# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import database

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None


class CashierScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=10)
        self.on_back = on_back
        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self._build()
        self._list()

    def _build(self):
        # ÜST ÇUBUK (BAŞLIK + BUTONLAR)
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Sol tarafta Ana Menü butonu
        btn_ana = tk.Button(
            top, text="⬅️ Ana Menü", bg="#800000", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self.on_back
        )
        btn_ana.pack(side="left", padx=(0, 10), ipadx=10, ipady=3)

        # Başlık ortada
        ttk.Label(
            top, text="💵 KASA RAPORU",
            font=("Segoe UI", 22, "bold")
        ).pack(side="left", padx=(0, 10))

        # Sağ butonlar
        btn_frame = ttk.Frame(top)
        btn_frame.pack(side="right")

        tk.Button(
            btn_frame, text="📅 Bugün", bg="#6c757d", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self._set_today
        ).pack(side="left", padx=5, ipadx=8, ipady=3)

        tk.Button(
            btn_frame, text="📊 Rapor Getir", bg="#007bff", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self._list
        ).pack(side="left", padx=5, ipadx=8, ipady=3)

        tk.Button(
            btn_frame, text="💾 Z Raporu (Excel)", bg="#20c997", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self._export_excel
        ).pack(side="left", padx=5, ipadx=8, ipady=3)

        tk.Button(
            btn_frame, text="➕ Gider Ekle", bg="#dc3545", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self._add_expense
        ).pack(side="left", padx=5, ipadx=8, ipady=3)

        # TARİH FİLTRE GİRİŞİ
        filt = ttk.Frame(self)
        filt.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Label(filt, text="Başlangıç Tarihi (YYYY-AA-GG):").pack(side="left", padx=(0, 5))
        ttk.Entry(filt, textvariable=self.start_date, width=14).pack(side="left")
        ttk.Label(filt, text="Bitiş Tarihi:").pack(side="left", padx=5)
        ttk.Entry(filt, textvariable=self.end_date, width=14).pack(side="left")

        # TABLO
        cols = ("TARİH", "TÜR", "AÇIKLAMA", "TUTAR (₺)")
        self.tv = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for c in cols:
            self.tv.heading(c, text=c)
            anchor = "e" if "TUTAR" in c else "w"
            width = 150 if "TUTAR" in c else 200
            if c == "AÇIKLAMA": width = 280
            self.tv.column(c, anchor=anchor, width=width)
        self.tv.grid(row=2, column=0, sticky="nsew", pady=(6, 10))

        # ALT ÖZET BÖLÜMÜ
        bottom = tk.Frame(self, bg="#f9f9f9")
        bottom.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        for i in range(4):
            bottom.grid_columnconfigure(i, weight=1)

        font = ("Segoe UI", 13, "bold")
        self.lbl_gelir = tk.Label(bottom, text="Gelir: 0,00 ₺", font=font, bg="#f9f9f9", fg="#198754")
        self.lbl_gider = tk.Label(bottom, text="Gider: 0,00 ₺", font=font, bg="#f9f9f9", fg="#dc3545")
        self.lbl_iade = tk.Label(bottom, text="İade: 0,00 ₺", font=font, bg="#f9f9f9", fg="#fd7e14")
        self.lbl_net = tk.Label(bottom, text="Net Kasa: 0,00 ₺", font=("Segoe UI", 14, "bold"), bg="#f9f9f9", fg="#0d6efd")

        self.lbl_gelir.grid(row=0, column=0, pady=6)
        self.lbl_gider.grid(row=0, column=1, pady=6)
        self.lbl_iade.grid(row=0, column=2, pady=6)
        self.lbl_net.grid(row=0, column=3, pady=6)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    # ==================== #
    #  ARAYÜZ FONKSİYONLAR #
    # ==================== #
    def _set_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.start_date.set(today)
        self.end_date.set(today)

    def _list(self):
        for i in self.tv.get_children():
            self.tv.delete(i)

        s, e = self.start_date.get().strip(), self.end_date.get().strip()
        query = "SELECT date,type,description,amount FROM cash_register ORDER BY date DESC"
        params = ()
        if s and e:
            query = "SELECT date,type,description,amount FROM cash_register WHERE date BETWEEN ? AND ? ORDER BY date DESC"
            params = (s, e + "T23:59:59")

        con = database.baglan()
        cur = con.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        con.close()

        gelir = gider = iade = 0
        for d, t, desc, amt in rows:
            if t == "income": gelir += amt
            elif t == "expense": gider += amt
            elif t == "return": iade += amt
            self.tv.insert("", "end", values=(d.replace("T", " "), t.upper(), desc, f"{amt:.2f}"))

        net = gelir - gider - iade
        self.lbl_gelir.config(text=f"Gelir: {gelir:,.2f} ₺".replace(",", "."))
        self.lbl_gider.config(text=f"Gider: {gider:,.2f} ₺".replace(",", "."))
        self.lbl_iade.config(text=f"İade: {iade:,.2f} ₺".replace(",", "."))
        self.lbl_net.config(text=f"Net Kasa: {net:,.2f} ₺".replace(",", "."),
                            fg="#198754" if net >= 0 else "#dc3545")

    def _add_expense(self):
        win = tk.Toplevel(self)
        win.title("Yeni Gider Ekle")
        ttk.Label(win, text="Açıklama:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        e_desc = ttk.Entry(win, width=35)
        e_desc.grid(row=0, column=1, padx=6, pady=6)
        ttk.Label(win, text="Tutar (₺):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        e_amt = ttk.Entry(win, width=20)
        e_amt.grid(row=1, column=1, padx=6, pady=6)

        def kaydet():
            try:
                amt = float(e_amt.get().strip())
                desc = e_desc.get().strip() or "Gider"
                database.kasa_hareket("expense", amt, desc)
                self._list()
                win.destroy()
            except:
                messagebox.showerror("Hata", "Tutarı doğru giriniz (örn: 120.50)")

        tk.Button(win, text="Kaydet", bg="#28a745", fg="white",
                  font=("Segoe UI", 11, "bold"), command=kaydet).grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)

    def _export_excel(self):
        if Workbook is None:
            messagebox.showerror("Eksik Paket", "Excel dışa aktarma için 'openpyxl' kurulmalı.")
            return

        dt = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            title="Excel Raporu Kaydet",
            defaultextension=".xlsx",
            initialfile=f"kasa_raporu_{dt}.xlsx",
            filetypes=[("Excel Dosyası", "*.xlsx")]
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "KASA RAPORU"
        ws.append(["Tarih", "Tür", "Açıklama", "Tutar (₺)"])

        for item in self.tv.get_children():
            ws.append(self.tv.item(item, "values"))

        ws.append([])
        ws.append(["Toplam Gelir", "", "", self.lbl_gelir.cget("text").split(": ")[1]])
        ws.append(["Toplam Gider", "", "", self.lbl_gider.cget("text").split(": ")[1]])
        ws.append(["Toplam İade", "", "", self.lbl_iade.cget("text").split(": ")[1]])
        ws.append(["Net Kasa", "", "", self.lbl_net.cget("text").split(": ")[1]])

        for col in ws.columns:
            max_len = max(len(str(cell.value)) for cell in col if cell.value)
            ws.column_dimensions[col[0].column_letter].width = max_len + 3

        try:
            wb.save(path)
            messagebox.showinfo("Excel Raporu", f"Kaydedildi:\n{path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi:\n{e}")
