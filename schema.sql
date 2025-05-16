-- schema.sql
CREATE DATABASE IF NOT EXISTS bustbuy;
USE bustbuy;

-- tabel User (parent dari Buyer dan Seller)
CREATE TABLE IF NOT EXISTS User (
    id_user INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nama_panjang VARCHAR(255) NOT NULL,
    tanggal_lahir DATE,
    foto_profil VARCHAR(255),
    tipe ENUM('Buyer', 'Seller') DEFAULT 'Buyer'
);

CREATE TABLE IF NOT EXISTS Pertemanan (
    id_user INT NOT NULL,
    id_user_teman INT NOT NULL,

    PRIMARY KEY (id_user, id_user_teman),

    FOREIGN KEY (id_user) REFERENCES User(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_user_teman) REFERENCES User(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Seller (
    id_user INT NOT NULL PRIMARY KEY,
    ktp VARCHAR(255) NOT NULL,
    foto_diri VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (id_user) REFERENCES User(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS InstTelp (
    id_user INT NOT NULL,
    nomor_telpon VARCHAR(20) NOT NULL,

    PRIMARY KEY (id_user, nomor_telpon),

    FOREIGN KEY (id_user) REFERENCES User(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Buyer (
    id_user INT NOT NULL PRIMARY KEY,

    FOREIGN KEY (id_user) REFERENCES User(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Produk (
    id_produk INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_seller INT NOT NULL,
    nama VARCHAR(255) NOT NULL,
    deskripsi TEXT,

    FOREIGN KEY (id_seller) REFERENCES Seller(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS VarianProduk (
    sku VARCHAR(255) NOT NULL,
    id_produk INT NOT NULL,
    nama_varian VARCHAR(255) NOT NULL,
    harga INT NOT NULL CHECK (harga >= 0),
    stok INT NOT NULL DEFAULT 0 CHECK (stok >= 0),

    PRIMARY KEY (sku, id_produk),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Keranjang (
    id_keranjang INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_user INT NOT NULL,
    id_produk INT NOT NULL,
    sku VARCHAR(255) NOT NULL,
    kuantitas INT NOT NULL DEFAULT 1,

    FOREIGN KEY (id_user) REFERENCES Buyer(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (sku, id_produk) REFERENCES VarianProduk(sku, id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Wishlist (
    id_user INT NOT NULL,
    id_produk INT NOT NULL,

    PRIMARY KEY(id_user, id_produk),

    FOREIGN KEY (id_user) REFERENCES Buyer(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Alamat (
    id_alamat INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_user INT NOT NULL,
    provinsi VARCHAR(255) NOT NULL,
    kota VARCHAR(255) NOT NULL,
    jalan VARCHAR(255) NOT NULL,
    is_utama BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (id_user) REFERENCES Buyer(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE 
);

CREATE TABLE IF NOT EXISTS Orders (
    id_order INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_user INT NOT NULL,
    id_alamat INT NOT NULL,
    status_order ENUM('belum dibayar', 
                      'disiapkan',
                      'dikirim', 
                      'sampai', 
                      'dibatalkan')
        NOT NULL DEFAULT 'belum dibayar',
    metode_pembayaran VARCHAR(255) NOT NULL,
    metode_pengiriman VARCHAR(255) NOT NULL,
    waktu_pemesanan TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    catatan VARCHAR(255),

    FOREIGN KEY (id_user) REFERENCES Buyer(id_user)
        ON UPDATE CASCADE,
    FOREIGN KEY (id_alamat) REFERENCES Alamat(id_alamat)
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS InstProduk (
    id_order INT NOT NULL,
    id_produk INT NOT NULL,
    sku VARCHAR(255) NOT NULL,
    kuantitas INT NOT NULL DEFAULT 1,

    PRIMARY KEY(id_order, id_produk, sku),

    FOREIGN KEY (id_order) REFERENCES Orders(id_order)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (sku, id_produk) REFERENCES VarianProduk(sku, id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS InstTag (
    id_produk INT NOT NULL,
    tag VARCHAR(255) NOT NULL,

    PRIMARY KEY (tag, id_produk),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS InstGambar (
    id_produk INT NOT NULL,
    gambar VARCHAR(255) NOT NULL,

    PRIMARY KEY (id_produk, gambar),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Ulasan (
    id_ulasan INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_order INT NOT NULL,
    id_produk INT NOT NULL,
    nilai INT NOT NULL CHECK (nilai BETWEEN 1 AND 5),
    komentar TEXT,

    FOREIGN KEY (id_order) REFERENCES Orders(id_order)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)