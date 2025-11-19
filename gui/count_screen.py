# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
from openpyxl import Workbook
from datetime import datetime


class CountScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=12)
        self.on_back = on_back
        self.counts = {}
        self._auto_after = None
        self._build()
        self._refresh()

    def _build(self):
        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.grid_columnconfigure(1, weight=1)

        # 🔴 Ana Menü
        tk.Button(
            top, text="⬅️ Ana Menü", bg="#800000", fg="white",
            font=("Segoe UI", 11, "bold"), cursor="hand2",
            command=self.on_back, activebackground="#a00000"
        ).pack(side="left", padx=(0, 10), ipadx=10, ipady=3)

        ttk.Label(top, text="📦 SAYIM", font=("Segoe UI", 20, "bold")).pack(side="left")

        # Sağ butonlar
        for txt, color, cmd in [
            ("💾 Dışa Aktar (Excel)", "#007bff", self._export),
            ("✅ Farkları Uygula", "#28a745", self._apply),
            ("🗑️ Satır Sil", "#dc3545", self._remove),
            ("🧹 Temizle", "#6c757d", self._clear),
        ]:
            tk.Button(top, text=txt, bg=color, fg="white",
                      font=("Segoe UI", 11, "bold"), cursor="hand2",
                      command=cmd).pack(side="right", padx=4, ipadx=10, ipady=3)

        # Barkod girişi
        ent = ttk.Frame(self)
        ent.grid(row=1, column=0, sticky="ew", pady=8)
        ttk.Label(ent, text="Barkod:").pack(side="left")
        self.e_bc = ttk.Entry(ent, width=34)
        self.e_bc.pack(side="left", padx=6)
        self.e_bc.bind("<Return>", lambda e: self._add())
        self.auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ent, text="Oto Giriş", variable=self.auto_var).pack(side="left", padx=6)
        self.e_bc.bind("<KeyRelease>", self._auto_check)

        # Tablo
        self.tree = ttk.Treeview(
            self, columns=("BARKOD", "ÜRÜN", "SAYILAN", "SİSTEM STOK", "FARK"),
            show="headings", height=16
        )
        for c, w, a in [
            ("BARKOD", 170, "w"),
            ("ÜRÜN", 220, "w"),
            ("SAYILAN", 100, "center"),
            ("SİSTEM STOK", 100, "center"),
            ("FARK", 120, "center")
        ]:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor=a)

        # 🔹 Tag renkleri
        self.tree.tag_configure("eksik", background="#ffcccc")  # kırmızı
        self.tree.tag_configure("fazla", background="#ccffcc")  # yeşil

        self.tree.grid(row=2, column=0, sticky="nsew", pady=8)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.e_bc.focus_set()

    # -------------------------------------------------------------
    def _auto_check(self, event=None):
        if not self.auto_var.get():
            return
        if self._auto_after:
            self.after_cancel(self._auto_after)

        def run():
            t = self.e_bc.get().strip()
            if len(t) >= 6 and t.isdigit():
                self._add()
        self._auto_after = self.after(120, run)

    # -------------------------------------------------------------
    def _add(self):
        bc = self.e_bc.get().strip()
        if not bc:
            return
        pr = database.urun_barkod(bc)
        self.e_bc.delete(0, "end")

        if not pr:
            if not messagebox.askyesno("Yeni Ürün", f"{bc} barkodu sistemde yok. Yeni ürün kartı açılsın mı?"):
                return
            self._open_new_product_form(bc)
            return

        # 🔹 Adet girişi penceresi
        win = tk.Toplevel(self)
        win.title("Adet Girişi")
        win.geometry("340x180")
        win.resizable(False, False)
        win.configure(bg="#f8f9fa")

        ttk.Label(win, text=f"Ürün: {pr.get('name','-')}", font=("Segoe UI", 11, "bold")).pack(pady=(15, 8))
        ttk.Label(win, text="Sayım Adedi (tam sayı):", font=("Segoe UI", 10)).pack()

        adet_entry = ttk.Entry(win, font=("Segoe UI", 11), justify="center", width=12)
        adet_entry.pack(pady=6)
        adet_entry.focus_set()

        def kaydet(*_):
            try:
                adet_str = adet_entry.get().strip()
                if not adet_str.isdigit():
                    raise ValueError
                adet = int(adet_str)
                if adet < 0:
                    raise ValueError
                self.counts[bc] = adet
                self._refresh()
                win.destroy()
            except Exception:
                messagebox.showerror("Hata", "Lütfen geçerli bir tam sayı girin.")

        def iptal():
            win.destroy()

        win.bind("<Return>", kaydet)

        btn_fr = ttk.Frame(win)
        btn_fr.pack(pady=10)
        tk.Button(btn_fr, text="Kaydet", bg="#28a745", fg="white",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=kaydet).pack(side="left", padx=8, ipadx=10, ipady=3)
        tk.Button(btn_fr, text="İptal", bg="#dc3545", fg="white",
                  font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=iptal).pack(side="left", padx=8, ipadx=10, ipady=3)

    # -------------------------------------------------------------
    def _open_new_product_form(self, barcode):
        win = tk.Toplevel(self)
        win.title("Yeni Ürün Kartı")
        ttk.Label(win, text="Barkod:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        e_bar = ttk.Entry(win, width=30)
        e_bar.grid(row=0, column=1, padx=6, pady=4)
        e_bar.insert(0, barcode)
        ttk.Label(win, text="Ad:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        e_name = ttk.Entry(win, width=30)
        e_name.grid(row=1, column=1, padx=6, pady=4)
        ttk.Label(win, text="Fiyat (TL):").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        e_price = ttk.Entry(win, width=30)
        e_price.grid(row=2, column=1, padx=6, pady=4)
        ttk.Label(win, text="KDV (%):").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        e_kdv = ttk.Entry(win, width=30)
        e_kdv.grid(row=3, column=1, padx=6, pady=4)
        e_kdv.insert(0, "20")

        from gui.stock_screen import CATEGORIES
        ttk.Label(win, text="Kategori:").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        cmb_cat = ttk.Combobox(win, values=CATEGORIES, state="readonly", width=28)
        cmb_cat.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        cmb_cat.current(0)
        sups = database.tedarikci_listesi()
        ttk.Label(win, text="Toptancı:").grid(row=5, column=0, sticky="w", padx=6, pady=4)
        cmb_sup = ttk.Combobox(win, values=[f"{sid} - {name}" for sid, name, _ in sups],
                               state="readonly", width=28)
        cmb_sup.grid(row=5, column=1, sticky="w", padx=6, pady=4)

        def save():
            try:
                name = e_name.get().strip()
                price = float(e_price.get().strip())
                kdv = int(e_kdv.get().strip())
                cat = cmb_cat.get()
                try:
                    sup_id = int(cmb_sup.get().split(" - ")[0])
                except Exception:
                    sup_id = None
                database.urun_kaydet_veya_guncelle(barcode, name, price, kdv, cat, supplier_id=sup_id)
                self._refresh()
                win.destroy()
            except Exception:
                messagebox.showerror("Hata", "Alanları doğru doldurun.")

        tk.Button(win, text="Kaydet", bg="#28a745", fg="white",
                  font=("Segoe UI", 12, "bold"), height=2,
                  command=save).grid(row=6, column=0, columnspan=2, sticky="ew", padx=6, pady=10)

    # -------------------------------------------------------------
    def _remove(self):
        sel = self.tree.selection()
        if not sel:
            return
        bc = self.tree.item(sel[0], "values")[0]
        if bc in self.counts:
            del self.counts[bc]
        self._refresh()

    def _clear(self):
        self.counts.clear()
        self._refresh()

    def _refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for bc, cnt in self.counts.items():
            pr = database.urun_barkod(bc)
            name = pr["name"] if pr else "-"
            sys_stock = pr["stock"] if pr else 0
            fark = cnt - (sys_stock or 0)

            # 🔹 Renk ve ibare seçimi
            if fark < 0:
                tag = "eksik"
                fark_str = f"{fark} 📉 Eksik"
            elif fark > 0:
                tag = "fazla"
                fark_str = f"+{fark} 📈 Fazla"
            else:
                tag = ""
                fark_str = "0"

            self.tree.insert("", "end",
                             values=(bc, name, cnt, sys_stock, fark_str),
                             tags=(tag,))

    def _apply(self):
        applied = 0
        for bc, cnt in self.counts.items():
            pr = database.urun_barkod(bc)
            if not pr:
                continue
            fark = cnt - (pr["stock"] or 0)
            if fark != 0:
                database.stok_degistir(pr["id"], fark, "adjust", ref="sayim", note="Sayım farkı")
                applied += 1
        messagebox.showinfo("Sayım", f"Uygulanan kayıt: {applied}")
        self._clear()

    def _export(self):
        filename = f"sayim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path = filedialog.asksaveasfilename(
            title="Excel olarak kaydet",
            defaultextension=".xlsx",
            initialfile=filename,
            filetypes=[("Excel Dosyası", "*.xlsx")]
        )
        if not path:
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Sayım Sonuçları"
        ws.append(["Barkod", "Ürün Adı", "Sayılan", "Sistem Stok", "Fark"])
        for item in self.tree.get_children():
            ws.append(self.tree.item(item, "values"))
        wb.save(path)
        messagebox.showinfo("Dışa Aktar", f"Excel dosyası oluşturuldu:\n{path}")
