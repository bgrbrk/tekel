# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, hashlib
from utils.backup import yedek_al

class AdminScreen(ttk.Frame):
    def __init__(self, master, on_back, user, settings_path):
        super().__init__(master, padding=8)
        self.on_back = on_back; self.user = user
        self.settings_path = settings_path; self.settings = self._read_settings()
        self._build()

    def _read_settings(self):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {"yazdir_fis": False, "varsayilan_kdv": 20}

    def _save_settings(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def _build(self):
        top = ttk.Frame(self); top.grid(row=0, column=0, sticky="ew")
        ttk.Button(top, text="⮌ Ana Menü", command=self.on_back).pack(side="left")
        ttk.Label(top, text="YÖNETİCİ", font=("Segoe UI", 18, "bold")).pack(side="left", padx=12)

        if self.user.get("role")!="admin":
            ttk.Label(self, text="Bu bölümü görmek için yetkiniz yok.", foreground="red").grid(row=1, column=0, sticky="w", pady=10)
            return

        nb = ttk.Notebook(self); nb.grid(row=1, column=0, sticky="nsew")
        # Ayarlar
        frm = ttk.Frame(nb, padding=10); nb.add(frm, text="Ayarlar")
        self.yazdir_var = tk.BooleanVar(value=bool(self.settings.get("yazdir_fis", False)))
        ttk.Checkbutton(frm, text="Satıştan sonra fiş yazdır", variable=self.yazdir_var).grid(row=0, column=0, sticky="w", pady=6)
        ttk.Label(frm, text="Varsayılan KDV (%):").grid(row=1, column=0, sticky="w")
        self.e_kdv = ttk.Entry(frm, width=10); self.e_kdv.insert(0, str(self.settings.get("varsayilan_kdv", 20))); self.e_kdv.grid(row=1, column=1, sticky="w", padx=6)
        def save_set():
            try:
                self.settings["varsayilan_kdv"] = int(self.e_kdv.get().strip())
                self.settings["yazdir_fis"] = bool(self.yazdir_var.get())
            except Exception:
                messagebox.showerror("Hata","Ayarlar kaydedilemedi."); return
            self._save_settings(); messagebox.showinfo("Ayarlar","Kaydedildi.")
        tk.Button(frm, text="Kaydet", bg="#28a745", fg="white", font=("Segoe UI", 14, "bold"), height=2, command=save_set).grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")

        # Kullanıcı ekle
        ufrm = ttk.Frame(nb, padding=10); nb.add(ufrm, text="Kullanıcı Ekle")
        ttk.Label(ufrm, text="Kullanıcı Adı:").grid(row=0, column=0, sticky="w")
        e_user = ttk.Entry(ufrm, width=20); e_user.grid(row=0, column=1, sticky="w", padx=6)
        ttk.Label(ufrm, text="Şifre:").grid(row=1, column=0, sticky="w")
        e_pass = ttk.Entry(ufrm, width=20, show="*"); e_pass.grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(ufrm, text="Rol (admin/kasiyer):").grid(row=2, column=0, sticky="w")
        e_role = ttk.Entry(ufrm, width=20); e_role.insert(0,"kasiyer"); e_role.grid(row=2, column=1, sticky="w", padx=6)
        def add_user():
            import database
            u = e_user.get().strip(); p = e_pass.get().strip(); r = e_role.get().strip()
            if not u or not p or r not in ("admin","kasiyer"):
                messagebox.showerror("Hata","Alanları doğru giriniz."); return
            con = database._conn(); cur = con.cursor()
            try:
                cur.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                            (u, hashlib.sha256(p.encode()).hexdigest(), r))
                con.commit(); messagebox.showinfo("Kullanıcı","Eklendi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Eklenemedi: {e}")
            finally: con.close()
        tk.Button(ufrm, text="Ekle", bg="#007bff", fg="white", font=("Segoe UI", 14, "bold"), height=2, command=add_user).grid(row=3, column=0, columnspan=2, pady=8, sticky="ew")

        # Yedek
        bfrm = ttk.Frame(nb, padding=10); nb.add(bfrm, text="Yedek Al")
        import os
        dbp = os.path.join(os.path.dirname(__file__), "..", "turcotekel.db")
        setp = os.path.join(os.path.dirname(__file__), "..", "config","settings.json")
        tk.Button(bfrm, text="DB + Ayarlar Yedeği", bg="#6c757d", fg="white", font=("Segoe UI", 14, "bold"), height=2,
                  command=lambda: yedek_al(dbp, setp)).pack(fill="x")

        # SQL Raporu
        rfrm = ttk.Frame(nb, padding=10); nb.add(rfrm, text="SQL Raporu")
        ttk.Label(rfrm, text="Sadece SELECT sorguları çalıştırılır.", foreground="gray").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,6))
        self.e_sql = tk.Text(rfrm, height=4, width=80); self.e_sql.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.tv = ttk.Treeview(rfrm, show="headings", height=14); self.tv.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=6)
        rfrm.columnconfigure(0, weight=1); rfrm.rowconfigure(3, weight=1)
        def run_sql():
            q = self.e_sql.get("1.0","end").strip().rstrip(";")
            if not q.lower().startswith("select"):
                messagebox.showerror("Hata","Sadece SELECT sorguları izinli."); return
            try:
                import database
                con = database._conn(); cur = con.cursor(); cur.execute(q); rows = cur.fetchall()
                headers = [d[0] for d in cur.description] if cur.description else []
                self.tv["columns"] = headers
                for c in headers: self.tv.heading(c, text=c); self.tv.column(c, width=140, anchor="w")
                for i in self.tv.get_children(): self.tv.delete(i)
                for r in rows: self.tv.insert("", "end", values=[str(x) for x in r])
                con.close()
            except Exception as e:
                messagebox.showerror("SQL Hatası", str(e))
        tk.Button(rfrm, text="Çalıştır", bg="#007bff", fg="white", font=("Segoe UI", 14, "bold"), height=2, command=run_sql).grid(row=2, column=2, sticky="e", pady=6)
