# gui/dashboard.py
import tkinter as tk
from tkinter import ttk

PALET={
    "satis":"#22c55e",
    "alis":"#3b82f6",
    "stok":"#f97316",
    "toptanci":"#a855f7",
    "kasa":"#64748b",
    "yonetici":"#f59e0b",
    "cikis":"#ef4444"
}

class Panel(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw)
        self.app = app
        self.insa_et()

    def b(self,parent,text,key,cmd):
        return tk.Button(
            parent,text=text,command=cmd,
            bg=PALET[key],fg="white",
            font=("Segoe UI",28,"bold"),
            relief="flat",bd=0,height=2,
            cursor="hand2",activebackground=PALET[key]
        )

    def insa_et(self):
        ust=ttk.Frame(self); ust.pack(fill="x")
        ttk.Label(ust,text=f"Merhaba, {self.app.kullanici['username']}",font=("Segoe UI",26,"bold")).pack(side="left",padx=16,pady=10)

        from utils.currency_updater import son_kurlar
        kur = son_kurlar()
        if kur:
            kur_text = " | ".join([f"{k}: {v[0]:.2f}" for k,v in kur.items()])
            ttk.Label(ust,text=f"Kurlar: {kur_text}",font=("Segoe UI",18)).pack(side="right",padx=16)

        grid=tk.Frame(self,bg="#f3f4f6"); grid.pack(expand=True,fill="both",padx=24,pady=24)

        for r in range(2): grid.rowconfigure(r,weight=1)
        for c in range(4): grid.columnconfigure(c,weight=1)

        self.b(grid,"Satış","satis",self.app.goster_satis).grid(row=0,column=0,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Alış (QR/Fatura)","alis",self.app.goster_alis).grid(row=0,column=1,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Stok Yönetimi","stok",self.app.goster_stok).grid(row=0,column=2,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Toptancı Cari","toptanci",self.app.goster_toptanci).grid(row=0,column=3,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Kasa İşlemleri","kasa",self.app.goster_kasa).grid(row=1,column=0,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Yönetici","yonetici",self.app.goster_yonetici).grid(row=1,column=1,padx=16,pady=16,sticky="nsew")
        self.b(grid,"Çıkış","cikis",self.app.cikis).grid(row=1,column=2,padx=16,pady=16,sticky="nsew")
