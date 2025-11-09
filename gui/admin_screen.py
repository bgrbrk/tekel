# gui/admin_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, shutil
from tkinter import filedialog

class YoneticiEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw)
        self.app = app
        self.ayarlar = app.ayarlar

        ttk.Label(self, text="Yönetici Ayarları", font=("Segoe UI", 34, "bold")).pack(pady=20)

        # ✅ BooleanVar düzeltildi (ttk değil tk)
        self.var_fis = tk.BooleanVar(value=self.ayarlar.get("fis_yazdir", True))

        ttk.Checkbutton(self, text="Satış Sonrası Fiş Yazdır", variable=self.var_fis,
                        command=self.kaydet).pack(pady=10)

        ttk.Button(self, text="Varsayılan KDV Oranı Ayarla", command=self.set_kdv).pack(pady=10)
        ttk.Button(self, text="Yedek Al", command=self.yedek).pack(pady=10)
        ttk.Button(self, text="Ana Menü", command=self.app.goster_panel).pack(pady=40)

    def kaydet(self):
        self.ayarlar["fis_yazdir"] = self.var_fis.get()
        self.kaydet_ayar()

    def set_kdv(self):
        win = tk.Toplevel(self)
        win.title("Varsayılan KDV")
        ttk.Label(win, text="KDV (%)", font=("Segoe UI", 18)).pack(pady=10)
        e = ttk.Entry(win, font=("Segoe UI", 18))
        e.insert(0, self.ayarlar.get("varsayilan_kdv", 20))
        e.pack(pady=10)
        def save():
            self.ayarlar["varsayilan_kdv"] = int(e.get())
            self.kaydet_ayar()
            win.destroy()
        ttk.Button(win, text="Kaydet", command=save).pack(pady=10)

    def kaydet_ayar(self):
        p = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
        json.dump(self.ayarlar, open(p, "w"), indent=4)

    def yedek(self):
        hedef = filedialog.askdirectory()
        if not hedef: return
        shutil.make_archive(os.path.join(hedef, "yedek"), "zip",
                            os.path.join(os.path.dirname(__file__), ".."))
        messagebox.showinfo("Yedek", "Yedek alma tamamlandı.")
