# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

class SalesScreen(ttk.Frame):
    """
    SATIŞ EKRANI
    - Üstte: Ana Menü butonu, başlık, barkod girişi (Enter ile ekle) ve 'Oto Giriş' seçeneği.
    - Orta: Sepet (Treeview)
    - Altta: Solda adet -/+, Satış İptal; sağda Kredi Kartı / Nakit. Ortada geniş boşluk.
    - En altta: Sol 'Toplam TL', sağ kur eşdeğerleri (≈ $ | € | £)
    """
    def __init__(self, master, on_back, user, settings):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self.user = user
        self.settings = settings
        self.sepet = {}          # {barcode: {product_id, name, qty, price, kdv, barcode}}
        self._auto_after = None  # oto giriş debouncing
        self._build()
        self._refresh_totals()

    # ---------------- UI ----------------
    def _build(self):
        # Üst başlık ve barkod alanı
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="SATIŞ", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        ent = ttk.Frame(self); ent.grid(row=1, column=0, sticky="ew", pady=(6, 4))
        ttk.Label(ent, text="Barkod:").pack(side="left")
        self.e_bar = ttk.Entry(ent, width=40)
        self.e_bar.pack(side="left", padx=6)
        self.e_bar.focus_set()
        self.e_bar.bind("<Return>", lambda e: self._add_barcode())

        # NOT: ttk.BooleanVar kullanmıyoruz (talep gereği). tk.BooleanVar kullan.
        self.auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ent, text="Oto Giriş", variable=self.auto_var).pack(side="left", padx=6)
        self.e_bar.bind("<KeyRelease>", self._auto_check)

        # Sepet tablosu
        cols = ("BARKOD", "ÜRÜN ADI", "ADET", "FİYAT (TL)", "KDV (%)", "TOPLAM (TL)")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree.heading(c, text=c)
            # soldan hizalı ve biraz geniş kolonlar
            anchor = "w" if c in ("BARKOD", "ÜRÜN ADI") else "center"
            self.tree.column(c, width=150, anchor=anchor)
        self.tree.grid(row=2, column=0, sticky="nsew", pady=6)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Alt buton satırı: sol grup / boşluk / sağ grup
        btn_row = ttk.Frame(self)
        btn_row.grid(row=3, column=0, sticky="ew", pady=(6, 8))
        btn_row.columnconfigure(0, weight=0)  # sol grup
        btn_row.columnconfigure(1, weight=1)  # geniş boşluk (esneyecek)
        btn_row.columnconfigure(2, weight=0)  # sağ grup

        # Sol butonlar
        left_grp = ttk.Frame(btn_row)
        left_grp.grid(row=0, column=0, sticky="w")
        tk.Button(
            left_grp, text="− ADET", bg="#6c757d", fg="white",
            font=("Segoe UI", 12, "bold"), height=2, command=self._dec
        ).pack(side="left", padx=6)
        tk.Button(
            left_grp, text="+ ADET", bg="#6c757d", fg="white",
            font=("Segoe UI", 12, "bold"), height=2, command=self._inc
        ).pack(side="left", padx=6)
        tk.Button(
            left_grp, text="SATIŞ İPTAL", bg="#dc3545", fg="white",
            font=("Segoe UI", 12, "bold"), height=2, command=self._iptal
        ).pack(side="left", padx=6)

        # Ortada boşluk
        ttk.Frame(btn_row).grid(row=0, column=1, sticky="ew")

        # Sağ butonlar
        right_grp = ttk.Frame(btn_row)
        right_grp.grid(row=0, column=2, sticky="e")
        tk.Button(
            right_grp, text="KREDİ KARTI", bg="#0d6efd", fg="white",
            font=("Segoe UI", 12, "bold"), height=2,
            command=lambda: self._save_sale("card")
        ).pack(side="left", padx=6)
        tk.Button(
            right_grp, text="NAKİT", bg="#28a745", fg="white",
            font=("Segoe UI", 12, "bold"), height=2,
            command=lambda: self._save_sale("cash")
        ).pack(side="left", padx=6)

        # En alt toplam ve döviz eşdeğerleri
        bottom = ttk.Frame(self)
        bottom.grid(row=4, column=0, sticky="ew")
        self.lbl_total = ttk.Label(bottom, text="Toplam: 0,00 TL", font=("Segoe UI", 14, "bold"))
        self.lbl_total.pack(side="left")
        self.lbl_fx = ttk.Label(bottom, text="≈ $.. | €.. | £..", font=("Segoe UI", 11))
        self.lbl_fx.pack(side="right")

    # ---------------- Oto giriş debounce ----------------
    def _auto_check(self, _ev=None):
        if not self.auto_var.get():
            return
        # Debounce
        if self._auto_after:
            try:
                self.after_cancel(self._auto_after)
            except Exception:
                pass

        def run():
            t = self.e_bar.get().strip()
            # Barkod okuyucu 10-13 haneli rakam basar genelde
            if len(t) >= 6 and t.isdigit():
                self._add_barcode()
        self._auto_after = self.after(120, run)

    # ---------------- Sepet işlemleri ----------------
    def _add_barcode(self):
        bc = self.e_bar.get().strip()
        if not bc:
            return
        pr = database.urun_barkod(bc)
        if not pr:
            # Sadece 1 kez uyar (çift tetiklenmesin)
            messagebox.showerror("Ürün Yok", "Bu barkod kayıtlı değil.\nÖnce Stok > Ürün Ekle bölümünden kaydedin.")
            self.e_bar.delete(0, "end")
            return

        it = self.sepet.get(bc)
        if it:
            it["qty"] += 1
        else:
            self.sepet[bc] = {
                "product_id": pr["id"],
                "name": pr["name"],
                "qty": 1,
                "price": pr["sale_price_tl"],
                "kdv": pr["kdv"],
                "barcode": bc,
            }
        self._refresh_tree()
        self._refresh_totals()
        self.e_bar.delete(0, "end")

    def _get_selected_barcode(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")[0]  # ilk sütun barkod

    def _inc(self):
        bc = self._get_selected_barcode()
        if bc and bc in self.sepet:
            self.sepet[bc]["qty"] += 1
            self._refresh_tree(); self._refresh_totals()

    def _dec(self):
        bc = self._get_selected_barcode()
        if bc and bc in self.sepet:
            self.sepet[bc]["qty"] -= 1
            if self.sepet[bc]["qty"] <= 0:
                del self.sepet[bc]
            self._refresh_tree(); self._refresh_totals()

    def _iptal(self):
        if not self.sepet:
            return
        if messagebox.askyesno("İptal", "Sepeti tamamen temizlemek istiyor musunuz?"):
            self.sepet.clear()
            self._refresh_tree(); self._refresh_totals()

    # ---------------- Kayıt ----------------
    def _save_sale(self, pay_type: str):
        if not self.sepet:
            messagebox.showwarning("Boş", "Sepete ürün ekleyin.")
            return

        items = []
        for bc, it in self.sepet.items():
            items.append({
                "product_id": it["product_id"],
                "barcode": bc,
                "name": it["name"],
                "qty": it["qty"],
                "price": it["price"],
                "kdv": it["kdv"],
                "toplam": it["qty"] * it["price"]
            })
        total = sum(x["toplam"] for x in items)

        try:
            database.satis_kaydet(
                cashier_id=self.user["id"],
                items=items,
                total_tl=total,
                payment_type="card" if pay_type == "card" else "cash",
                fis_yaz=bool(self.settings.get("yazdir_fis", False))
            )
        except Exception as e:
            messagebox.showerror("Hata", f"Satış kaydedilemedi:\n{e}")
            return

        messagebox.showinfo("Satış", "Satış kaydedildi.")
        self.sepet.clear()
        self._refresh_tree(); self._refresh_totals()

    # ---------------- Görünüm güncelleme ----------------
    def _refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for bc, it in self.sepet.items():
            toplam = it["qty"] * it["price"]
            self.tree.insert(
                "", "end",
                values=(bc, it["name"], it["qty"], f"{it['price']:.2f}", it["kdv"], f"{toplam:.2f}")
            )

    def _refresh_totals(self):
        tot = sum(it["qty"] * it["price"] for it in self.sepet.values())
        self.lbl_total.config(text=f"Toplam: {tot:.2f} TL")
        # Döviz eşdeğerleri: DB’de 1 TRY -> CUR oranı tutuluyor; TL -> CUR = TL * rate
        try:
            rates = database.son_kurlar()
            usd = tot * float(rates.get("USD", {}).get("rate_to_tl", 0) or 0)
            eur = tot * float(rates.get("EUR", {}).get("rate_to_tl", 0) or 0)
            gbp = tot * float(rates.get("GBP", {}).get("rate_to_tl", 0) or 0)
            if usd and eur and gbp:
                self.lbl_fx.config(text=f"≈ ${usd:.2f} | €{eur:.2f} | £{gbp:.2f}")
            else:
                self.lbl_fx.config(text="≈ $.. | €.. | £..")
        except Exception:
            self.lbl_fx.config(text="≈ $.. | €.. | £..")
