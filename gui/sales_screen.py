# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import ttk, messagebox
import database

class SalesScreen(ttk.Frame):
    def __init__(self, master, on_back, user, settings):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self.user = user
        self.settings = settings

        self.basket = {}
        self._build()
        self._refresh_totals()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(2, weight=1)

        tk.Button(top, text="⮌ Ana Menü", bg="#b22222", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=12, pady=4,
                  command=self.on_back).grid(row=0, column=0, sticky="w")

        ttk.Label(top, text="SATIŞ", font=("Segoe UI", 18, "bold")).grid(row=0, column=1, sticky="w", padx=12)

        ttk.Label(top, text="Barkod:").grid(row=1, column=0, sticky="w", pady=6)
        self.e_barcode = ttk.Entry(top, width=40)
        self.e_barcode.grid(row=1, column=1, sticky="w")
        self.e_barcode.bind("<Return>", lambda e: self._add_by_barcode())

        logo_path = os.path.join("assets", "satis.png")
        self._logo_img = None
        if os.path.exists(logo_path):
            try:
                self._logo_img = tk.PhotoImage(file=logo_path)
                tk.Label(top, image=self._logo_img, bd=0).grid(row=0, column=2, rowspan=2, sticky="ne", padx=8, pady=4)
            except:
                pass

        mid = ttk.Frame(self)
        mid.grid(row=1, column=0, sticky="nsew")
        mid.grid_rowconfigure(0, weight=1)
        mid.grid_columnconfigure(0, weight=1)

        cols = ("BARKOD", "ÜRÜN", "ADET", "FİYAT", "KDV", "TOPLAM")
        self.tv = ttk.Treeview(mid, columns=cols, show="headings", height=18)
        for c in cols:
            self.tv.heading(c, text=c)
        self.tv.column("BARKOD", width=130)
        self.tv.column("ÜRÜN", width=250)
        self.tv.column("ADET", width=60, anchor="center")
        self.tv.column("FİYAT", width=100, anchor="e")
        self.tv.column("KDV", width=60, anchor="center")
        self.tv.column("TOPLAM", width=120, anchor="e")
        self.tv.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(mid, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tv.bind("<Delete>", self._delete_selected)

        bottom = tk.Frame(self, bg="#e8e6e1")
        bottom.grid(row=2, column=0, sticky="ew", pady=6)
        bottom.grid_columnconfigure(1, weight=1)

        left = tk.Frame(bottom, bg="#e8e6e1")
        left.grid(row=0, column=0, sticky="w", padx=10)

        tk.Button(left, text="İADE", bg="#ffc107", fg="black",
                  font=("Segoe UI", 11, "bold"), padx=18,
                  command=lambda: self._pay("return")).pack(side="left", padx=6, ipady=9)

        tk.Button(left, text="Adet +", bg="#0d6efd", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=14, command=self._inc).pack(side="left", padx=6, ipady=9)
        tk.Button(left, text="Adet -", bg="#6c757d", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=14, command=self._dec).pack(side="left", padx=6, ipady=9)
        tk.Button(left, text="Satış İptal", bg="#d63343", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=14, command=self._cancel).pack(side="left", padx=6, ipady=9)

        center = tk.Frame(bottom, bg="#e8e6e1")
        center.grid(row=0, column=1, sticky="n")

        self.total_lbl = tk.Label(center, text="Toplam: 0,00 TL",
                                  font=("Segoe UI", 26, "bold"), bg="#e8e6e1")
        self.total_lbl.pack()

        # ✅ KUR BÖLÜMÜ
        cur_frame = tk.Frame(center, bg="#e8e6e1")
        cur_frame.pack(pady=4)

        self.usd_lbl = tk.Label(cur_frame, text="$ -", fg="green", bg="#e8e6e1", font=("Segoe UI", 11, "bold"))
        self.eur_lbl = tk.Label(cur_frame, text="€ -", fg="red", bg="#e8e6e1", font=("Segoe UI", 11, "bold"))
        self.gbp_lbl = tk.Label(cur_frame, text="£ -", fg="blue", bg="#e8e6e1", font=("Segoe UI", 11, "bold"))
        self.usd_lbl.pack(side="left", padx=10)
        self.eur_lbl.pack(side="left", padx=10)
        self.gbp_lbl.pack(side="left", padx=10)

        right = tk.Frame(bottom, bg="#e8e6e1")
        right.grid(row=0, column=2, sticky="e", padx=10)

        tk.Button(right, text="NAKİT", bg="#28a745", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=20,
                  command=lambda: self._pay("cash")).pack(side="left", padx=6, ipady=10)

        tk.Button(right, text="KREDİ KARTI", bg="#0d6efd", fg="white",
                  font=("Segoe UI", 11, "bold"), padx=14,
                  command=lambda: self._pay("card")).pack(side="left", ipady=10)

        self.after(100, lambda: self.e_barcode.focus_set())

    # ------------ LOGIC ----------------

    def _add_by_barcode(self):
        code = self.e_barcode.get().strip()
        if not code:
            return self._focus_barcode(True)

        pr = database.urun_barkod(code)
        if not pr:
            messagebox.showwarning("Bulunamadı", f"Barkod bulunamadı: {code}")
            return self._focus_barcode(True)

        if code in self.basket:
            self.basket[code]["qty"] += 1
        else:
            self.basket[code] = {
                "product_id": pr["id"],
                "name": pr["name"],
                "qty": 1,
                "price": pr["sale_price_tl"],
                "kdv": pr["kdv"]
            }

        self._refresh()
        self._focus_barcode(True)

    def _focus_barcode(self, clear=False):
        if clear:
            self.e_barcode.delete(0, "end")
        self.e_barcode.focus_set()

    def _get_selected_barcode(self):
        sel = self.tv.selection()
        if not sel:
            return None
        return str(self.tv.item(sel[0])["values"][0])

    def _inc(self):
        bc = self._get_selected_barcode()
        if bc and bc in self.basket:
            self.basket[bc]["qty"] += 1
            self._refresh()

    def _dec(self):
        bc = self._get_selected_barcode()
        if bc and bc in self.basket:
            if self.basket[bc]["qty"] > 1:
                self.basket[bc]["qty"] -= 1
            else:
                del self.basket[bc]
            self._refresh()

    def _delete_selected(self, event=None):
        bc = self._get_selected_barcode()
        if bc and bc in self.basket:
            del self.basket[bc]
            self._refresh()

    def _cancel(self):
        if messagebox.askyesno("İptal", "Satışı iptal edeceksiniz. Emin misiniz?"):
            self.basket.clear()
            self._refresh()

    def _pay(self, method):
        if not self.basket:
            return messagebox.showwarning("Boş", "Sepet boş.")

        sign = -1 if method == "return" else 1

        items = [{
            "barcode": bc,
            "product_id": it["product_id"],
            "name": it["name"],
            "qty": sign * it["qty"],
            "price": it["price"],
            "kdv": it["kdv"]
        } for bc, it in self.basket.items()]

        total = sum(i["qty"] * i["price"] * (1 + i["kdv"] / 100) for i in items)

        database.satis_kaydet(self.user["id"], items, total, method)

        messagebox.showinfo("Tamam", "İADE KAYDEDİLDİ." if method=="return" else "SATIŞ KAYDEDİLDİ.")

        self.basket.clear()
        self._refresh()
        self._focus_barcode(True)

    # ------------ VIEW REFRESH -------------
    def _refresh(self):
        for i in self.tv.get_children():
            self.tv.delete(i)
        for bc, it in self.basket.items():
            t = it["qty"] * it["price"] * (1 + it["kdv"] / 100)
            self.tv.insert("", "end", values=(bc, it["name"], it["qty"],
                                              f"{it['price']:.2f}", it["kdv"], f"{t:.2f}"))
        self._refresh_totals()

    def _total(self):
        return sum(it["qty"] * it["price"] * (1 + it["kdv"] / 100) for it in self.basket.values())

    def _refresh_totals(self):
        total = self._total()
        self.total_lbl.config(text=f"Toplam: {total:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))

        try:
            kurlar = database.son_kurlar()
            usd = kurlar["USD"]["rate_to_tl"]
            eur = kurlar["EUR"]["rate_to_tl"]
            gbp = kurlar["GBP"]["rate_to_tl"]
            self.usd_lbl.config(text=f"$ {total*usd:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.eur_lbl.config(text=f"€ {total*eur:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.gbp_lbl.config(text=f"£ {total*gbp:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        except:
            self.usd_lbl.config(text="$ -")
            self.eur_lbl.config(text="€ -")
            self.gbp_lbl.config(text="£ -")
