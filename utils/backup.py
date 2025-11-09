import os, zipfile, datetime
from tkinter import filedialog, messagebox
def yedekle(db_path, settings_path):
    klasor=filedialog.askdirectory(title="Yedeği Kaydet")
    if not klasor: return
    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S"); zp=os.path.join(klasor,f"turco_pos_yedek_{ts}.zip")
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        if os.path.exists(db_path): z.write(db_path,"database.db")
        if os.path.exists(settings_path): z.write(settings_path,"config/settings.json")
    messagebox.showinfo("Yedek", f"Yedek alındı:\n{zp}")
