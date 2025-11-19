# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database


class SuppliersScreen(ttk.Frame):
    def __init__(self, master, on_nav):
        super().__init__(master, padding=12)
        self.on_nav = on_nav
        self._arayuz_olustur()

    # ------------------ ARAYÜZ ------------------ #
    def _arayuz_olustur(self):
        ust = ttk.Frame(self)
        ust.pack(fill="x", pady=(0, 10))

        # 🔙 Ana Menü
        btn_ana = tk.Button(
            ust, text="⬅️ Ana Menü", bg="#800000", fg="white",
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            command=self.on_nav  # parametresiz
        )
        btn_ana.pack(side="left", padx=(0, 10), ipadx=10, ipady=3)

        # Başlık
        ttk.Label(
            ust, text="🤝 Toptancılar / Cari Yönetimi",
            font=("Segoe UI", 22, "bold")
        ).pack(side="left", padx=(0, 10))

        # Sağdaki butonlar
        btn_yeni = tk.Button(
            ust, text="➕ Yeni Toptancı", bg="#28a745", fg="white",
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            command=self._toptanci_ekle_penceresi
        )
        btn_yeni.pack(side="right", padx=5, ipadx=10, ipady=3)

        btn_cari = tk.Button(
            ust, text="🧾 Cari Defteri", bg="#007bff", fg="white",
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            command=self._cari_defterini_goster
        )
        btn_cari.pack(side="right", padx=5, ipadx=10, ipady=3)

        btn_duzelt = tk.Button(
            ust, text="✏️ Düzelt", bg="#ffc107", fg="black",
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            command=self._toptanci_duzelt_penceresi
        )
        btn_duzelt.pack(side="right", padx=5, ipadx=10, ipady=3)

        btn_sil = tk.Button(
            ust, text="🗑️ Sil", bg="#dc3545", fg="white",
            font=("Segoe UI", 12, "bold"), cursor="hand2",
            command=self._toptanci_sil
        )
        btn_sil.pack(side="right", padx=5, ipadx=10, ipady=3)

        # Tablo
        sutunlar = (
            "id", "ad", "vergi_no", "vergi_dairesi",
            "sorumlu", "telefon", "adres", "bakiye"
        )
        self.liste = ttk.Treeview(self, columns=sutunlar, show="headings", height=18)
        basliklar = [
            "ID", "Toptancı Ünvanı", "Vergi No", "Vergi Dairesi",
            "Sorumlu Kişi", "Telefon", "Adres", "Bakiye (₺)"
        ]
        for c, baslik in zip(sutunlar, basliklar):
            self.liste.heading(c, text=baslik)
            self.liste.column(c, anchor="w", width=140)
        self.liste.pack(fill="both", expand=True)

        self._toptancilari_yukle()

    # ------------------ LİSTEYİ YÜKLE ------------------ #
    def _toptancilari_yukle(self):
        for i in self.liste.get_children():
            self.liste.delete(i)
        try:
            con = database.baglan()
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS suppliers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    tax_number TEXT,
                    tax_office TEXT,
                    contact_person TEXT,
                    phone TEXT,
                    address TEXT,
                    balance REAL DEFAULT 0
                )
            """)
            cur.execute("""
                SELECT id, name, tax_number, tax_office,
                       contact_person, phone, address, balance
                FROM suppliers ORDER BY name ASC
            """)
            rows = cur.fetchall()
            con.close()
            for r in rows:
                self.liste.insert("", "end", values=r)
        except Exception as e:
            messagebox.showerror("Hata", f"Toptancılar yüklenemedi:\n{e}")

    # ------------------ EKLE ------------------ #
    def _toptanci_ekle_penceresi(self):
        win = tk.Toplevel(self)
        win.title("Yeni Toptancı Ekle")
        win.geometry("480x520")
        win.resizable(False, False)

        ttk.Label(win, text="Toptancı Ünvanı:").pack(pady=4)
        e_name = ttk.Entry(win, width=50); e_name.pack()
        ttk.Label(win, text="Vergi No:").pack(pady=4)
        e_vno = ttk.Entry(win, width=50); e_vno.pack()
        ttk.Label(win, text="Vergi Dairesi:").pack(pady=4)
        e_vd = ttk.Entry(win, width=50); e_vd.pack()
        ttk.Label(win, text="Sorumlu Kişi:").pack(pady=4)
        e_sorumlu = ttk.Entry(win, width=50); e_sorumlu.pack()
        ttk.Label(win, text="Telefon:").pack(pady=4)
        e_tel = ttk.Entry(win, width=50); e_tel.pack()
        ttk.Label(win, text="Adres:").pack(pady=4)
        e_adr = tk.Text(win, width=45, height=3); e_adr.pack(pady=4)

        def kaydet():
            name = e_name.get().strip()
            if not name:
                messagebox.showwarning("Eksik Bilgi", "Toptancı ünvanı zorunludur.")
                return
            try:
                con = database.baglan()
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO suppliers 
                    (name, tax_number, tax_office, contact_person, phone, address, balance)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (
                    name,
                    e_vno.get().strip(),
                    e_vd.get().strip(),
                    e_sorumlu.get().strip(),
                    e_tel.get().strip(),
                    e_adr.get("1.0", tk.END).strip()
                ))
                con.commit(); con.close()
                messagebox.showinfo("Başarılı", f"{name} eklendi.")
                win.destroy()
                self._toptancilari_yukle()
            except Exception as e:
                messagebox.showerror("Hata", f"Kayıt başarısız:\n{e}")

        ttk.Button(win, text="Kaydet", command=kaydet).pack(pady=12)

    # ------------------ DÜZELT ------------------ #
    def _toptanci_duzelt_penceresi(self):
        sid = self._secili_toptanci_id()
        if not sid:
            messagebox.showwarning("Seçim", "Bir toptancı seçin.")
            return
        con = database.baglan()
        cur = con.cursor()
        cur.execute("""
            SELECT name, tax_number, tax_office, contact_person, phone, address 
            FROM suppliers WHERE id=?
        """, (sid,))
        row = cur.fetchone()
        con.close()
        if not row:
            messagebox.showerror("Hata", "Kayıt bulunamadı.")
            return

        win = tk.Toplevel(self)
        win.title("Toptancı Düzelt")
        win.geometry("480x520")
        win.resizable(False, False)

        ttk.Label(win, text="Toptancı Ünvanı:").pack(pady=4)
        e_name = ttk.Entry(win, width=50); e_name.insert(0, row[0]); e_name.pack()
        ttk.Label(win, text="Vergi No:").pack(pady=4)
        e_vno = ttk.Entry(win, width=50); e_vno.insert(0, row[1] or ""); e_vno.pack()
        ttk.Label(win, text="Vergi Dairesi:").pack(pady=4)
        e_vd = ttk.Entry(win, width=50); e_vd.insert(0, row[2] or ""); e_vd.pack()
        ttk.Label(win, text="Sorumlu Kişi:").pack(pady=4)
        e_sorumlu = ttk.Entry(win, width=50); e_sorumlu.insert(0, row[3] or ""); e_sorumlu.pack()
        ttk.Label(win, text="Telefon:").pack(pady=4)
        e_tel = ttk.Entry(win, width=50); e_tel.insert(0, row[4] or ""); e_tel.pack()
        ttk.Label(win, text="Adres:").pack(pady=4)
        e_adr = tk.Text(win, width=45, height=3); e_adr.insert("1.0", row[5] or ""); e_adr.pack(pady=4)

        def kaydet():
            name = e_name.get().strip()
            if not name:
                messagebox.showwarning("Eksik", "Toptancı ünvanı zorunludur.")
                return
            try:
                con = database.baglan()
                cur = con.cursor()
                cur.execute("""
                    UPDATE suppliers 
                    SET name=?, tax_number=?, tax_office=?, contact_person=?, phone=?, address=? 
                    WHERE id=?
                """, (
                    name,
                    e_vno.get().strip(),
                    e_vd.get().strip(),
                    e_sorumlu.get().strip(),
                    e_tel.get().strip(),
                    e_adr.get("1.0", tk.END).strip(),
                    sid
                ))
                con.commit(); con.close()
                messagebox.showinfo("Başarılı", "Kayıt güncellendi.")
                win.destroy()
                self._toptancilari_yukle()
            except Exception as e:
                messagebox.showerror("Hata", f"Güncelleme başarısız:\n{e}")

        ttk.Button(win, text="Kaydet", command=kaydet).pack(pady=12)

    # ------------------ SİL ------------------ #
    def _toptanci_sil(self):
        sid = self._secili_toptanci_id()
        if not sid:
            messagebox.showwarning("Seçim", "Bir toptancı seçin.")
            return
        con = database.baglan()
        cur = con.cursor()

        hareket_sayisi = 0
        try:
            cur.execute("SELECT COUNT(*) FROM purchases WHERE supplier_id=?", (sid,))
            hareket_sayisi += cur.fetchone()[0]
        except:
            pass
        try:
            cur.execute("SELECT COUNT(*) FROM supplier_ledger WHERE supplier_id=?", (sid,))
            hareket_sayisi += cur.fetchone()[0]
        except:
            pass

        if hareket_sayisi > 0:
            con.close()
            messagebox.showwarning("Engellendi", "Bu toptancının cari hareketleri var, silinemez.")
            return

        if not messagebox.askyesno("Onay", "Bu toptancıyı silmek istiyor musunuz?"):
            con.close(); return

        try:
            cur.execute("DELETE FROM suppliers WHERE id=?", (sid,))
            con.commit(); con.close()
            self._toptancilari_yukle()
            messagebox.showinfo("Silindi", "Toptancı başarıyla silindi.")
        except Exception as e:
            con.close()
            messagebox.showerror("Hata", f"Silme başarısız:\n{e}")

    # ------------------ CARI DEFTERI ------------------ #
    def _cari_defterini_goster(self):
        messagebox.showinfo("Bilgi", "Cari defteri özelliği bir sonraki sürümde aktif edilecek.")

    # ------------------ YARDIMCI ------------------ #
    def _secili_toptanci_id(self):
        secim = self.liste.selection()
        if not secim:
            return None
        degerler = self.liste.item(secim[0])["values"]
        return degerler[0] if degerler else None
