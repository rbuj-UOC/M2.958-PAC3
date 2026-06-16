-- Crear la base de dades botigues si no existeix
CREATE DATABASE IF NOT EXISTS botigues;
USE botigues;

-- Crear l'usuari uoc amb permisos a la base de dades botigues
DROP USER IF EXISTS 'uoc'@'%';
CREATE USER 'uoc'@'%' IDENTIFIED BY 'examplepass';
GRANT ALL PRIVILEGES ON botigues.* TO 'uoc'@'%';
FLUSH PRIVILEGES;

-- Crear la taula productes si no existeix
CREATE TABLE IF NOT EXISTS productes (
    id_producte VARCHAR(20) PRIMARY KEY,
    departament VARCHAR(255) NOT NULL,
    descripcio VARCHAR(255) NOT NULL,
    preu DECIMAL(10, 2) NOT NULL
);

-- Crear la taula vendes si no existeix
CREATE TABLE IF NOT EXISTS vendes (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_botiga VARCHAR(20) NOT NULL,
    id_producte VARCHAR(20) NOT NULL,
    quantitat INT NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    -- Afegir la clau forana que fa referència a la taula productes
    CONSTRAINT fk_vendes_productes
        FOREIGN KEY (id_producte)
        REFERENCES productes(id_producte)
);
