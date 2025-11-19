# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import datetime
import requests

DB_PATH = "data.db"

# ---------------------- #
#  VERİTABANI BAĞLANTI  #
# ---------------------- #
def baglan():
    return sqlite3.connect(DB_PATH)

# ---------------------- #
#     SATIŞ KAYDETME    #
# ---------------------- #
def satis_kaydet(user_id, items, total_tl, payment_type):
    con = baglan()
    cur = con.cursor()
    now = datetime.datetime.now().isoformat(timespec="seconds")

    # Satış kaydı
    cur.execute("""
        INSERT INTO sales(date,total_tl,payment_type,cashier_id,items_json)
        VALUES(?,?,?,?,?)
    """, (now, total_tl, payment_type, user_id, json.dumps(items)))

    # Stok güncelleme
    if payment_type in ("cash", "card"):
        for it in items:
            cur.execute("UPDATE products SET stock=COALESCE(stock,0)-? WHERE id=?", (it["qty"], it["product_id"]))
    elif payment_type == "return":
        for it in items:
            cur.execute("UPDATE products SET stock=COALESCE(stock,0)+? WHERE id=?", (it["qty"], it["product_id"]))

    # Kasa hareketleri
    if payment_type == "cash":
        kasa_hareket("income", total_tl, "Nakit Satış")
    elif payment_type == "card":
        kasa_hareket("income", total_tl, "Kart Satış")
    elif payment_type == "return":
        kasa_hareket("return", abs(total_tl), "İade")

    con.commit()
    con.close()

# ---------------------- #
#    KASA HAREKETLERİ   #
# ---------------------- #
def kasa_hareket(tur, miktar, aciklama):
    con = baglan()
    cur = con.cursor()
    now = datetime.datetime.now().isoformat(timespec="seconds")
    cur.execute("""
        INSERT INTO cash_register(date,type,amount,description)
        VALUES(?,?,?,?)
    """, (now, tur, miktar, aciklama))
    con.commit()
    con.close()

# ---------------------- #
#      KASA RAPORU      #
# ---------------------- #
def kasa_raporu():
    con = baglan()
    cur = con.cursor()
    cur.execute("SELECT date,type,amount,description FROM cash_register ORDER BY date DESC")
    rows = cur.fetchall()

    gelir = sum(r[2] for r in rows if r[1] == "income")
    gider = sum(r[2] for r in rows if r[1] == "expense")
    iade = sum(r[2] for r in rows if r[1] == "return")
    net = gelir - gider - iade

    con.close()
    return rows, gelir, gider, iade, net

# ---------------------- #
#     Z RAPORU YAZ      #
# ---------------------- #
def z_raporu_yaz():
    rows, gelir, gider, iade, net = kasa_raporu()
    path = f"zraporu_{datetime.date.today()}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("TARİH | TÜR | TUTAR | AÇIKLAMA\n")
        f.write("-" * 70 + "\n")
        for r in rows:
            f.write(f"{r[0]} | {r[1]} | {r[2]:.2f} | {r[3]}\n")
        f.write("\n")
        f.write(f"Toplam Gelir: {gelir:.2f} TL\n")
        f.write(f"Toplam Gider: {gider:.2f} TL\n")
        f.write(f"Toplam İade: {iade:.2f} TL\n")
        f.write(f"Kasa Net: {net:.2f} TL\n")
    return os.path.abspath(path)

# ---------------------- #
#     KASA DETAYLARI    #
# ---------------------- #
def kasa_rapor_detay():
    con = baglan()
    cur = con.cursor()
    cur.execute("SELECT type, SUM(amount) FROM cash_register GROUP BY type")
    data = cur.fetchall()
    con.close()
    return {r[0]: r[1] for r in data}

# ---------------------- #
#     GİRİŞ KONTROL     #
# ---------------------- #
def giris(kullanici_adi, sifre):
    con = baglan()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'kasiyer'
        )
    """)
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", ('admin', '1234', 'admin'))
        con.commit()
    cur.execute("SELECT id, username, role FROM users WHERE username=? AND password=?", (kullanici_adi, sifre))
    user = cur.fetchone()
    con.close()
    if user:
        return {"id": user[0], "username": user[1], "role": user[2]}
    return None

# ---------------------- #
#     ÜRÜN BARKODU      #
# ---------------------- #
def urun_barkod(barkod):
    con = baglan()
    cur = con.cursor()
    try:
        cur.execute("SELECT id, name, sale_price, stock FROM products WHERE barcode=?", (barkod,))
    except:
        cur.execute("SELECT id, name, price, stock FROM products WHERE barcode=?", (barkod,))
    result = cur.fetchone()
    con.close()
    if result:
        return {"product_id": result[0], "name": result[1], "price": result[2], "stock": result[3]}
    return None

# ---------------------- #
#       SON KURLAR       #
# ---------------------- #
def son_kurlar():
    con = baglan()
    cur = con.cursor()
    cur.execute("SELECT code, rate FROM currency_rates ORDER BY updated_at DESC LIMIT 3")
    data = cur.fetchall()
    con.close()
    if not data:
        return [("💵", 0), ("💶", 0), ("💷", 0)]
    return data

# ---------------------- #
#   KURLARI GÜNCELLE    #
# ---------------------- #
def kurlari_guncelle():
    try:
        con = baglan()
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS currency_rates(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                rate REAL,
                updated_at TEXT
            )
        """)

        # 💱 Döviz verisini çek
        res = requests.get("https://open.er-api.com/v6/latest/TRY", timeout=10).json()
        if res.get("result") == "success":
            rates = res["rates"]
            now = datetime.datetime.now().isoformat(timespec='seconds')

            # 🪙 Emoji / sembollü döviz listesi
            data = [
                ("💵 USD", round(rates["USD"], 4), now),
                ("💶 EUR", round(rates["EUR"], 4), now),
                ("💷 GBP", round(rates["GBP"], 4), now)
            ]

            cur.executemany(
                "INSERT INTO currency_rates (code, rate, updated_at) VALUES (?, ?, ?)",
                data
            )
            con.commit()

            # Terminal çıktısı
            print("💱 Kurlar başarıyla güncellendi:")
            print(f"    USD: 1 USD = {1 / rates['USD']:.2f} TL")
            print(f"    EUR: 1 EUR = {1 / rates['EUR']:.2f} TL")
            print(f"    GBP: 1 GBP = {1 / rates['GBP']:.2f} TL")

        else:
            print("⚠️ Kur verisi alınamadı:", res.get("error-type"))

    except Exception as e:
        print("❌ Kur güncelleme hatası:", e)
    finally:
        con.close()

# ---------------------- #
#      TEDARİKÇİLER     #
# ---------------------- #
def tedarikci_listesi():
    con = baglan()
    cur = con.cursor()
    cur.execute("SELECT id, name, balance FROM suppliers ORDER BY name ASC")
    rows = cur.fetchall()
    con.close()
    return rows

# ---------------------- #
#  TABLO KONTROL OLUŞTUR #
# ---------------------- #
def tablo_kontrol_ve_olustur():
    con = baglan()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            balance REAL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            rate REAL,
            updated_at TEXT
        )
    """)
    con.commit()
    con.close()
    print("✅ Eksik tablolar kontrol edildi ve varsa oluşturuldu.")

# ---------------------- #
#     STOK LİSTESİ      #
# ---------------------- #
def tree_rows_for_stock():
    con = baglan()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT p.barcode, p.name, COALESCE(p.stock,0), COALESCE(p.price,0), p.id, s.name
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY p.name ASC
        """)
    except:
        cur.execute("""
            SELECT barcode, name, COALESCE(stock,0), COALESCE(price,0), id, ''
            FROM products ORDER BY name ASC
        """)
    rows = cur.fetchall()
    con.close()
    return rows

# ---------------------- #
#        KURULUM        #
# ---------------------- #
def kurulum():
    tablo_kontrol_ve_olustur()
    kurlari_guncelle()
    print("🚀 Veritabanı kurulumu tamamlandı.")

def urun_kaydet_veya_guncelle(barcode, name, price, kdv, category, stock=0, supplier_id=None):
    """
    Eğer barkod varsa ürün güncellenir, yoksa yeni ürün eklenir.
    Yeni ürün eklenirken stok miktarı kaydedilir.
    """
    con = baglan()
    cur = con.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                price REAL DEFAULT 0,
                kdv REAL DEFAULT 0,
                category TEXT,
                supplier_id INTEGER,
                stock REAL DEFAULT 0,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        """)

        cur.execute("SELECT id FROM products WHERE barcode=?", (barcode,))
        row = cur.fetchone()

        if row:
            pid = row[0]
            # Güncelleme (stok sabit kalır)
            cur.execute("""
                UPDATE products
                SET name=?, price=?, kdv=?, category=?, supplier_id=?
                WHERE id=?
            """, (name, price, kdv, category, supplier_id, pid))
        else:
            # Yeni ürün ekleme (stok miktarı dahil)
            cur.execute("""
                INSERT INTO products (barcode, name, price, kdv, category, supplier_id, stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (barcode, name, price, kdv, category, supplier_id, stock))
            pid = cur.lastrowid

        con.commit()
        return pid

    except Exception as e:
        print("❌ Ürün kaydet/güncelle hatası:", e)
        return None
    finally:
        con.close()

# ---------------------- #
#      ÜRÜN GETİR       #
# ---------------------- #
def urun_getir(barcode):
    """
    Barkoda göre ürün bilgilerini döndürür.
    Eğer ürün bulunmazsa None döner.
    """
    con = baglan()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT id, barcode, name, price, kdv, category, supplier_id, stock
            FROM products
            WHERE barcode=?
        """, (barcode,))
        row = cur.fetchone()
        con.close()
        if row:
            return {
                "id": row[0],
                "barcode": row[1],
                "name": row[2],
                "price": row[3],
                "kdv": row[4],
                "category": row[5],
                "supplier_id": row[6],
                "stock": row[7]
            }
        return None
    except Exception as e:
        print("❌ Ürün getir hatası:", e)
        con.close()
        return None
# ---------------------- #
#     STOK DEĞİŞTİR     #
# ---------------------- #
def stok_degistir(product_id, miktar, tur="adjust", ref="", note=""):
    """
    Sayım ekranı veya manuel stok düzeltmelerinde kullanılır.
    Ürün stok miktarını arttırır veya azaltır.
    """
    try:
        con = baglan()
        cur = con.cursor()
        # Ürün tablosunu güvenceye al
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE,
                name TEXT NOT NULL,
                price REAL DEFAULT 0,
                kdv REAL DEFAULT 0,
                category TEXT,
                supplier_id INTEGER,
                stock REAL DEFAULT 0
            )
        """)

        # Mevcut stok bilgisini al
        cur.execute("SELECT COALESCE(stock,0) FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        if not row:
            print(f"⚠️ Ürün bulunamadı (id={product_id})")
            return

        mevcut = float(row[0])
        yeni_stok = mevcut + float(miktar)
        if yeni_stok < 0:
            yeni_stok = 0  # stok negatif olmasın

        cur.execute("UPDATE products SET stock=? WHERE id=?", (yeni_stok, product_id))
        con.commit()

        print(f"📦 Stok güncellendi | ID={product_id} | Eski={mevcut} | Yeni={yeni_stok} | Ref={ref} | Not={note}")
    except Exception as e:
        print("❌ stok_degistir hatası:", e)
    finally:
        con.close()
