-- schema.sql
CREATE DATABASE IF NOT EXISTS bustbuy15;
USE bustbuy15;

-- tabel User (parent dari Buyer dan Seller)
CREATE TABLE IF NOT EXISTS `User` (
    id_user INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nama_panjang VARCHAR(255) NOT NULL,
    tanggal_lahir DATE NOT NULL,
    no_telp VARCHAR(20) NOT NULL,
    foto_profil VARCHAR(255),
    tipe ENUM('Buyer', 'Seller') DEFAULT 'Buyer' NOT NULL,

    CHECK (no_telp REGEXP '^[0-9]{8,15}$'),
    CHECK (TRIM(nama_panjang) <> ''),
    CHECK (email REGEXP '^[^@\\s]+@[^@\\s]+\\.com$')
);

DELIMITER //

CREATE TRIGGER user_age_insert_check
BEFORE INSERT ON User
FOR EACH ROW
BEGIN
    -- Menghitung usia berdasarkan tanggal lahir yang baru dan tanggal saat ini
    -- Jika tanggal lahir BARU lebih dari 17 tahun ke belakang dari tanggal hari ini, berarti usia < 17 tahun
    IF NEW.tanggal_lahir > DATE_SUB(CURDATE(), INTERVAL 17 YEAR) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usia pengguna harus minimal 17 tahun.';
    END IF;
END;
//

CREATE TRIGGER user_age_update_check
BEFORE UPDATE ON User
FOR EACH ROW
BEGIN
    IF NEW.tanggal_lahir > DATE_SUB(CURDATE(), INTERVAL 17 YEAR) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usia pengguna harus minimal 17 tahun.';
    END IF;
END;
//

DELIMITER ;

CREATE TABLE IF NOT EXISTS Pertemanan (
    id_user INT NOT NULL,
    id_user_teman INT NOT NULL,

    PRIMARY KEY (id_user, id_user_teman),

    FOREIGN KEY (id_user) REFERENCES `User`(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (id_user_teman) REFERENCES `User`(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Seller (
    id_user INT NOT NULL PRIMARY KEY,
    ktp VARCHAR(255) NOT NULL,
    foto_diri VARCHAR(255) NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE NOT NULL,

    FOREIGN KEY (id_user) REFERENCES `User`(id_user)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CHECK (ktp <> foto_diri)
);

DELIMITER //
CREATE TRIGGER check_seller_verification_transition
BEFORE UPDATE ON Seller
FOR EACH ROW
BEGIN
    IF OLD.is_verified = TRUE AND NEW.is_verified = FALSE THEN SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Status seller tidak dapat berubah dari verified menjadi tidak verified';
    END IF;
END;//
DELIMITER ;

DELIMITER //

CREATE TRIGGER seller_verification_check
BEFORE UPDATE ON Seller
FOR EACH ROW
BEGIN
    IF NEW.is_verified = TRUE AND (NEW.ktp IS NULL OR 
    TRIM(NEW.ktp) = '' OR NEW.foto_diri IS NULL OR 
    TRIM(NEW.foto_diri) = '') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Tidak bisa memverifikasi seller 
        sebelum KTP dan foto diri diunggah.';
    END IF;
END;
//

DELIMITER ;

CREATE TABLE IF NOT EXISTS Buyer (
    id_user INT NOT NULL PRIMARY KEY,

    FOREIGN KEY (id_user) REFERENCES `User`(id_user)
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
        ON UPDATE CASCADE,
    
    CHECK (TRIM(nama) <> ''),
    UNIQUE(id_seller, nama)
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
        ON UPDATE CASCADE,
    
    CHECK (TRIM(nama_varian) <> ''),
    CHECK (TRIM(sku) <> '')
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
        ON UPDATE CASCADE,

    CHECK (kuantitas >= 1),
    UNIQUE(id_user, id_produk, sku)
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
        ON UPDATE CASCADE,
    
    CHECK (TRIM(jalan) <> ''),
    CHECK (TRIM(kota) <> ''),
    CHECK (TRIM(provinsi) <> '')
);

DELIMITER //
CREATE TRIGGER alamat_utama_check 
    BEFORE INSERT ON Alamat
    FOR EACH ROW
BEGIN
    IF NEW.is_utama = TRUE THEN
        UPDATE Alamat SET is_utama = FALSE WHERE id_user = NEW.id_user;
    END IF;
END//

CREATE TRIGGER alamat_utama_update_check 
    BEFORE UPDATE ON Alamat
    FOR EACH ROW
BEGIN
    IF NEW.is_utama = TRUE AND OLD.is_utama = FALSE THEN
        UPDATE Alamat SET is_utama = FALSE WHERE id_user = NEW.id_user AND id_alamat != NEW.id_alamat;
    END IF;
END//
DELIMITER ;

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

DELIMITER //
CREATE TRIGGER check_status_order_transition
BEFORE UPDATE ON Orders
FOR EACH ROW
BEGIN
    DECLARE msg VARCHAR(255);


    IF OLD.status_order = 'belum dibayar' AND NEW.status_order NOT IN ('disiapkan', 'dibatalkan') THEN
        SET msg = 'Transisi dari "belum dibayar" hanya boleh ke "disiapkan" atau "dibatalkan"';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
    END IF;


    IF OLD.status_order = 'disiapkan' AND NEW.status_order NOT IN ('dikirim', 'dibatalkan') THEN
        SET msg = 'Transisi dari "disiapkan" hanya boleh ke "dikirim" atau "dibatalkan"';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
    END IF;


    IF OLD.status_order = 'dikirim' AND NEW.status_order NOT IN ('sampai', 'dibatalkan') THEN
        SET msg = 'Transisi dari "dikirim" hanya boleh ke "sampai" atau "dibatalkan"';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
    END IF;


    IF OLD.status_order = 'sampai' AND NEW.status_order != 'sampai' THEN
        SET msg = 'Order yang sudah "sampai" tidak bisa diubah';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
    END IF;


    IF OLD.status_order = 'dibatalkan' AND NEW.status_order != 'dibatalkan' THEN
        SET msg = 'Order yang "dibatalkan" tidak bisa diubah';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
    END IF;
END;//
DELIMITER ;

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
        ON UPDATE CASCADE,
    
    CHECK (TRIM(tag) <> '')
);

CREATE TABLE IF NOT EXISTS InstGambar (
    id_produk INT NOT NULL,
    gambar VARCHAR(255) NOT NULL,

    PRIMARY KEY (id_produk, gambar),

    FOREIGN KEY (id_produk) REFERENCES Produk(id_produk)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CHECK (TRIM(gambar) <> '')
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
);

DELIMITER //
CREATE TRIGGER ulasan_validation 
    BEFORE INSERT ON Ulasan
    FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM InstProduk 
        WHERE id_order = NEW.id_order AND id_produk = NEW.id_produk
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ulasan hanya dapat dibuat untuk produk yang ada dalam order';
    END IF;
END//
DELIMITER ;

DELIMITER //

CREATE TRIGGER pertemanan_self_check_insert
BEFORE INSERT ON Pertemanan
FOR EACH ROW
BEGIN
    IF NEW.id_user = NEW.id_user_teman THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User tidak dapat berteman dengan dirinya sendiri';
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE TRIGGER pertemanan_self_check_update
BEFORE UPDATE ON Pertemanan
FOR EACH ROW
BEGIN
    IF NEW.id_user = NEW.id_user_teman THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User tidak dapat berteman dengan dirinya sendiri';
    END IF;
END;
//

DELIMITER ;

-- Trigger untuk validasi Varian Produk: nama_varian harus unik untuk setiap produk
DELIMITER //

CREATE TRIGGER varian_produk_unique_check_insert
BEFORE INSERT ON VarianProduk
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM VarianProduk 
        WHERE id_produk = NEW.id_produk 
        AND nama_varian = NEW.nama_varian 
        AND sku != NEW.sku
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nama varian harus unik untuk setiap produk';
    END IF;
END;
//

DELIMITER ;

DELIMITER //

CREATE TRIGGER varian_produk_unique_check_update
BEFORE UPDATE ON VarianProduk
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM VarianProduk 
        WHERE id_produk = NEW.id_produk 
        AND nama_varian = NEW.nama_varian 
        AND sku != NEW.sku
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nama varian harus unik untuk setiap produk';
    END IF;
END;
//

DELIMITER ;