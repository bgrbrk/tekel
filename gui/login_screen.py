from tkinter import ttk, messagebox
class GirisEkrani(ttk.Frame):
    def __init__(self, master, app, **kw):
        super().__init__(master, **kw); self.app=app
        self.columnconfigure(0,weight=1)
        baslik=ttk.Frame(self); baslik.grid(row=0,column=0,sticky="ew")
        ttk.Label(baslik,text="Turco Tekel POS",font=("Segoe UI",36,"bold")).pack(pady=20)
        kart=ttk.Frame(self,padding=20); kart.grid(row=1,column=0,pady=20)
        ttk.Label(kart,text="Kullanıcı Adı").grid(row=0,column=0,sticky="e",padx=6,pady=6)
        self.eu=ttk.Entry(kart,width=28); self.eu.grid(row=0,column=1,padx=6,pady=6)
        ttk.Label(kart,text="Şifre").grid(row=1,column=0,sticky="e",padx=6,pady=6)
        self.ep=ttk.Entry(kart,show="*",width=28); self.ep.grid(row=1,column=1,padx=6,pady=6)
        ttk.Button(kart,text="Giriş",style="Big.TButton",command=self.giris).grid(row=2,column=0,columnspan=2,sticky="ew",pady=12)
        self.ep.bind("<Return>", lambda e:self.giris())
    def giris(self):
        u=self.app.db_giris(self.eu.get(), self.ep.get())
        if not u: messagebox.showerror("Hata","Geçersiz bilgiler"); return
        self.app.kullanici_ayarla(u); self.app.goster_panel()
