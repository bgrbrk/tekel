import tkinter as tk
from tkinter import ttk, messagebox
from database import baglan, urun_kaydet_veya_guncelle, stok_degistir

class StokEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw); self.app=app; self.insa_et()
    def insa_et(self):
        ust=ttk.Frame(self); ust.pack(fill="x")
        ttk.Button(ust,text="⮌ Ana Menü",style="Big.TButton",command=self.app.goster_panel).pack(side="left",padx=8,pady=8)
        ttk.Label(ust,text="Stok Yönetimi",font=("Segoe UI",28,"bold")).pack(side="left",padx=12,pady=8)
        bar=ttk.Frame(self); bar.pack(fill="x",pady=8)
        ttk.Button(bar,text="Stok Raporu (Barkod + Tarih)",command=self.rapor).pack(side="left",padx=6)
        ttk.Button(bar,text="Ürün Ekle/Düzenle",command=self.urun_duzenle).pack(side="left",padx=6)
        self.tv=ttk.Treeview(self,columns=("barkod","urun","stok","fiyat"),show="headings",height=18)
        for c in ("barkod","urun","stok","fiyat"): self.tv.heading(c,text=c.upper())
        self.tv.column("stok",anchor="e"); self.tv.column("fiyat",anchor="e")
        self.tv.pack(fill="both",expand=True,padx=12,pady=12)
        self.yukle()
    def yukle(self):
        for i in self.tv.get_children(): self.tv.delete(i)
        c=baglan(); rows=c.execute("SELECT barcode,name,stock,sale_price_tl FROM products ORDER BY name").fetchall(); c.close()
        for bc,n,st,pr in rows: self.tv.insert("", "end", values=(bc,n,st,f"{pr:.2f}"))
    def urun_duzenle(self):
        win=tk.Toplevel(self); win.title("Ürün Ekle/Düzenle")
        ttk.Label(win,text="Barkod:").grid(row=0,column=0,sticky="e"); eb=ttk.Entry(win,width=24); eb.grid(row=0,column=1,padx=6)
        ttk.Label(win,text="Ad:").grid(row=1,column=0,sticky="e"); en=ttk.Entry(win,width=32); en.grid(row=1,column=1,padx=6)
        ttk.Label(win,text="Fiyat (TL):").grid(row=2,column=0,sticky="e"); ef=ttk.Entry(win,width=16); ef.grid(row=2,column=1,padx=6)
        ttk.Label(win,text="KDV (%):").grid(row=3,column=0,sticky="e"); ek=ttk.Entry(win,width=10); ek.grid(row=3,column=1,padx=6)
        ttk.Label(win,text="Kategori:").grid(row=4,column=0,sticky="e"); from json import load; import os
        ayar_yol=os.path.join(os.path.dirname(__file__),"..","config","settings.json"); 
        try:
            kat=load(open(ayar_yol,"r",encoding="utf-8"))["kategoriler"]
        except Exception:
            kat=["Alkollü","Alkolsüz","Sigara","Market"]
        cb=ttk.Combobox(win,values=kat,state="readonly"); cb.grid(row=4,column=1,padx=6); cb.current(0)
        def kaydet():
            try: fiyat=float(ef.get().replace(",",".")); kdv=int(ek.get() or 20)
            except: messagebox.showerror("Hata","Geçerli fiyat/KDV giriniz."); return
            if not eb.get().strip() or not en.get().strip(): messagebox.showwarning("Zorunlu","Barkod ve Ad zorunludur."); return
            urun_kaydet_veya_guncelle(eb.get().strip(), en.get().strip(), fiyat, kdv, cb.get())
            messagebox.showinfo("Ürün","Kaydedildi."); self.yukle(); win.destroy()
        ttk.Button(win,text="Kaydet",command=kaydet).grid(row=5,column=0,columnspan=2,sticky="ew",pady=8)
    def rapor(self):
        win=tk.Toplevel(self); win.title("Stok Raporu")
        f=ttk.Frame(win); f.pack(fill="x",padx=8,pady=8)
        ttk.Label(f,text="Barkod:").grid(row=0,column=0,sticky="e"); eb=ttk.Entry(f,width=24); eb.grid(row=0,column=1,padx=6); eb.focus_set()
        ttk.Label(f,text="Başlangıç (YYYY-AA-GG):").grid(row=0,column=2,sticky="e"); ef=ttk.Entry(f,width=16); ef.grid(row=0,column=3,padx=6)
        ttk.Label(f,text="Bitiş (YYYY-AA-GG):").grid(row=0,column=4,sticky="e"); et=ttk.Entry(f,width=16); et.grid(row=0,column=5,padx=6)
        tv=ttk.Treeview(win,columns=("tarih","tip","adet","ref","not"),show="headings",height=16)
        for c in ("tarih","tip","adet","ref","not"): tv.heading(c,text=c.upper())
        tv.column("adet",anchor="e")
        tv.pack(fill="both",expand=True,padx=8,pady=8)
        lb=ttk.Label(win,font=("Segoe UI",16,"bold")); lb.pack(pady=8)
        def calistir():
            for i in tv.get_children(): tv.delete(i)
            bc=eb.get().strip()
            if not bc: messagebox.showwarning("Uyarı","Barkod giriniz/okutunuz."); return
            c=baglan(); r=c.execute("SELECT id,name FROM products WHERE barcode=?", (bc,)).fetchone()
            if not r: c.close(); messagebox.showwarning("Yok","Ürün bulunamadı."); return
            pid,pn=r; q="SELECT date,type,qty,ref,note FROM stock_movements WHERE product_id=?"; prm=[pid]
            if ef.get().strip(): q+=" AND date>=?"; prm.append(ef.get().strip())
            if et.get().strip(): q+=" AND date<=?"; prm.append(et.get().strip()+"T23:59:59")
            q+=" ORDER BY date"; rows=c.execute(q,prm).fetchall(); c.close()
            g=cik=duz=0
            for d,t,qt,rf,no in rows:
                tv.insert("", "end", values=(d,t,qt,rf,no)); 
                g+=qt if t=="in" else 0; cik+=qt if t=="out" else 0; duz+=qt if t=="adjust" else 0
            lb.config(text=f"{pn} — GİRİŞ: {g} | ÇIKIŞ: {cik} | DÜZELTME: {duz}")
        ttk.Button(win,text="Filtrele",command=calistir).pack(pady=8)
