INSERT INTO cliente (rfc, nombre, apellido, email) VALUES
('ABC123456789', 'Juan', 'Pérez', 'juan@proyectoabd'),
('DEF987654321', 'María', 'González', 'maria@proyectoabd'),
('GHI456789123', 'Carlos', 'López', 'carlos@proyectoabd'),
('JKL789123456', 'Laura', 'Ramírez', 'laura@proyectoabd'),
('MNO321654987', 'Pedro', 'Hernández', 'pedro@proyectoabd'),
('PQR654987321', 'Lucía', 'Torres', 'lucia@proyectoabd'),
('STU147258369', 'Andrés', 'Flores', 'andres@proyectoabd'),
('VWX369258147', 'Sofía', 'Rojas', 'sofia@proyectoabd'),
('YZA258369147', 'Miguel', 'Cruz', 'miguel@proyectoabd'),
('BCD159357486', 'Elena', 'Suárez', 'elena@proyectoabd');

INSERT INTO vendedor (nombre, apellido, email) VALUES
('Ana', 'Martínez', 'ana@proyectoabd'),
('Luis', 'Rodríguez', 'luis@proyectoabd'),
('Paula', 'Vega', 'paula@proyectoabd'),
('Jorge', 'Navarro', 'jorge@proyectoabd'),
('Natalia', 'Santos', 'natalia@proyectoabd'),
('Diego', 'Mendoza', 'diego@proyectoabd'),
('Carmen', 'Ibáñez', 'carmen@proyectoabd'),
('Hugo', 'Silva', 'hugo@proyectoabd'),
('Irene', 'Lara', 'irene@proyectoabd'),
('Raúl', 'Campos', 'raul@proyectoabd');

INSERT INTO producto (categoria, descripcion, precio, stock) VALUES
('Electrónica', 'Laptop Dell Inspiron', 15000.00, 10),
('Electrónica', 'Mouse Logitech Inalámbrico', 250.00, 50),
('Oficina', 'Silla Ergonómica Negra', 2500.00, 20),
('Oficina', 'Escritorio de Madera', 4800.00, 15),
('Accesorios', 'Teclado Mecánico', 1200.00, 30),
('Accesorios', 'Audífonos Bluetooth', 900.00, 40),
('Electrónica', 'Monitor 24 pulgadas', 3500.00, 18),
('Oficina', 'Organizador de Escritorio', 300.00, 60),
('Accesorios', 'Base para Laptop', 650.00, 25),
('Electrónica', 'Impresora Multifuncional', 4200.00, 12);

INSERT INTO venta (id_cliente, id_vendedor, subtotal, impuestos, total, fecha) VALUES
(1, 1, 15000.00, 2400.00, 17400.00, NOW()),
(2, 2, 250.00, 40.00, 290.00, NOW() - INTERVAL '1 day'),
(3, 3, 2500.00, 400.00, 2900.00, NOW() - INTERVAL '2 days'),
(4, 4, 4800.00, 768.00, 5568.00, NOW() - INTERVAL '3 days'),
(5, 5, 1200.00, 192.00, 1392.00, NOW() - INTERVAL '4 days'),
(6, 6, 900.00, 144.00, 1044.00, NOW() - INTERVAL '5 days'),
(7, 7, 3500.00, 560.00, 4060.00, NOW() - INTERVAL '6 days'),
(8, 8, 300.00, 48.00, 348.00, NOW() - INTERVAL '7 days'),
(9, 9, 650.00, 104.00, 754.00, NOW() - INTERVAL '8 days'),
(10, 10, 4200.00, 672.00, 4872.00, NOW() - INTERVAL '9 days');

INSERT INTO detalle_vta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 1, 15000.00, 15000.00),
(2, 2, 1, 250.00, 250.00),
(3, 3, 1, 2500.00, 2500.00),
(4, 4, 1, 4800.00, 4800.00),
(5, 5, 1, 1200.00, 1200.00),
(6, 6, 1, 900.00, 900.00),
(7, 7, 1, 3500.00, 3500.00),
(8, 8, 1, 300.00, 300.00),
(9, 9, 1, 650.00, 650.00),
(10, 10, 1, 4200.00, 4200.00);
