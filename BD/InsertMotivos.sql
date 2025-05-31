INSERT INTO "Motivos" (nombre, etapa, fecha_creacion, fecha_actualizacion)
VALUES 
    -- Etapa 1
    ('Imagen Faltante de Integrar', '1', NOW(), NOW()), -- Motivo 1
    ('Imagen Sobrante - Falta en la Relación', '1', NOW(), NOW()), -- Motivo 2
    ('Imagen Ilegible', '1', NOW(), NOW()), -- Motivo 3
    ('Radicado con inconsistencia en cantidad de Anexos', '1', NOW(), NOW()), -- Motivo 4
    ('Radicado no cumple estructura', '1', NOW(), NOW()), -- Motivo 5
    ('Oficio sin Firma y Sin Correo Origen', '1', NOW(), NOW()), -- Motivo 6
    ('Radicado con inconsistencia en cantidad de Páginas', '1', NOW(), NOW()), -- Motivo 7
    ('Oficio NO está Dirigido al Banco Davivienda', '1', NOW(), NOW()), -- Motivo 8
    ('Oficio afectado empleado Davivienda (exclusivamente)', '1', NOW(), NOW()), -- Motivo 9
    ('Oficios Derechos Económicos, Acciones, Canon de Arrendamiento (exclusivamente)', '1', NOW(), NOW()), -- Motivo 10
    ('Oficios DaviPlata (Exclusivamente)', '1', NOW(), NOW()), -- Motivo 11
    ('PDF con imágenes de Oficios de diferente Entidad', '1', NOW(), NOW()), 


    -- Etapa 2
    ('Solicitud de Embargo e Información (Mixto)', '2', NOW(), NOW()), -- Motivo 12
    ('Embargo FIDUCIARIA - Mixto', '2', NOW(), NOW()), -- Motivo 13
    ('Diferencia Entre Letras y Números Cuantía', '2', NOW(), NOW()), -- Motivo 14
    ('Cambio De Cuantía', '2', NOW(), NOW()), -- Motivo 15
    ('Cambio Cuenta de Depósito Judicial', '2', NOW(), NOW()), -- Motivo 16
    ('Multas, Sanciones y Reiteraciones', '2', NOW(), NOW()), -- Motivo 17
    ('Oficios Terceras Partes/Porcentajes', '2', NOW(), NOW()), -- Motivo 18
    ('Oficios de Remanentes', '2', NOW(), NOW()), -- Motivo 19
    ('Oficio Daviplata (Mixto)', '2', NOW(), NOW()), -- Motivo 20
    ('Oficio Derechos Económicos, Acciones, Canon de Arrendamiento (Mixto)', '2', NOW(), NOW()), -- Motivo 21
    ('Oficio afectado empleado Davivienda (Mixto)', '2', NOW(), NOW()) -- Motivo 22