-- schema.sql

-- tabel User (parent dari Buyer dan Seller)
CREATE TABLE IF NOT EXISTS User (
    -- id INT PRIMARY KEY NOT NULL, (kalau setuju)
    email VARCHAR(255) PRIMARY KEY NOT NULL,

    password_hash VARCHAR(255) NOT NULL,
    nama_panjang VARCHAR(255) NOT NULL,
    tanggal_lahir DATE, -- wajib apa kgk?
    foto_profil VARCHAR(255), --wajib apa kgk?
    tipe ENUM('Buyer', 'Seller') DEFAULT 'Buyer'
);

CREATE TABLE IF NOT EXISTS Pertemanan(
    email VARCHAR(255) NOT NULL,
    email_friend VARCHAR(255) NOT NULL,
    PRIMARY KEY (email, email_friend),

    -- FOREIGN KEY (email_friend) REFERENCES User(email),
    -- FOREIGN KEY (email) REFERENCES User(email)

    -- perlu pake on delete cascade on update cascade gk ya? apa gk boleh?
    -- both email sama email_friend better keduanya jadi PK atau tabel gk ada PK samsek?
);

CREATE TABLE IF NOT EXISTS InstTelp(
    email VARCHAR(255) NOT NULL,
    nomor_telpon VARCHAR(20) NOT NULL,
    PRIMARY KEY (email, nomor_telpon),

    FOREIGN KEY (email) REFERENCES User(email)
    -- perlu pake on delete cascade on update cascade gk ya? apa gk boleh?
    -- email better keduanya jadi PK atau tabel gk ada PK samsek?
);

CREATE TABLE IF NOT EXISTS Buyer(
    email VARCHAR(255) PRIMARY KEY NOT NULL,
    FOREIGN KEY (email) REFERENCES User(email)
);

CREATE TABLE IF NOT EXISTS Keranjang(
    -- ini sementara, blm fix masalah PK
    email VARCHAR(255) NOT NULL,
    sku VARCHAR(255) NOT NULL,
    id_produk INT NOT NULL,

    PRIMARY KEY(email, sku, id_produk),

    kuantitas INT NOT NULL,

    FOREIGN KEY (email) REFERENCES Buyer(email),
    FOREIGN KEY (sku) REFERENCES VarianProduk(sku),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk) --masih sementara
);

CREATE TABLE IF NOT EXISTS Wishlist(
    -- ini sementara, blm fix masalah PK
    email VARCHAR(255) NOT NULL,
    id_produk INT NOT NULL,

    -- PRIMARY KEY(email, id_produk),

    FOREIGN KEY (email) REFERENCES Buyer(email),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);

CREATE TABLE IF NOT EXISTS Alamat(
    email VARCHAR(255) NOT NULL,
    id_alamat INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    provinsi VARCHAR(255) NOT NULL,
    kota VARCHAR(255) NOT NULL,
    jalan VARCHAR(255) NOT NULL,
    is_utama BOOLEAN NOT NULL,

    FOREIGN KEY (email) REFERENCES Buyer(email) 
);

CREATE TABLE IF NOT EXISTS Orders(
    id_order INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_alamat INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    status_order ENUM('pesanan belum dibayar', 'pesanan sedang disiapkan', 'pesanan sedang dikirim', 'pesanan sampai', 'pesanan dibatalkan') NOT NULL,
    metode_pembayaran VARCHAR(255) NOT NULL,
    metode_pengiriman VARCHAR(255) NOT NULL,
    catatan VARCHAR(255) NOT NULL,
    waktu_pemesanan TIMESTAMP NOT NULL,
    kuantitas INT NOT NULL DEFAULT 1,
    sku VARCHAR(255), -- bisa null kan yak

    FOREIGN KEY (id_alamat) REFERENCES Buyer(email),
    FOREIGN KEY (email) REFERENCES Alamat(id_alamat)

    -- FK SKU?
);

CREATE TABLE IF NOT EXISTS InstProduk(
    id_order INT NOT NULL,
    id_produk INT NOT NULL,

    -- PRIMARY KEY(id_order, id_produk),

    FOREIGN KEY (id_order) REFERENCES Orders(id_order),
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)

    -- FK SKU?
);

CREATE TABLE IF NOT EXISTS Produk(
    id_produk INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nama VARCHAR(255) NOT NULL,
    deskripsi VARCHAR(255), --not null or nah
    email VARCHAR(255) NOT NULL,

    FOREIGN KEY (email) REFERENCES VerifiedSeller(email)
);

CREATE TABLE IF NOT EXISTS VarianProduk(
    sku VARCHAR(255) NOT NULL,
    id_produk INT NOT NULL,
    nama_varian VARCHAR(255) NOT NULL,
    harga INT NOT NULL,
    stok INT NOT NULL,

    PRIMARY KEY (sku, id_produk),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);

CREATE TABLE IF NOT EXISTS InstTag(
    id_produk INT NOT NULL,
    tag VARCHAR(255) NOT NULL,

    -- PRIMARY KEY (tag, id_produk),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);

CREATE TABLE IF NOT EXISTS InstGambar(
    id_produk INT NOT NULL,
    gambar VARCHAR(255) NOT NULL,

    -- PRIMARY KEY (gambar, id_produk),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
);

CREATE TABLE IF NOT EXISTS Seller(
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    ktp VARCHAR(255) NOT NULL,
    foto_diri VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL,

    FOREIGN KEY (email) REFERENCES User(email)
)