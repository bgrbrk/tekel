# -*- coding: utf-8 -*-
import os, zipfile
from tkinter import filedialog, messagebox

def yedek_al(db_path: str, settings_path: str):
    target_dir = filedialog.askdirectory(title="Yedek klasörünü seçin")
    if not target_dir: return
    zip_path = os.path.join(target_dir, "TurcoTekelPOS_YEDEK.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        if os.path.exists(db_path):
            z.write(db_path, arcname=os.path.basename(db_path))
        if os.path.exists(settings_path):
            z.write(settings_path, arcname=os.path.join("config", os.path.basename(settings_path)))
    messagebox.showinfo("Yedek", f"Yedek oluşturuldu:\n{zip_path}")
