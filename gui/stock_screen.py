# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

CATEGORIES = ["Alkollü", "Alkolsüz", "Sigara", "Market"]

class AutocompleteEntry(ttk.Entry):
    """Elle yazarken liste önerisi çıkaran toptancı kutusu"""
    def __init__(self, master, values, **kwargs):
        super().__init__(master, **kwargs)
        self.values = values
        self.lb = None
        self.bind("<KeyRelease>", self._update_list)

    def _update_list(self, event):
        if self.lb:
            self.lb.destroy()
        text = self.get().strip().lower()
        if not text:
            return
        matches = [v for v in self.values if text in v.lower()]
        if not matches:
            return
        self.lb = tk.Listbox(self.master, height=min(5, len(matches)))
        for m in matches:
            self.lb.insert("end", m)
        self.lb.bind("<<ListboxSelect>>", self._select_item)
        self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())

    def _select_item(self, event):
        if not self.lb:
            return
        sel = self.lb.get(self.lb.curselection())
        self.delete(0, "end")
        self.insert(0, sel)
        self.lb.destroy()
        self.lb = None

class StockScreen(ttk.Frame):
    def __init__(self, master, on_back):
        super().__init__(master, padding=8)
        self.on_back = on_back
        self._build()
        self._load()

    def _build(self):
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        # Ana Menü
        tk.Button(top, text="⮌ Ana Menü", command=self.on_back,
                  bg="#800000", fg="white", font=("Segoe UI", 12, "bold"),
                  cursor="hand2").pack(side="left", padx=(0, 10), ipadx=10, ipady=3)

        ttk.Label(top, text="📦 Stok Yönetimi", font=("Segoe UI", 22, "bold")
                  ).pack(side="left", padx=(0, 10))

        # Sağ butonlar
        tk.Button(top, text="➕ Ürün Ekle", bg="#17a2b8", fg="white",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=self._open_form).pack(side="right", padx=5, ipadx=10, ipady=3)

        tk.Button(top, text="✏️ Düzenle", bg="#ffc107", fg="black",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=self._edit_selected).pack(side="right", padx=5, ipadx=10, ipady=3)

        tk.Button(top, text="🗑️ Sil", bg="#dc3545", fg="white",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=self._delete_selected).pack(side="right", padx=5, ipadx=10, ipady=3)

        tk.Button(top, text="📊 Stok Raporu", bg="#6c757d", fg="white",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=self._open_report).pack(side="right", padx=5, ipadx=10, ipady=3)

        # Tablo
        cols = ("BARKOD", "ÜRÜN", "STOK", "FİYAT", "TOPTANCI", "ID")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c, anchor="center")

        self.tree.column("BARKOD", width=150, anchor="w")
        self.tree.column("ÜRÜN", width=310, anchor="w")
        self.tree.column("STOK", width=80, anchor="center")
        self.tree.column("FİYAT", width=80, anchor="center")
        self.tree.column("TOPTANCI", width=250, anchor="center")
        self.tree.column("ID", width=50, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)

    # ------------------ LİSTE YÜKLE ------------------ #
    def _load(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for bc, name, st, sp, pid, sname in database.tree_rows_for_stock():
            try:
                st = int(float(st))
            except:
                pass
            try:
                sp = f"{float(sp):.2f}"
            except:
                pass
            self.tree.insert("", "end", values=(bc, name, st, sp, sname, pid))

    # ------------------ ÜRÜN EKLE ------------------ #
    def _open_form(self):
        win = tk.Toplevel(self)
        win.title("Yeni Ürün Ekle")
        win.geometry("420x540")
        win.resizable(False, False)

        ttk.Label(win, text="Barkod:").pack(pady=4)
        e_bar = ttk.Entry(win, width=35); e_bar.pack(); e_bar.focus_set()

        ttk.Label(win, text="Ürün Adı:").pack(pady=4)
        e_name = ttk.Entry(win, width=35); e_name.pack()

        ttk.Label(win, text="Fiyat (₺):").pack(pady=4)
        e_price = ttk.Entry(win, width=35); e_price.pack()

        ttk.Label(win, text="KDV (%):").pack(pady=4)
        e_kdv = ttk.Entry(win, width=35); e_kdv.pack()

        ttk.Label(win, text="Kategori:").pack(pady=4)
        cmb_cat = ttk.Combobox(win, values=CATEGORIES, state="readonly", width=32)
        cmb_cat.pack(pady=4); cmb_cat.current(0)

        ttk.Label(win, text="Stok Miktarı:").pack(pady=4)
        e_stok = ttk.Entry(win, width=35); e_stok.pack()

        sups = database.tedarikci_listesi()
        sup_names = [f"{sid} - {name}" for sid, name, _ in sups]
        ttk.Label(win, text="Toptancı:").pack(pady=4)
        e_sup = AutocompleteEntry(win, values=sup_names, width=35)
        e_sup.pack(pady=4)

        def save():
            try:
                barcode = e_bar.get().strip()
                name = e_name.get().strip()
                price = round(float(e_price.get().strip()), 2)
                kdv = int(e_kdv.get().strip())
                cat = cmb_cat.get()
                stok = int(e_stok.get().strip())

                supplier_text = e_sup.get().strip()
                sup_id = int(supplier_text.split(" - ")[0]) if supplier_text and " - " in supplier_text else None
            except Exception as e:
                messagebox.showerror("Hata", f"Alanları doğru doldurun.\n{e}")
                return

            try:
                # 🔧 Güncel uyumlu çağrı
                pid = database.urun_kaydet_veya_guncelle(
                    barcode, name, price, kdv, cat, stok, sup_id
                )
                messagebox.showinfo("Başarılı", "Ürün kaydedildi.")
                win.destroy()
                self._load()
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt başarısız:\n{e}")

        tk.Button(win, text="Kaydet", bg="#28a745", fg="white",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=save).pack(pady=10, ipadx=10, ipady=5)

    # ------------------ DÜZENLE ------------------ #
    def _edit_selected(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Seçim Yok", "Düzenlemek için bir ürün seçin.")
            return
        barcode = self.tree.item(item, "values")[0]
        data = database.urun_getir(barcode)
        if not data:
            messagebox.showerror("Hata", "Kayıt bulunamadı.")
            return

        win = tk.Toplevel(self)
        win.title("Ürün Bilgilerini Düzenle")
        win.geometry("420x480")
        win.resizable(False, False)

        ttk.Label(win, text="Barkod:").pack(pady=4)
        e_bar = ttk.Entry(win, width=35); e_bar.insert(0, data["barcode"]); e_bar.pack()

        ttk.Label(win, text="Ürün Adı:").pack(pady=4)
        e_name = ttk.Entry(win, width=35); e_name.insert(0, data["name"]); e_name.pack()

        ttk.Label(win, text="Fiyat (₺):").pack(pady=4)
        e_price = ttk.Entry(win, width=35); e_price.insert(0, str(data["price"])); e_price.pack()

        ttk.Label(win, text="KDV (%):").pack(pady=4)
        e_kdv = ttk.Entry(win, width=35); e_kdv.insert(0, str(data["kdv"])); e_kdv.pack()

        ttk.Label(win, text="Kategori:").pack(pady=4)
        cmb_cat = ttk.Combobox(win, values=CATEGORIES, state="readonly", width=32)
        cmb_cat.pack(pady=4); cmb_cat.set(data["category"])

        sups = database.tedarikci_listesi()
        sup_names = [f"{sid} - {name}" for sid, name, _ in sups]
        ttk.Label(win, text="Toptancı:").pack(pady=4)
        e_sup = AutocompleteEntry(win, values=sup_names, width=35)
        e_sup.pack(pady=4)

        def save_edit():
            try:
                new_bar = e_bar.get().strip()
                new_name = e_name.get().strip()
                new_price = round(float(e_price.get().strip()), 2)
                new_kdv = int(e_kdv.get().strip())
                new_cat = cmb_cat.get()

                supplier_text = e_sup.get().strip()
                sup_id = int(supplier_text.split(" - ")[0]) if " - " in supplier_text else None

                con = database.baglan()
                cur = con.cursor()
                cur.execute("""
                    UPDATE products
                    SET barcode=?, name=?, price=?, kdv=?, category=?, supplier_id=?
                    WHERE barcode=?
                """, (new_bar, new_name, new_price, new_kdv, new_cat, sup_id, barcode))
                con.commit(); con.close()

                messagebox.showinfo("Başarılı", "Ürün bilgileri güncellendi.")
                win.destroy()
                self._load()
            except Exception as e:
                messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")

        tk.Button(win, text="Kaydet", bg="#28a745", fg="white",
                  font=("Segoe UI", 12, "bold"), cursor="hand2",
                  command=save_edit).pack(pady=10, ipadx=10, ipady=5)

    # ------------------ SİL ------------------ #
    def _delete_selected(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Seçim Yok", "Silmek için bir ürün seçin.")
            return
        values = self.tree.item(item, "values")
        barcode = values[0]; urun_adi = values[1]
        if not messagebox.askyesno("Onay", f"'{urun_adi}' ürününü silmek istiyor musunuz?"):
            return
        try:
            con = database.baglan()
            cur = con.cursor()
            cur.execute("DELETE FROM products WHERE barcode=?", (barcode,))
            con.commit(); con.close()
            self._load()
            messagebox.showinfo("Silindi", f"{urun_adi} başarıyla silindi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Silme işlemi başarısız:\n{e}")

    def _open_report(self):
        messagebox.showinfo("Bilgi", "Stok raporu özelliği yakında eklenecek.")
