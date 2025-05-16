import mysql.connector
from mysql.connector import Error
from faker import Faker
from datetime import datetime, timedelta
import random

# TODO: benerin penamaan sku
# TODO: id user auto increment

# Inisialisasi Faker untuk bahasa Indonesia
fake = Faker('id_ID')

def create_connection():
    """Membuat koneksi ke database MariaDB"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      
            password='n0um1sy1fa',      
            database='bustbuy4' 
        )
        return connection
    except Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None


def generate_sku(id_produk, varian_num):
    """Generate SKU untuk varian produk"""
    return f"SKU-{id_produk:04d}-{varian_num:02d}"

def seed_users(connection):
    """Mengisi data User sebanyak 100 user: 50 Seller dan 50 Buyer"""
    cursor = connection.cursor()
    
    users = []
    total_seller = 50
    total_buyer = 50
    
    # Buat 50 Seller terlebih dahulu
    for i in range(total_seller):
        nama_panjang = fake.unique.name()
        email = f"{nama_panjang.split()[0].lower()}{random.randint(1,999)}@bustbuy.id"
        password_hash = fake.password()
        tanggal_lahir = fake.date_of_birth(minimum_age=18, maximum_age=60)
        foto_profil = f"profile_seller_{i+1}.jpg"
        tipe = "Seller"
        
        users.append((email, password_hash, nama_panjang, tanggal_lahir, foto_profil, tipe))
    
    # Buat 50 Buyer
    for i in range(total_buyer):
        nama_panjang = fake.unique.name()
        email = f"{nama_panjang.split()[0].lower()}{random.randint(1,999)}@bustbuy.id"
        password_hash = fake.password()
        tanggal_lahir = fake.date_of_birth(minimum_age=18, maximum_age=60)
        foto_profil = f"profile_buyer_{i+1}.jpg"
        tipe = "Buyer"
        
        users.append((email, password_hash, nama_panjang, tanggal_lahir, foto_profil, tipe))
    
    try:
        cursor.executemany(
            """INSERT INTO User 
            (email, password_hash, nama_panjang, tanggal_lahir, foto_profil, tipe) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            users
        )
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(users)} users: {total_seller} Sellers dan {total_buyer} Buyers")
        return True
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding users: {e}")
        return False
    finally:
        cursor.close()


def seed_buyers_and_sellers(connection):
    """Mengisi data Buyer dan Seller berdasarkan User yang ada"""
    cursor = connection.cursor()
    
    try:
        # Ambil semua user dan tipe mereka
        cursor.execute("SELECT id_user, tipe FROM User")
        user_types = {row[0]: row[1] for row in cursor.fetchall()}
        
        buyers = []
        sellers = []
        
        for id_user, tipe in user_types.items():
            if tipe == "Buyer":
                buyers.append((id_user,))
            else:  # Seller
                ktp = f"ktp_{id_user}.jpg"
                foto_diri = f"selfie_{id_user}.jpg"
                is_verified = random.choice([True, False])  # 50% verified
                sellers.append((id_user, ktp, foto_diri, is_verified))
        
        # Insert buyers
        if buyers:
            cursor.executemany(
                "INSERT INTO Buyer (id_user) VALUES (%s)",
                buyers
            )
        
        # Insert sellers
        if sellers:
            cursor.executemany(
                """INSERT INTO Seller 
                (id_user, ktp, foto_diri, is_verified) 
                VALUES (%s, %s, %s, %s)""",
                sellers
            )
        
        connection.commit()
        print(f"✅ Berhasil menambahkan {len(buyers)} buyers dan {len(sellers)} sellers")
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding buyers dan sellers: {e}")
    finally:
        cursor.close()

def seed_pertemanan(connection, max_friends=8):
    """Mengisi data pertemanan antara user"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT id_user FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        pertemanan = set()  # Gunakan set untuk menghindari duplikat
        
        for user_id in user_ids:
            num_friends = random.randint(1, min(max_friends, len(user_ids)-1))
            potential_friends = [uid for uid in user_ids if uid != user_id]
            friends = random.sample(potential_friends, min(num_friends, len(potential_friends)))
            
            for friend_id in friends:
                # Pastikan tidak ada duplikat dengan urutan terbalik
                if (friend_id, user_id) not in pertemanan:
                    pertemanan.add((user_id, friend_id))
        
        if pertemanan:
            cursor.executemany(
                "INSERT INTO Pertemanan (id_user, id_user_teman) VALUES (%s, %s)",
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
        cursor.execute("SELECT id_user FROM User")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        inst_telp = []
        
        for user_id in user_ids:
            num_numbers = random.randint(1, max_numbers)
            for _ in range(num_numbers):
                nomor_telpon = fake.phone_number()[:20]  # Batasi panjang sesuai schema
                inst_telp.append((user_id, nomor_telpon))
        
        if inst_telp:
            cursor.executemany(
                "INSERT INTO InstTelp (id_user, nomor_telpon) VALUES (%s, %s)",
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
        cursor.execute("SELECT id_user FROM Buyer")
        buyer_ids = [row[0] for row in cursor.fetchall()]
        
        alamat = []
        provinsi_kota = {
            'Jakarta': ['Jakarta Pusat', 'Jakarta Selatan', 'Jakarta Barat', 'Jakarta Timur', 'Jakarta Utara'],
            'Jawa Barat': ['Bandung', 'Bogor', 'Bekasi', 'Depok', 'Cimahi'],
            'Jawa Tengah': ['Semarang', 'Surakarta', 'Yogyakarta', 'Magelang', 'Pekalongan'],
            'Jawa Timur': ['Surabaya', 'Malang', 'Sidoarjo', 'Madiun', 'Kediri'],
            'Banten': ['Tangerang', 'Serang', 'Cilegon', 'South Tangerang']
        }
        
        for user_id in buyer_ids:
            num_addresses = random.randint(1, max_addresses)
            for i in range(num_addresses):
                provinsi = random.choice(list(provinsi_kota.keys()))
                kota = random.choice(provinsi_kota[provinsi])
                jalan = fake.street_address()
                is_utama = (i == 0)  # Alamat pertama sebagai utama
                
                alamat.append((user_id, provinsi, kota, jalan, is_utama))
        
        if alamat:
            cursor.executemany(
                """INSERT INTO Alamat 
                (id_user, provinsi, kota, jalan, is_utama) 
                VALUES (%s, %s, %s, %s, %s)""",
                alamat
            )
            connection.commit()
            print(f"✅ Berhasil menambahkan {len(alamat)} alamat")
        
        # Return untuk digunakan di fungsi lain
        cursor.execute("SELECT id_alamat, id_user FROM Alamat WHERE is_utama = TRUE")
        return {row[1]: row[0] for row in cursor.fetchall()}  # Dict {user_id: alamat_utama_id}
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding alamat: {e}")
        return {}
    finally:
        cursor.close()

def seed_produk_dan_varian(connection, count=100):
    """Mengisi data produk dan varian produk"""
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT id_user FROM Seller WHERE is_verified = TRUE")
        seller_ids = [row[0] for row in cursor.fetchall()]
        
        if not seller_ids:
            print("⚠ Tidak ada verified seller. Lewati seeding produk.")
            return {}
        
        produk_ids = {}  # Untuk menyimpan id_produk yang dibuat
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
            id_seller = random.choice(seller_ids)
            kategori = random.choice(list(kategori_produk.keys()))
            subkategori = random.choice(kategori_produk[kategori])
            nama = f"{subkategori} {fake.word().capitalize()}"
            deskripsi = fake.sentence(nb_words=10)
            
            # Insert produk dan dapatkan ID
            cursor.execute(
                """INSERT INTO Produk 
                (nama, deskripsi, id_seller) 
                VALUES (%s, %s, %s)""",
                (nama, deskripsi, id_seller)
            )
            
            product_id = cursor.lastrowid
            produk_ids[product_id] = {"seller_id": id_seller}
            
            # Buat varian produk (1-3 varian per produk)
            num_variants = random.randint(1, 3)
            for j in range(num_variants):
                sku = generate_sku(product_id, j+1)
                nama_varian = f"Varian {j+1} - {fake.color_name()}"
                harga = random.randint(10000, 5000000)
                stok = random.randint(0, 100)
                
                varian_produk.append((sku, product_id, nama_varian, harga, stok))
                produk_ids[product_id].setdefault("varians", []).append({"sku": sku, "stok": stok})
            
            # Tambahkan 1-3 tag
            tags = random.sample(list(kategori_produk.keys()), min(random.randint(1, 3), len(kategori_produk)))
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
        print(f"✅ Berhasil menambahkan {len(produk_ids)} produk, {len(varian_produk)} varian, {len(inst_tag)} tag, dan {len(inst_gambar)} gambar")
        return produk_ids
    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding produk: {e}")
        return {}
    finally:
        cursor.close()

def seed_keranjang_dan_wishlist(connection, produk_ids):
    """Mengisi data keranjang dan wishlist dengan minimal 150 & 100 item"""
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id_user FROM Buyer")
        buyer_ids = [row[0] for row in cursor.fetchall()]

        if not buyer_ids or not produk_ids:
            print("⚠ Tidak ada data buyer atau produk. Lewati seeding keranjang dan wishlist.")
            return

        keranjang = []
        wishlist = []
        keranjang_set = set()
        wishlist_set = set()

        # Seed awal seperti biasa
        for buyer_id in buyer_ids:
            num_cart_items = random.randint(0, 5)
            cart_product_ids = set()

            if num_cart_items > 0:
                product_choices = random.sample(list(produk_ids.keys()), min(num_cart_items, len(produk_ids)))
                for product_id in product_choices:
                    if "varians" in produk_ids[product_id] and produk_ids[product_id]["varians"]:
                        varian = random.choice(produk_ids[product_id]["varians"])
                        if varian["stok"] > 0:
                            kuantitas = random.randint(1, min(5, varian["stok"]))
                            key = (buyer_id, varian["sku"])
                            if key not in keranjang_set:
                                keranjang.append((buyer_id, varian["sku"], product_id, kuantitas))
                                keranjang_set.add(key)
                                cart_product_ids.add(product_id)

            # Wishlist (tidak duplikat dengan keranjang)
            num_wishlist_items = random.randint(0, 5)
            available_products = [pid for pid in produk_ids.keys() if pid not in cart_product_ids]
            if num_wishlist_items > 0 and available_products:
                wishlist_products = random.sample(available_products, min(num_wishlist_items, len(available_products)))
                for product_id in wishlist_products:
                    key = (buyer_id, product_id)
                    if key not in wishlist_set:
                        wishlist.append((buyer_id, product_id))
                        wishlist_set.add(key)

        # Jika belum mencapai jumlah minimal, tambah data ekstra secara acak
        while len(keranjang) < 150:
            buyer_id = random.choice(buyer_ids)
            product_id = random.choice(list(produk_ids.keys()))
            if "varians" in produk_ids[product_id] and produk_ids[product_id]["varians"]:
                varian = random.choice(produk_ids[product_id]["varians"])
                if varian["stok"] > 0:
                    key = (buyer_id, varian["sku"])
                    if key not in keranjang_set:
                        kuantitas = random.randint(1, min(5, varian["stok"]))
                        keranjang.append((buyer_id, varian["sku"], product_id, kuantitas))
                        keranjang_set.add(key)

        while len(wishlist) < 100:
            buyer_id = random.choice(buyer_ids)
            product_id = random.choice(list(produk_ids.keys()))
            key = (buyer_id, product_id)
            if key not in wishlist_set:
                wishlist.append((buyer_id, product_id))
                wishlist_set.add(key)

        # Insert keranjang
        if keranjang:
            cursor.executemany(
                """INSERT INTO Keranjang 
                (id_user, sku, id_produk, kuantitas) 
                VALUES (%s, %s, %s, %s)""",
                keranjang
            )

        # Insert wishlist
        if wishlist:
            cursor.executemany(
                "INSERT INTO Wishlist (id_user, id_produk) VALUES (%s, %s)",
                wishlist
            )

        connection.commit()
        print(f"✅ Berhasil menambahkan {len(keranjang)} item keranjang dan {len(wishlist)} item wishlist")

    except Error as e:
        connection.rollback()
        print(f"❌ Error seeding keranjang dan wishlist: {e}")

    finally:
        cursor.close()


def seed_orders(connection, produk_ids, alamat_utama, count=200):
    """Mengisi data orders"""
    cursor = connection.cursor()
    
    try:
        if not alamat_utama or not produk_ids:
            print("⚠ Tidak cukup data untuk seeding orders. Diperlukan buyer dengan alamat dan produk.")
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
        payment_methods = ['Transfer Bank', 'Kartu Kredit', 'OVO', 'Gopay', 'Dana', 'COD']
        shipping_methods = ['JNE', 'J&T', 'SiCepat', 'Ninja Express', 'AnterAja']
        
        # ID dari buyer yang memiliki alamat utama
        buyer_ids = list(alamat_utama.keys())
        
        for _ in range(min(count, len(buyer_ids) * len(produk_ids))):
            buyer_id = random.choice(buyer_ids)
            id_alamat = alamat_utama[buyer_id]
            
            status_order = random.choices(
                status_options,
                weights=[10, 20, 20, 40, 10]  # Lebih banyak pesanan yang sudah sampai
            )[0]
            metode_pembayaran = random.choice(payment_methods)
            metode_pengiriman = random.choice(shipping_methods)
            catatan = fake.sentence(nb_words=5) if random.random() > 0.7 else None
            
            # Insert order
            cursor.execute("""
                INSERT INTO Orders 
                (id_alamat, id_user, status_order, metode_pembayaran, metode_pengiriman, catatan) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_alamat, buyer_id, status_order, metode_pembayaran, metode_pengiriman, catatan))
            
            order_id = cursor.lastrowid
            
            # Tambahkan 1-3 produk ke order
            num_products = random.randint(1, 3)
            product_choices = random.sample(list(produk_ids.keys()), min(num_products, len(produk_ids)))
            
            for product_id in product_choices:
                if "varians" in produk_ids[product_id] and produk_ids[product_id]["varians"]:
                    varian = random.choice(produk_ids[product_id]["varians"])
                    kuantitas = random.randint(1, 5)
                    
                    inst_produk.append((order_id, product_id, varian["sku"], kuantitas))
        
        # Insert instproduk
        if inst_produk:
            cursor.executemany(
                """INSERT INTO InstProduk 
                (id_order, id_produk, sku, kuantitas) 
                VALUES (%s, %s, %s, %s)""",
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
        seed_buyers_and_sellers(connection)
        seed_pertemanan(connection)
        seed_inst_telp(connection)
        alamat_utama = seed_alamat(connection)
        produk_ids = seed_produk_dan_varian(connection)
        seed_keranjang_dan_wishlist(connection, produk_ids)
        seed_orders(connection, produk_ids, alamat_utama)
        
        print("\n🎉 Database seeding berhasil diselesaikan!")
    except Error as e:
        print(f"\n🔥 Error selama seeding: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Koneksi database ditutup")

if __name__ == "__main__":
    main()