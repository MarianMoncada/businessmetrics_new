CREATE TABLE cliente (
  cliente_id SERIAL PRIMARY KEY,
  rfc VARCHAR(13) UNIQUE NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE vendedor (
  id_vendedor SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE producto (
  id_producto SERIAL PRIMARY KEY,
  categoria VARCHAR(50) NOT NULL,
  descripcion TEXT,
  precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
  stock INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE venta (
  id_venta SERIAL PRIMARY KEY,
  id_cliente INT NOT NULL,
  id_vendedor INT NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  impuestos DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  fecha TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (id_cliente) REFERENCES cliente(cliente_id),
  FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor)
);

CREATE TABLE detalle_vta (
  id_detalle SERIAL PRIMARY KEY,
  id_venta INT NOT NULL,
  id_producto INT NOT NULL,
  cantidad INT NOT NULL CHECK (cantidad > 0),
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (id_venta) REFERENCES venta(id_venta),
  FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);
