import tkinter as tk
from tkinter import ttk, messagebox
from database import urun_barkod, satis_kaydet
from utils.currency_updater import son_kurlar
from utils.helpers import tl

class SatisEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw)
        self.app = app
        self.sepet = []
        self.kurlar = son_kurlar()
        self.arayuz()

    def arayuz(self):
        # Üst Bar
        ust = ttk.Frame(self)
        ust.pack(fill="x", pady=10)

        ttk.Button(ust, text="⮌ Ana Menü", command=self.app.goster_panel, style="Big.TButton")\
            .pack(side="left", padx=10)

        ttk.Label(ust, text="SATIŞ", font=("Segoe UI", 34, "bold")).pack(side="left", padx=20)

        # Barkod Giriş
        bf = ttk.Frame(self)
        bf.pack(fill="x", padx=10)

        ttk.Label(bf, text="Barkod:", font=("Segoe UI", 20)).pack(side="left")
        self.e = ttk.Entry(bf, font=("Segoe UI", 24), width=18)
        self.e.pack(side="left", padx=10)
        self.e.focus_set()
        self.e.bind("<Return>", self.ekle)

        # Ürün Tablosu
        sutunlar = ("barkod", "ad", "adet", "fiyat", "kdv", "toplam")
        self.tv = ttk.Treeview(self, columns=sutunlar, show="headings", height=16)

        basliklar = [
            ("barkod", "BARKOD", "w"),
            ("ad", "ÜRÜN ADI", "w"),
            ("adet", "ADET", "center"),
            ("fiyat", "FİYAT (TL)", "e"),
            ("kdv", "KDV (%)", "e"),
            ("toplam", "TOPLAM (TL)", "e")
        ]

        for col, text, align in basliklar:
            self.tv.heading(col, text=text)
            self.tv.column(col, anchor=align, width=170)

        self.tv.pack(fill="both", expand=True, padx=10, pady=10)

        # ALT BİLGİ Alanı
        alt = ttk.Frame(self)
        alt.pack(fill="x", pady=10)

        self.lbl_toplam = ttk.Label(alt, text="Toplam: 0,00 TL", font=("Segoe UI", 32, "bold"))
        self.lbl_toplam.pack(side="left", padx=20)

        self.lbl_doviz = ttk.Label(alt, text="≈ $0.00 | €0.00 | £0.00", font=("Segoe UI", 18))
        self.lbl_doviz.pack(side="left", padx=10)

        # RENKLİ BUTON ALANI
        tuslar = tk.Frame(self, bg="#eee")
        tuslar.pack(fill="x", padx=10, pady=10)

        self.button(tuslar, "NAKİT", "#16a34a", lambda: self.kaydet("Nakit"))
        self.button(tuslar, "KREDİ KARTI", "#2563eb", lambda: self.kaydet("Kredi Kartı"))
        self.button(tuslar, "SATIŞ İPTAL", "#dc2626", self.iptal)

    def button(self, parent, text, renk, cmd):
        b = tk.Button(parent, text=text, font=("Segoe UI", 26, "bold"),
                      bg=renk, fg="white", height=2, relief="flat", cursor="hand2",
                      activebackground=renk, command=cmd)
        b.pack(side="left", expand=True, fill="x", padx=10)
        return b

    def ekle(self, e=None):
        barkod = self.e.get().strip()
        self.e.delete(0, "end")
        if not barkod:
            return

        urun = urun_barkod(barkod)
        if not urun:
            messagebox.showwarning("Bulunamadı", "Bu barkod kayıtlı değil.")
            return

        for x in self.sepet:
            if x["id"] == urun["id"]:
                x["adet"] += 1
                x["toplam"] = x["adet"] * x["fiyat"]
                return self.yenile()

        self.sepet.append({
            "id": urun["id"],
            "barkod": urun["barcode"],
            "ad": urun["name"],
            "adet": 1,
            "fiyat": float(urun["sale_price_tl"]),
            "kdv": urun["kdv"],
            "toplam": float(urun["sale_price_tl"])
        })
        self.yenile()

    def yenile(self):
        for i in self.tv.get_children():
            self.tv.delete(i)

        toplam = 0

        for x in self.sepet:
            toplam += x["toplam"]
            self.tv.insert("", "end", values=(
                x["barkod"], x["ad"], x["adet"],
                f"{x['fiyat']:.2f}", f"%{x['kdv']}", f"{x['toplam']:.2f}"
            ))

        self.lbl_toplam.config(text=f"Toplam: {tl(toplam)}")

        if self.kurlar:
            self.lbl_doviz.config(text=f"≈ ${toplam/self.kurlar['USD'][0]:.2f} | €{toplam/self.kurlar['EUR'][0]:.2f} | £{toplam/self.kurlar['GBP'][0]:.2f}")

    def kaydet(self, odeme_turu):
        if not self.sepet:
            return

        toplam = sum(x["toplam"] for x in self.sepet)
        satis_kaydet(self.app.kullanici["id"], self.sepet, toplam, odeme_turu)

        messagebox.showinfo("Satış Tamamlandı", "Satış başarıyla kaydedildi.")
        self.sepet = []
        self.yenile()

    def iptal(self):
        self.sepet = []
        self.yenile()
