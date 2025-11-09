import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from database import kurulum, giris
from gui.login_screen import GirisEkrani
from gui.dashboard import Panel
from gui.sales_screen import SatisEkrani
from gui.purchase_screen import AlisEkrani
from gui.stock_screen import StokEkrani
from gui.suppliers_screen import ToptanciEkrani
from gui.cashier_screen import KasaEkrani
from gui.admin_screen import YoneticiEkrani

class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__(); kurulum(); self.title("Turco Tekel POS — R.M Bilişim")
        self.ayarlar=self.ayar_yukle(); self.style=ttk.Style(); self.style.theme_use(self.ayarlar.get("tema","clam"))
        self.option_add("*Font",("Segoe UI",20)); self.style.configure("TButton",font=("Segoe UI",22),padding=22); self.style.configure("Big.TButton",font=("Segoe UI",30,"bold"),padding=30)
        self.style.configure("Treeview",rowheight=52,font=("Segoe UI",20)); self.style.configure("Treeview.Heading",font=("Segoe UI",22,"bold"))
        self.after(10,self.olcek_uygula)
        if self.ayarlar.get("tam_ekran",True): self.attributes("-fullscreen",True)
        self.bind('<F11>', lambda e: self.attributes('-fullscreen', not self.attributes('-fullscreen')))
        self.bind('<Escape>', lambda e: self.attributes('-fullscreen', False))
        self.govde=ttk.Frame(self); self.govde.pack(fill="both",expand=True); self.kullanici=None; self.aktif=None; self.goster_giris()
    def olcek_uygula(self):
        h=self.winfo_screenheight(); base=int(self.ayarlar.get("ui_olcek_taban_yukseklik",1080)); scale=max(1.0,min(2.0,h/base)); self.tk.call('tk','scaling',scale)
    def ayar_yukle(self):
        p=os.path.join(os.path.dirname(__file__),"config","settings.json")
        return json.load(open(p,"r",encoding="utf-8")) if os.path.exists(p) else {"varsayilan_kdv":20,"fis_yazdir":True}
    def kullanici_ayarla(self,u): self.kullanici=u
    def _goster(self,frame):
        if self.aktif: self.aktif.destroy()
        self.aktif=frame; self.aktif.pack(fill="both",expand=True)
    def goster_giris(self): self._goster(GirisEkrani(self.govde,self))
    def goster_panel(self): self._goster(Panel(self.govde,self))
    def goster_satis(self): self._goster(SatisEkrani(self.govde,self))
    def goster_alis(self): self._goster(AlisEkrani(self.govde,self))
    def goster_stok(self): self._goster(StokEkrani(self.govde,self))
    def goster_toptanci(self): self._goster(ToptanciEkrani(self.govde,self))
    def goster_kasa(self): self._goster(KasaEkrani(self.govde,self))
    def goster_yonetici(self):
        if self.kullanici and self.kullanici.get("role")!="admin": messagebox.showwarning("Yetki","Yönetici paneli için yetki gerekli"); return
        self._goster(YoneticiEkrani(self.govde,self))
    def cikis(self): self.kullanici=None; self.goster_giris()
    def db_giris(self,u,p): return giris(u,p)

if __name__=="__main__": Uygulama().mainloop()
