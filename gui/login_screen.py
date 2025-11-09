# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

class LoginScreen(ttk.Frame):
    def __init__(self, master, on_login_ok):
        super().__init__(master, padding=20)
        self.on_login_ok = on_login_ok
        self._build()

    def _build(self):
        ttk.Label(self, text="Turco Tekel POS - Giriş", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,20))
        ttk.Label(self, text="Kullanıcı Adı:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Şifre:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.e_user = ttk.Entry(self, width=30); self.e_user.grid(row=1, column=1, padx=5, pady=5)
        self.e_pass = ttk.Entry(self, width=30, show="*"); self.e_pass.grid(row=2, column=1, padx=5, pady=5)

        def do_login():
            info = database.giris(self.e_user.get().strip(), self.e_pass.get().strip())
            if info: self.on_login_ok(info)
            else: messagebox.showerror("Giriş Hatası", "Kullanıcı adı veya şifre hatalı.")

        btn = tk.Button(self, text="GİRİŞ", bg="#28a745", fg="white", font=("Segoe UI", 12, "bold"), height=2, command=do_login)
        btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        self.columnconfigure(1, weight=1); self.e_user.focus_set()
        self.e_user.bind("<Return>", lambda e: do_login())
        self.e_pass.bind("<Return>", lambda e: do_login())
