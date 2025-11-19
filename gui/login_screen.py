# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import database

class LoginScreen(tk.Frame):
    def __init__(self, master, on_login_ok):
        super().__init__(master, bg="#e0dfdb")
        self.master = master
        self.on_login_ok = on_login_ok
        self.build()

    def add_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(foreground="gray")

        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.config(foreground="black")

        def on_focus_out(event):
            if entry.get().strip() == "":
                entry.insert(0, text)
                entry.config(foreground="gray")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def build(self):
        # Logoları yükle
        self.turco_logo = tk.PhotoImage(file="assets/turco_tekel.png")
        self.bay_logo = tk.PhotoImage(file="assets/baybilisimfinal.png")

        # Boyut düzeni
        self.turco_logo = self.turco_logo.subsample(1, 1)
        self.bay_logo = self.bay_logo.subsample(6, 6)

        # EK: Elemanları yukarı aldık (y_offset ↓ burada)
        container = tk.Frame(self, bg="#e0dfdb")
        container.place(relx=0.5, rely=0.42, anchor="center")

        tk.Label(container, image=self.turco_logo, bg="#e0dfdb").pack(pady=(0, 10))

        # Kullanıcı adı
        self.username_entry = ttk.Entry(container, width=26)
        self.username_entry.pack(pady=5)
        self.add_placeholder(self.username_entry, "Kullanıcı Adı")
        self.username_entry.focus()

        # Şifre
        self.password_entry = ttk.Entry(container, width=26, show="")
        self.password_entry.pack(pady=5)
        self.add_placeholder(self.password_entry, "Şifre")

        # Şifre maskesi
        self.password_entry.bind("<KeyRelease>", lambda e:
            self.password_entry.config(show="*" if self.password_entry.get() not in ("", "Şifre") else "")
        )

        # PARLAMA EFEKTİ BUTON
        self.login_btn = tk.Label(container, text="  Giriş Yap  ", bg="#d2c29d", fg="black",
                                  font=("Segoe UI", 13, "bold"), bd=2, relief="raised", cursor="hand2")
        self.login_btn.pack(pady=12)

        self.login_btn.bind("<Button-1>", lambda e: self.do_login())
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#f5e6b8"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg="#d2c29d"))

        # Enter ile login
        self.master.bind("<Return>", lambda e: self.do_login())

        # Sol alt Bay Bilişim
        tk.Label(self, image=self.bay_logo, bg="#e0dfdb").place(relx=0.00, rely=1.06, anchor="sw")

        # Sağ alt Developer
        tk.Label(self, text="Developer: Buğra Berk Yalı", bg="#e0dfdb",
                 fg="#000000", font=("Arial", 11, "italic")).place(relx=0.98, rely=0.98, anchor="se")

    def do_login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()

        if u in ("", "Kullanıcı Adı") or p in ("", "Şifre"):
            messagebox.showwarning("Uyarı", "Lütfen kullanıcı adı ve şifre girin.")
            return

        info = database.giris(u, p)
        if info:
            self.on_login_ok(info)
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış.")
