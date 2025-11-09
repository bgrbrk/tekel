# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import os, json, sys

# Multi-platform import safety for "python main.py" (adds this folder to sys.path)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
from gui.login_screen import LoginScreen
from gui.dashboard import Dashboard
from gui.sales_screen import SalesScreen
from gui.purchase_screen import PurchaseScreen
from gui.stock_screen import StockScreen
from gui.suppliers_screen import SuppliersScreen
from gui.cashier_screen import CashierScreen
from gui.admin_screen import AdminScreen
from gui.count_screen import CountScreen
from utils.helpers import setup_style

APP_TITLE = "Turco Tekel POS"

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)

        # Başlangıçta tam ekran (F11 aç/kapat, ESC çık)
        self.attributes("-fullscreen", True)
        self.bind("<F11>", lambda e: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.settings_path = os.path.join("config","settings.json")
        self.settings = self._load_settings()
        setup_style(self)

        database.kurulum()
        try:
            from utils import currency_updater
            currency_updater.guncelle()
        except Exception:
            pass

        self.user = None
        self.container = ttk.Frame(self); self.container.pack(fill="both", expand=True)
        self.show_login()

    def _load_settings(self):
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"yazdir_fis": False, "varsayilan_kdv": 20}

    def _exit_app(self):
        self.destroy()
        return None

    def show_login(self):
        for w in self.container.winfo_children(): w.destroy()
        LoginScreen(self.container, self._login_success).pack(fill="both", expand=True)

    def _login_success(self, user):
        self.user = user
        self.show_dashboard()

    def show_dashboard(self):
        for w in self.container.winfo_children(): w.destroy()
        Dashboard(self.container, self.show_screen, self.user).pack(fill="both", expand=True)

    def show_screen(self, name):
        if name == "exit":
            self._exit_app()
            return
        for w in self.container.winfo_children(): w.destroy()
        screens = {
            "sales": lambda: SalesScreen(self.container, self.show_dashboard, self.user, self.settings),
            "purchase": lambda: PurchaseScreen(self.container, self.show_dashboard),
            "stock": lambda: StockScreen(self.container, self.show_dashboard),
            "suppliers": lambda: SuppliersScreen(self.container, self.show_dashboard),
            "cashier": lambda: CashierScreen(self.container, self.show_dashboard),
            "admin": lambda: AdminScreen(self.container, self.show_dashboard, self.user, self.settings_path),
            "count": lambda: CountScreen(self.container, self.show_dashboard),
        }
        screens[name]().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
