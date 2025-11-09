from tkinter import ttk, messagebox
import tkinter as tk, json
from database import baglan, urun_kaydet_veya_guncelle, stok_degistir
from utils.barcode_reader import fatura_qr_coz
class AlisEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw); self.app=app; self.kalemler=[]; self.insa_et()
    def insa_et(self):
        ust=ttk.Frame(self); ust.pack(fill="x")
        ttk.Button(ust,text="⮌ Ana Menü",style="Big.TButton",command=self.app.goster_panel).pack(side="left",padx=8,pady=8)
        ttk.Label(ust,text="Alış / Fatura (QR)",font=("Segoe UI",28,"bold")).pack(side="left",padx=12,pady=8)
        bar=ttk.Frame(self); bar.pack(fill="x",pady=8)
        ttk.Label(bar,text="Toptancı:").pack(side="left"); self.cmb=ttk.Combobox(bar,state="readonly",width=32); self.cmb.pack(side="left",padx=6); ttk.Button(bar,text="Yenile",command=self.toptanci_yukle).pack(side="left",padx=6)
        qr=ttk.Frame(self); qr.pack(fill="x",pady=8); ttk.Label(qr,text="Fatura QR/Payload:").pack(side="left",padx=6); self.e=ttk.Entry(qr,width=64); self.e.pack(side="left",padx=6,fill="x",expand=True); ttk.Button(qr,text="Yükle",command=self.qr_yukle).pack(side="left",padx=6)
        self.tv=ttk.Treeview(self,columns=("barkod","ad","adet","fiyat"),show="headings",height=18)
        for c in ("barkod","ad","adet","fiyat"): self.tv.heading(c,text=c.upper())
        self.tv.column("adet",anchor="e"); self.tv.column("fiyat",anchor="e")
        self.tv.pack(fill="both",expand=True,padx=12,pady=12)
        ttk.Button(self,text="Kaydet",style="Big.TButton",command=self.kaydet).pack(pady=8,side="right",anchor="e")
        self.toptanci_yukle()
    def toptanci_yukle(self):
        c=baglan(); rows=c.execute("SELECT id,name FROM suppliers ORDER BY name").fetchall(); c.close()
        self.sup={n:i for i,n in rows}; self.cmb["values"]=list(self.sup.keys())
        if rows and not self.cmb.get(): self.cmb.current(0)
    def qr_yukle(self):
        data=fatura_qr_coz(self.e.get().strip()); items=data.get("items",[])
        if not items: messagebox.showwarning("QR","İçerik okunamadı."); return
        self.kalemler=[]
        for it in items:
            bc=str(it.get("barcode","")); ad=it.get("name","Ürün"); qty=int(it.get("qty",1)); fiyat=float(it.get("price",0.0))
            urun_kaydet_veya_guncelle(bc,ad,fiyat,kdv=int(it.get("kdv",20)),category=it.get("category"))
            self.kalemler.append({"barkod":bc,"ad":ad,"adet":qty,"fiyat":fiyat})
        self.yenile()
    def yenile(self):
        for i in self.tv.get_children(): self.tv.delete(i)
        for it in self.kalemler: self.tv.insert("", "end", values=(it["barkod"],it["ad"],it["adet"],f"{it['fiyat']:.2f}"))
    def kaydet(self):
        if not self.kalemler or not self.cmb.get(): return
        sid=self.sup[self.cmb.get()]; toplam=0.0
        c=baglan(); cur=c.cursor()
        for it in self.kalemler:
            qty=int(it["adet"]); fiyat=float(it["fiyat"]); toplam+=qty*fiyat
            cur.execute("SELECT id FROM products WHERE barcode=?", (it["barkod"],)); pid=cur.fetchone()[0]
            cur.execute("UPDATE products SET purchase_price_tl=? WHERE id=?", (fiyat, pid))
            stok_degistir(pid, qty, "in", ref="purchase")
        import datetime, json as js
        now=datetime.datetime.now().isoformat(timespec='seconds')
        cur.execute("INSERT INTO purchases(supplier_id,date,total_tl,items_json) VALUES(?,?,?,?)",(sid,now,toplam,js.dumps(self.kalemler,ensure_ascii=False)))
        cur.execute("INSERT INTO supplier_ledger(supplier_id,date,type,amount_tl,note) VALUES(?,?,?,?,?)",(sid,now,"purchase",toplam,"QR faturadan giriş"))
        cur.execute("UPDATE suppliers SET balance_tl=COALESCE(balance_tl,0)+? WHERE id=?", (toplam, sid))
        c.commit(); c.close(); messagebox.showinfo("Alış","Kaydedildi."); self.kalemler=[]; self.yenile()
