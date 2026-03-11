CREATE DATABASE medistock;
USE medistock;

-- Tabla de categorías de medicamentos
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255)
);

-- Tabla de medicamentos
CREATE TABLE medications (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id INT,
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Tabla de inventario
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    medication_id INT NOT NULL,
    quantity INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
);

-- Movimientos de inventario
CREATE TABLE inventory_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    medication_id INT NOT NULL,
    movement_type VARCHAR(50),
    quantity INT,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
);
INSERT INTO categories (name, description)
VALUES ('Analgesicos', 'Medicamentos para aliviar el dolor');

INSERT INTO medications (name, description, category_id, expiration_date)
VALUES ('Paracetamol', 'Alivio de dolor y fiebre', 1, '2027-12-31');

INSERT INTO inventory (medication_id, quantity)
VALUES (1, 100);
