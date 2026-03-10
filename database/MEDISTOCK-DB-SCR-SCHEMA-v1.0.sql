CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    password VARCHAR(100),
    rol VARCHAR(50)
);

CREATE TABLE medicamentos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100),
    descripcion TEXT
);

CREATE TABLE inventario (
    id INT PRIMARY KEY AUTO_INCREMENT,
    medicamento_id INT,
    lote VARCHAR(50),
    fecha_caducidad DATE,
    stock INT,
    FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id)
);
