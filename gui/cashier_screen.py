from tkinter import ttk, messagebox
import tkinter as tk, datetime, os
from database import baglan
class KasaEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw); self.app=app; self.insa_et()
    def insa_et(self):
        ust=ttk.Frame(self); ust.pack(fill="x")
        ttk.Button(ust,text="⮌ Ana Menü",style="Big.TButton",command=self.app.goster_panel).pack(side="left",padx=8,pady=8)
        ttk.Label(ust,text="Kasa",font=("Segoe UI",28,"bold")).pack(side="left",padx=12,pady=8)
        bar=ttk.Frame(self); bar.pack(fill="x",pady=8)
        ttk.Button(bar,text="Gelir Ekle",command=lambda:self.hareket("income")).pack(side="left",padx=6)
        ttk.Button(bar,text="Gider Ekle",command=lambda:self.hareket("expense")).pack(side="left",padx=6)
        ttk.Button(bar,text="Kasa Raporu",command=self.rapor).pack(side="left",padx=6)
        ttk.Button(bar,text="Gün Kapat (Z Raporu)",style="Big.TButton",command=self.z).pack(side="left",padx=6)
        self.lbl=ttk.Label(self,font=("Segoe UI",18)); self.lbl.pack(pady=10); self.ozet()
    def ozet(self):
        c=baglan(); bugun=datetime.date.today().isoformat()
        satis = c.execute("SELECT COALESCE(SUM(total_tl),0) FROM sales WHERE date LIKE ?",(bugun+"%",)).fetchone()[0] or 0.0
        gelir = c.execute("SELECT COALESCE(SUM(amount_tl),0) FROM cash_movements WHERE type='income' AND date LIKE ?",(bugun+"%",)).fetchone()[0] or 0.0
        gider = c.execute("SELECT COALESCE(SUM(amount_tl),0) FROM cash_movements WHERE type='expense' AND date LIKE ?",(bugun+"%",)).fetchone()[0] or 0.0
        c.close()
        self.lbl.config(text=f"Bugün Satış: {satis:.2f} TL | Gelir: {gelir:.2f} TL | Gider: {gider:.2f} TL")
    def hareket(self,tur):
        win=tk.Toplevel(self); win.title("Gelir Ekle" if tur=="income" else "Gider Ekle")
        ttk.Label(win,text="Tutar (TL):").grid(row=0,column=0,sticky="e",padx=6,pady=6); et=ttk.Entry(win,width=18); et.grid(row=0,column=1,padx=6,pady=6)
        ttk.Label(win,text="Not (zorunlu):").grid(row=1,column=0,sticky="e",padx=6,pady=6); en=ttk.Entry(win,width=32); en.grid(row=1,column=1,padx=6,pady=6)
        def kaydet():
            try: tutar=float(et.get().replace(",","."))
            except: messagebox.showerror("Hata","Geçerli tutar girin."); return
            if not en.get().strip(): messagebox.showwarning("Zorunlu","Not girmek zorunludur."); return
            c=baglan(); now=__import__('datetime').datetime.now().isoformat(timespec='seconds')
            c.execute("INSERT INTO cash_movements(date,type,amount_tl,note) VALUES(?,?,?,?)",(now,tur,tutar,en.get().strip())); c.commit(); c.close()
            messagebox.showinfo("Kasa","Kayıt edildi."); win.destroy(); self.ozet()
        ttk.Button(win,text="Kaydet",command=kaydet).grid(row=2,column=0,columnspan=2,sticky="ew",pady=8)
    def rapor(self):
        win=tk.Toplevel(self); win.title("Kasa Raporu")
        f=ttk.Frame(win); f.pack(fill="x",padx=8,pady=8)
        ttk.Label(f,text="Başlangıç (YYYY-AA-GG):").grid(row=0,column=0,sticky="e"); ef=ttk.Entry(f,width=16); ef.grid(row=0,column=1,padx=6)
        ttk.Label(f,text="Bitiş (YYYY-AA-GG):").grid(row=0,column=2,sticky="e"); et=ttk.Entry(f,width=16); et.grid(row=0,column=3,padx=6)
        tv=ttk.Treeview(win,columns=("tarih","tur","tutar","not"),show="headings",height=16)
        for c in ("tarih","tur","tutar","not"): tv.heading(c,text=c.upper())
        tv.column("tutar",anchor="e")
        tv.pack(fill="both",expand=True,padx=8,pady=8)
        lb=ttk.Label(win,font=("Segoe UI",16,"bold")); lb.pack(pady=8)
        def calistir():
            for i in tv.get_children(): tv.delete(i)
            q="SELECT date,type,amount_tl,note FROM cash_movements WHERE 1=1"; prm=[]
            if ef.get().strip(): q+=" AND date>=?"; prm.append(ef.get().strip())
            if et.get().strip(): q+=" AND date<=?"; prm.append(et.get().strip()+"T23:59:59")
            q+=" ORDER BY date"
            c=baglan(); rows=c.execute(q,prm).fetchall(); c.close()
            g=gi=0.0
            for d,t,a,n in rows:
                tv.insert("", "end", values=(d, "Gelir" if t=="income" else "Gider", f"{a if t=='income' else -a:.2f}", n))
                if t=="income": g+=a
                else: gi+=a
            lb.config(text=f"Toplam Gelir: {g:.2f} TL | Toplam Gider: {gi:.2f} TL | Net: {g-gi:.2f} TL")
        ttk.Button(win,text="Filtrele",command=calistir).pack(pady=8)
    def z(self):
        import datetime, os
        bugun=datetime.date.today().isoformat()
        c=baglan(); st=c.execute("SELECT COALESCE(SUM(total_tl),0) FROM sales WHERE date LIKE ?",(bugun+"%",)).fetchone()[0] or 0.0; c.close()
        yol=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",f"z_raporu_{bugun}.txt"))
        with open(yol,"w",encoding="utf-8") as f: f.write(f"Z RAPORU - {bugun}\nToplam Satış: {st:.2f} TL\n")
        messagebox.showinfo("Z Raporu",f"Oluşturuldu:\n{yol}"); self.ozet()
