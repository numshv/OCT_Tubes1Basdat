import mysql.connector
from mysql.connector import Error
from faker import Faker
from datetime import datetime, timedelta
import random

# Inisialisasi Faker untuk bahasa Indonesia
fake = Faker('id_ID')

def create_connection():
    """Membuat koneksi ke database MariaDB"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      
            password='',      
            database='bustbuy' 
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None


def generate_sku(id_produk, varian_num):
    """Generate SKU untuk varian produk"""
    return f"SKU-{id_produk:04d}-{varian_num:02d}"

def seed_users(connection, count=50):
    """Mengisi data User, Buyer, dan Seller"""
    cursor = connection.cursor()
    
    users = []
    buyers = []
    sellers = []
    
    for i in range(count):
        email = f"{nama_panjang}{random.randint(1,999)}@bustbuy.id"
        password_hash = fake.password()
        nama_panjang = fake.unique.name()
        tanggal_lahir = fake.date_of_birth(minimum_age=18, maximum_age=60)
        foto_profil = f"profile_{i+1}.jpg"
        tipe = "Seller" if i % 5 == 0 else "Buyer"  # 20% menjadi Seller
        
        users.append((email, password_hash, nama_panjang, tanggal_lahir, foto_profil, tipe))
        
        if tipe == "Buyer":
            buyers.append((email,))
        else:
            ktp = f"ktp_{i+1}.jpg"
            foto_diri = f"selfie_{i+1}.jpg"
            is_verified = random.choice([True, False])  # 50% verified
            sellers.append((email, ktp, foto_diri, is_verified))
    
    try:
        # Insert users
        cursor.executemany(
            """INSERT INTO User 
            (email, password_hash, nama_panjang, tanggal_lahir, foto_profil, tipe) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            users
        )
        
        # Insert buyers
        if buyers:
            cursor.executemany(
                "INSERT INTO Buyer (email) VALUES (%s)",
                buyers
            )
        
        # Insert sellers
        if sellers:
            cursor.executemany(
                """INSERT INTO Seller 
                (email, ktp, foto_diri, is_verified) 
                VALUES (%s, %s, %s, %s)""",
                sellers
            )
        
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(users)} users, {len(buyers)} buyers, dan {len(sellers)} sellers")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding users: {e}")
    finally:
        cursor.close()

def seed_pertemanan(connection, max_friends=8):
    """Mengisi data pertemanan antara user"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT email FROM User")
        emails = [row[0] for row in cursor.fetchall()]
        
        pertemanan = set()  # Gunakan set untuk menghindari duplikat
        
        for email in emails:
            num_friends = random.randint(1, max_friends)
            friends = random.sample(emails, num_friends)
            
            for friend in friends:
                if email != friend:
                    # Pastikan tidak ada duplikat dengan urutan terbalik
                    if (friend, email) not in pertemanan:
                        pertemanan.add((email, friend))
        
        if pertemanan:
            cursor.executemany(
                "INSERT INTO Pertemanan (email, email_friend) VALUES (%s, %s)",
                list(pertemanan)
            )
            connection.commit()
            print(f"✅ Berhasil menambahkan {len(pertemanan)} relasi pertemanan")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding pertemanan: {e}")
    finally:
        cursor.close()

def seed_inst_telp(connection, max_numbers=2):
    """Mengisi data nomor telepon user"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT email FROM User")
        emails = [row[0] for row in cursor.fetchall()]
        
        inst_telp = []
        
        for email in emails:
            num_numbers = random.randint(1, max_numbers)
            for _ in range(num_numbers):
                nomor_telpon = fake.phone_number()
                inst_telp.append((email, nomor_telpon))
        
        if inst_telp:
            cursor.executemany(
                "INSERT INTO InstTelp (email, nomor_telpon) VALUES (%s, %s)",
                inst_telp
            )
            connection.commit()
            print(f"✅ Berhasil menambahkan {len(inst_telp)} nomor telepon")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding inst telp: {e}")
    finally:
        cursor.close()

def seed_alamat(connection, max_addresses=3):
    """Mengisi data alamat untuk buyer"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT email FROM Buyer")
        buyer_emails = [row[0] for row in cursor.fetchall()]
        
        alamat = []
        provinsi_kota = {
            'Jakarta': ['Jakarta Pusat', 'Jakarta Selatan', 'Jakarta Barat', 'Jakarta Timur', 'Jakarta Utara'],
            'Jawa Barat': ['Bandung', 'Bogor', 'Bekasi', 'Depok', 'Cimahi'],
            'Jawa Tengah': ['Semarang', 'Surakarta', 'Yogyakarta', 'Magelang', 'Pekalongan'],
            'Jawa Timur': ['Surabaya', 'Malang', 'Sidoarjo', 'Madiun', 'Kediri'],
            'Banten': ['Tangerang', 'Serang', 'Cilegon', 'South Tangerang']
        }
        
        for email in buyer_emails:
            num_addresses = random.randint(1, max_addresses)
            for i in range(num_addresses):
                provinsi = random.choice(list(provinsi_kota.keys()))
                kota = random.choice(provinsi_kota[provinsi])
                jalan = fake.street_address()
                is_utama = (i == 0)  # Alamat pertama sebagai utama
                
                alamat.append((email, provinsi, kota, jalan, is_utama))
        
        if alamat:
            cursor.executemany(
                """INSERT INTO Alamat 
                (email, provinsi, kota, jalan, is_utama) 
                VALUES (%s, %s, %s, %s, %s)""",
                alamat
            )
            connection.commit()
            print(f"✅ Berhasil menambahkan {len(alamat)} alamat")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding alamat: {e}")
    finally:
        cursor.close()

def seed_produk_dan_varian(connection, count=100):
    """Mengisi data produk dan varian produk"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT email FROM Seller WHERE is_verified = TRUE")
        seller_emails = [row[0] for row in cursor.fetchall()]
        
        if not seller_emails:
            print("⚠ Tidak ada verified seller. Lewati seeding produk.")
            return
        
        produk = []
        varian_produk = []
        inst_tag = []
        inst_gambar = []
        
        kategori_produk = {
            'Elektronik': ['Smartphone', 'Laptop', 'Kamera', 'Headphone', 'Smartwatch'],
            'Fashion': ['Kaos', 'Celana', 'Jaket', 'Sepatu', 'Tas'],
            'Rumah Tangga': ['Furniture', 'Dekorasi', 'Perlengkapan Dapur', 'Alat Kebersihan'],
            'Hobi': ['Alat Musik', 'Buku', 'Alat Lukis', 'Peralatan Olahraga']
        }
        
        for i in range(count):
            email = random.choice(seller_emails)
            kategori = random.choice(list(kategori_produk.keys()))
            subkategori = random.choice(kategori_produk[kategori])
            nama = f"{subkategori} {fake.word().capitalize()}"
            deskripsi = fake.sentence(nb_words=10)
            
            produk.append((nama, deskripsi, email))
        
        # Insert produk dan dapatkan ID
        for p in produk:
            cursor.execute(
                """INSERT INTO Produk 
                (nama, deskripsi, email) 
                VALUES (%s, %s, %s)""",
                p
            )
            product_id = cursor.lastrowid
            
            # Buat varian produk (1-3 varian per produk)
            num_variants = random.randint(1, 3)
            for j in range(num_variants):
                sku = generate_sku(product_id, j+1)
                nama_varian = f"Varian {j+1} - {fake.color_name()}"
                harga = random.randint(10000, 5000000)
                stok = random.randint(0, 100)
                
                varian_produk.append((sku, product_id, nama_varian, harga, stok))
            
            # Tambahkan 1-3 tag
            tags = random.sample(list(kategori_produk.keys()), random.randint(1, 3))
            for tag in tags:
                inst_tag.append((product_id, tag))
            
            # Tambahkan 1-3 gambar
            num_images = random.randint(1, 3)
            for k in range(num_images):
                gambar = f"produk_{product_id}_img_{k+1}.jpg"
                inst_gambar.append((product_id, gambar))
        
        # Insert varian produk
        if varian_produk:
            cursor.executemany(
                """INSERT INTO VarianProduk 
                (sku, id_produk, nama_varian, harga, stok) 
                VALUES (%s, %s, %s, %s, %s)""",
                varian_produk
            )
        
        # Insert tag
        if inst_tag:
            cursor.executemany(
                "INSERT INTO InstTag (id_produk, tag) VALUES (%s, %s)",
                inst_tag
            )
        
        # Insert gambar
        if inst_gambar:
            cursor.executemany(
                "INSERT INTO InstGambar (id_produk, gambar) VALUES (%s, %s)",
                inst_gambar
            )
        
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(produk)} produk, {len(varian_produk)} varian, {len(inst_tag)} tag, dan {len(inst_gambar)} gambar")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding produk: {e}")
    finally:
        cursor.close()

def seed_keranjang_dan_wishlist(connection):
    """Mengisi data keranjang dan wishlist"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT email FROM Buyer")
        buyer_emails = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT sku, id_produk FROM VarianProduk")
        varian_produk = [(row[0], row[1]) for row in cursor.fetchall()]
        
        keranjang = []
        wishlist = []
        
        for email in buyer_emails:
            # Tambahkan 0-5 item ke keranjang
            num_cart_items = random.randint(0, 5)
            if num_cart_items > 0 and varian_produk:
                items = random.sample(varian_produk, min(num_cart_items, len(varian_produk)))
                for sku, id_produk in items:
                    kuantitas = random.randint(1, 5)
                    keranjang.append((email, sku, id_produk, kuantitas))
            
            # Tambahkan 0-5 item ke wishlist (tidak duplikat dengan keranjang)
            num_wishlist_items = random.randint(0, 5)
            if num_wishlist_items > 0 and varian_produk:
                available_items = [vp for vp in varian_produk 
                                 if not any(item for item in keranjang 
                                           if item[0] == email and item[2] == vp[1])]
                if available_items:
                    items = random.sample(available_items, min(num_wishlist_items, len(available_items)))
                    for sku, id_produk in items:
                        wishlist.append((email, id_produk))
        
        # Insert keranjang
        if keranjang:
            cursor.executemany(
                """INSERT INTO Keranjang 
                (email, sku, id_produk, kuantitas) 
                VALUES (%s, %s, %s, %s)""",
                keranjang
            )
        
        # Insert wishlist
        if wishlist:
            cursor.executemany(
                "INSERT INTO Wishlist (email, id_produk) VALUES (%s, %s)",
                wishlist
            )
        
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(keranjang)} item keranjang dan {len(wishlist)} item wishlist")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding keranjang dan wishlist: {e}")
    finally:
        cursor.close()

def seed_orders(connection, count=200):
    """Mengisi data orders"""
    cursor = connection.cursor()
    
    try:
        # Ambil data buyer dan alamat utama mereka
        cursor.execute("""
            SELECT b.email, a.id_alamat 
            FROM Buyer b
            JOIN Alamat a ON b.email = a.email
            WHERE a.is_utama = TRUE
        """)
        buyer_addresses = [(row[0], row[1]) for row in cursor.fetchall()]
        
        cursor.execute("SELECT sku, id_produk FROM VarianProduk")
        varian_produk = [(row[0], row[1]) for row in cursor.fetchall()]
        
        if not buyer_addresses or not varian_produk:
            print("⚠ Tidak cukup data untuk seeding orders. Diperlukan buyer dengan alamat dan varian produk.")
            return
        
        orders = []
        inst_produk = []
        
        status_options = [
            'pesanan belum dibayar', 
            'pesanan sedang disiapkan', 
            'pesanan sedang dikirim', 
            'pesanan sampai', 
            'pesanan dibatalkan'
        ]
        metode_pembayaran = ['Transfer Bank', 'Kartu Kredit', 'OVO', 'Gopay', 'Dana', 'COD']
        metode_pengiriman = ['JNE', 'J&T', 'SiCepat', 'Ninja Express', 'AnterAja']
        
        for i in range(count):
            email, id_alamat = random.choice(buyer_addresses)
            status_order = random.choices(
                status_options,
                weights=[10, 20, 20, 40, 10]  # Lebih banyak pesanan yang sudah sampai
            )[0]
            metode_pembayaran = random.choice(metode_pembayaran)
            metode_pengiriman = random.choice(metode_pengiriman)
            catatan = fake.sentence(nb_words=5) if random.random() > 0.7 else ""
            
            # Waktu pemesanan dalam 90 hari terakhir
            waktu_pemesanan = fake.date_time_between(
                start_date='-90d', 
                end_date='now'
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            kuantitas = random.randint(1, 5)
            sku, id_produk = random.choice(varian_produk)
            
            orders.append((
                id_alamat, email, status_order, metode_pembayaran, 
                metode_pengiriman, catatan, waktu_pemesanan, kuantitas, sku
            ))
        
        # Insert orders dan dapatkan ID
        for order in orders:
            cursor.execute("""
                INSERT INTO Orders (
                    id_alamat, email, status_order, metode_pembayaran, 
                    metode_pengiriman, catatan, waktu_pemesanan, kuantitas, sku
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, order)
            order_id = cursor.lastrowid
            
            # Tambahkan ke inst_produk
            inst_produk.append((order_id, id_produk))
        
        # Insert inst_produk
        if inst_produk:
            cursor.executemany(
                "INSERT INTO InstProduk (id_order, id_produk) VALUES (%s, %s)",
                inst_produk
            )
        
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(orders)} orders dan {len(inst_produk)} product instances")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding orders: {e}")
    finally:
        cursor.close()

def main():
    """Fungsi utama untuk menjalankan seeder"""
    connection = create_connection()
    if connection is None:
        return
    
    try:
        print("🚀 Memulai proses seeding database...")
        
        # Urutan seeding penting karena foreign key constraints
        seed_users(connection)
        seed_pertemanan(connection)
        seed_inst_telp(connection)
        seed_alamat(connection)
        seed_produk_dan_varian(connection)
        seed_keranjang_dan_wishlist(connection)
        seed_orders(connection)
        
        print("\n🎉 Database seeding berhasil diselesaikan!")
    except Error as e:
        print(f"\n🔥 Error selama seeding: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Koneksi database ditutup")

if __name__ == "__main__":
    main()