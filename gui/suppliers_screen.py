import tkinter as tk
from tkinter import ttk, messagebox
from database import baglan
from utils.helpers import tl

class ToptanciEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw); self.app=app; self.insa_et()
    def insa_et(self):
        ust=ttk.Frame(self); ust.pack(fill="x")
        ttk.Button(ust,text="⮌ Ana Menü",style="Big.TButton",command=self.app.goster_panel).pack(side="left",padx=8,pady=8)
        ttk.Label(ust,text="Toptancı Cari",font=("Segoe UI",28,"bold")).pack(side="left",padx=12,pady=8)
        bar=ttk.Frame(self); bar.pack(fill="x",pady=8)
        ttk.Label(bar,text="Seçili Toptancı:").pack(side="left",padx=(12,6))
        self.cmb=ttk.Combobox(bar,state="readonly",width=32); self.cmb.pack(side="left")
        self.cmb.bind("<<ComboboxSelected>>",lambda e:self.yukle())
        ttk.Button(bar,text="Ödeme Gir",command=self.odeme).pack(side="left",padx=6)
        ttk.Button(bar,text="Cari Raporu",command=self.rapor).pack(side="left",padx=6)
        self.tv=ttk.Treeview(self,columns=("tarih","aciklama","tutar"),show="headings",height=18)
        self.tv.heading("tarih",text="TARİH"); self.tv.column("tarih",anchor="w",width=220)
        self.tv.heading("aciklama",text="AÇIKLAMA"); self.tv.column("aciklama",anchor="w",width=600)
        self.tv.heading("tutar",text="TUTAR"); self.tv.column("tutar",anchor="e",width=200)
        self.tv.pack(fill="both",expand=True,padx=12,pady=12)
        self.lbl=ttk.Label(self,font=("Segoe UI",18,"bold")); self.lbl.pack(pady=10)
        self.yenile()
    def yenile(self):
        c=baglan(); rows=c.execute("SELECT id,name,balance_tl FROM suppliers ORDER BY name").fetchall(); c.close()
        self.sup={n:(i,b) for i,n,b in rows}; self.cmb["values"]=list(self.sup.keys())
        if rows: self.cmb.current(0); self.yukle()
    def yukle(self):
        for i in self.tv.get_children(): self.tv.delete(i)
        ad=self.cmb.get(); sid,bal=self.sup.get(ad,(None,0))
        if not sid: return
        c=baglan(); rows=c.execute("SELECT date,type,amount_tl,note FROM supplier_ledger WHERE supplier_id=? ORDER BY date DESC",(sid,)).fetchall(); c.close()
        for d,t,a,n in rows:
            is_borc = (t=="purchase")
            iid=self.tv.insert("", "end", values=(d, n or t, f"{a if is_borc else -a:.2f}"))
            self.tv.item(iid, tags=("borc" if is_borc else "alacak",))
        self.tv.tag_configure("borc",foreground="red"); self.tv.tag_configure("alacak",foreground="green")
        self.lbl.config(text=("Cari Borç: "+f"{bal:.2f} TL") if bal>0 else ("Alacak: "+f"{-bal:.2f} TL" if bal<0 else "Cari Kapalı"), foreground="red" if bal>0 else ("green" if bal<0 else "black"))
    def odeme(self):
        ad=self.cmb.get(); sid,_=self.sup.get(ad,(None,0))
        if not sid: return
        win=tk.Toplevel(self); win.title("Toptancı Ödeme")
        ttk.Label(win,text="Tutar (TL):").grid(row=0,column=0,sticky="e",padx=6,pady=6); et=ttk.Entry(win,width=18); et.grid(row=0,column=1,padx=6,pady=6)
        ttk.Label(win,text="Not:").grid(row=1,column=0,sticky="e",padx=6,pady=6); en=ttk.Entry(win,width=32); en.grid(row=1,column=1,padx=6,pady=6)
        def kaydet():
            try: tutar=float(et.get().replace(",","."))
            except: messagebox.showerror("Hata","Geçerli tutar girin."); return
            if not en.get().strip(): messagebox.showwarning("Zorunlu","Not girmek zorunludur."); return
            c=baglan(); cur=c.cursor()
            now=__import__('datetime').datetime.now().isoformat(timespec='seconds')
            cur.execute("INSERT INTO supplier_ledger(supplier_id,date,type,amount_tl,note) VALUES(?,?,?,?,?)",(sid,now,"payment",tutar,en.get().strip()))
            cur.execute("UPDATE suppliers SET balance_tl=COALESCE(balance_tl,0)-? WHERE id=?", (tutar,sid))
            c.commit(); c.close(); messagebox.showinfo("Ödeme","Kayıt edildi."); win.destroy(); self.yukle()
        ttk.Button(win,text="Kaydet",command=kaydet).grid(row=2,column=0,columnspan=2,sticky="ew",pady=8)
    def rapor(self):
        win=tk.Toplevel(self); win.title("Cari Rapor")
        f=ttk.Frame(win); f.pack(fill="x",padx=8,pady=8)
        ttk.Label(f,text="Başlangıç (YYYY-AA-GG):").grid(row=0,column=0,sticky="e"); ef=ttk.Entry(f,width=16); ef.grid(row=0,column=1,padx=6)
        ttk.Label(f,text="Bitiş (YYYY-AA-GG):").grid(row=0,column=2,sticky="e"); et=ttk.Entry(f,width=16); et.grid(row=0,column=3,padx=6)
        tv=ttk.Treeview(win,columns=("tarih","tur","not","tutar"),show="headings",height=16)
        for c in ("tarih","tur","not","tutar"): tv.heading(c,text=c.upper())
        tv.column("tutar",anchor="e")
        tv.pack(fill="both",expand=True,padx=8,pady=8)
        lb=ttk.Label(win,font=("Segoe UI",16,"bold")); lb.pack(pady=8)
        def calistir():
            for i in tv.get_children(): tv.delete(i)
            ad=self.cmb.get(); sid,_=self.sup.get(ad,(None,0))
            if not sid: return
            q="SELECT date,type,note,amount_tl FROM supplier_ledger WHERE supplier_id=?"; prm=[sid]
            if ef.get().strip(): q+=" AND date>=?"; prm.append(ef.get().strip())
            if et.get().strip(): q+=" AND date<=?"; prm.append(et.get().strip()+"T23:59:59")
            q+=" ORDER BY date"
            c=baglan(); rows=c.execute(q,prm).fetchall(); c.close()
            borc=odeme=0.0
            for d,t,n,a in rows:
                s = a if t=="purchase" else -a if t=="payment" else 0
                tv.insert("", "end", values=(d,t,n, f"{s:.2f}"))
                if t=="purchase": borc+=a
                elif t=="payment": odeme+=a
            net=borc-odeme
            lb.config(text=("Toplam Borç: "+f"{net:.2f} TL") if net>0 else ("Alacak: "+f"{-net:.2f} TL" if net<0 else "Cari Kapalı"), 
                      foreground="red" if net>0 else ("green" if net<0 else "black"))
        ttk.Button(win,text="Filtrele",command=calistir).pack(pady=8)
