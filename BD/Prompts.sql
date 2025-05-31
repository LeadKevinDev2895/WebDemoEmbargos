INSERT INTO public."Prompts" ("tipoPrompt",prompt,context,"json",fecha_creacion,fecha_actualizacion) VALUES
	 ('TITULO','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','Tu tarea es extraer información de documentos de embargo y desembargo siguiendo las siguientes reglas de extracción. Asegúrate de que cada metadato se extraiga de manera fiel y sin inferencias. Si un dato no está presente, debe marcarse como vacío ("").

Aquí están las reglas de extracción:

- **Instrucciones generales**: Analiza el contenido en su contexto y extrae cada metadato según su ubicación y relación con otros elementos.
',NULL,NULL,NULL),
	 ('PRODUCTOS','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','
- **productosBancarioMencionadosDelDemandado**: Extrae los productos financieros del documento, en espacial los que tengan un numero, ejemplo cuenta de haorro numero xxxxxxxxxxxxx

### **nombre**
Busca en el documento alguno de estos productos completos:

- Cuentas de ahorro
- Cuentas corrientes
- CDT (Certificados de Depósito a Término)
- Depósitos
- Daviplata
- Canon de Arrendamiento
- Producto de deudores
- Productos Fiduciarios
- Carteras Colectivas
- Títulos de Capitalización
- Fondos de Inversión

### **Número de Producto**

Nota si alguno de los productos extraídos tiene un numero debe marcar **asociarProducto** como true de lo contrario false

* Contexto: Asegúrate que la mención del producto esté en el contexto del embargo o desembargo.
','  "productosBancarioMencionadosDelDemandado": [
  {"nombre":"CDT", "numeroProducto": "1003030303030"}
 ],',NULL,NULL),
	 ('RESOLUCIONES','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','
- **resolucionesRadicadosNumerosReferencias**: Extraer cualquier identificador numérico o alfanumérico que permita distinguir unívocamente un documento dentro de su contexto administrativo, judicial o institucional.
La extracción debe realizarse en el orden de prioridad indicado, asegurando que se seleccionen los identificadores más específicos y relevantes.

Lee el documento y detecta todos los campos relevantes, tales como nombres, fechas, identificadores, direcciones, montos, tablas, subtítulos, firmas y cualquier otro campo presente en el documento.
Proporciona un listado completo de todos los campos identificados para asegurar una extracción completa.
Genera una estructura JSON con los campos identificados, organizando la información de manera clara.
Reglas para la extracción
Extrae solo la información literal contenida en el documento, sin inferencias.
No omitas ningún campo.
Si un campo no puede identificarse claramente, se marcará como null en la estructura JSON.
Si hay datos tabulares, organízalos en listas o matrices.

Números de Resolución Judicial (23 dígitos)
Identificadores de Procesos Coactivos
Otros identificadores administrativos o institucionales

Tipos de Identificadores a Extraer
1. Identificadores Judiciales (23 Dig)

*. Número de proceso
Número de proceso judicial (23 dígitos)
Número de radicado, rad o radicacion
Número de expediente
Referencia de proceso ejecutivo
*. Proceso laboral
*. Proceso ejecutivo
*. Radicado
*. Radicación
*. Expediente
*. Ref Ejecutivo
*. No

2. Identificadores Coactivos y Administrativos

Debes identificarlas en el siguiente orden

1- Resolución
2- Número Proceso / Proceso No.
3- Número Mandamiento de Pago / Mandamiento / MPC
4- Número Expediente / Expediente No. / EXP
5- Número Radicado / Radicado No.
6- Número Auto de Cobro
7- Número Comparendo /  Comparendo No.
8- Número Placa  / Placa No.
9- Número Contrato / No. Contrato /  Contrato
10- Número Proceso de Responsabilidad Fiscal / PRF No.
11- Consecutivo
12- Referencia de Pago
13- Referencia de Ejecución
14- Vigencia
15- Industria
16- Cédula Catastral
17- Matrícula Catastral
Radicación
Número de resolución administrativa
Número de mandamiento de pago
Número de expediente coactivo
Número de auto de cobro
Referencia de ejecución
Números de comparendo
Placas de vehículos (formato: XXX000 o XXX00X)
Referencias catastrales
Números de contrato
Números de proceso de responsabilidad fiscal
Matrículas inmobiliarias
Consecutivos institucionales

Reglas de Extracción
Priorización

Buscar primero en encabezado y sección de referencias
Priorizar el identificador más específico y completo
En caso de múltiples identificadores, extraer el más relevante según contexto','"resolucionesRadicadosNumerosReferencias": [
   "522874089001-2023-00049-00"
],',NULL,NULL),
	 ('DEMANDANTES','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','
- **Demandante**: # Extracción y Estructuración de Información del Demandante

Extrae y estructura la información del **DEMANDANTE** mencionados en el documento. El demandante se refiere a la persona natural o jurídica que solicita o reclama el embargo esto principalmente para los documentos provienen de juzgados. para el caso de entidades coactivas diferentes a juzgados normalmente el demandante es el firmante o el que dirige el documento y este puede llegar a tener la misma información de la entidad ya que como tal el demandante es la entidad en si y la persona que firma es el representante de la misma. Por otro lado para juzgados normalmente el demandante es un ente diferente al juzgado, es muy importante que no lo confundas con el o los destinatario del oficio.

Asegúrate de capturar cada instancia sin omitir datos válidos y sigue el formato indicado para cada demandante encontrado.  

Identifica la sección del documento donde se menciona la información del proceso judicial, en especial el apartado del demandante.
Extrae el nombre completo y el número de identificación (NIT o Cédula de Ciudadanía) del demandante listado en el documento.
Organiza los datos en una estructura JSON, asegurándote de que el demandante tenga su propio objeto con los datos correctamente estructurados.
No infieras información ni omitas datos. Extrae únicamente lo que esté explicitamente escrito en el documento.

---

## **Formato de Extracción**

Para tipos de entidades JUDICIALES este va a ser diferente a la entidad, para COACTIVAS es la misma

### **tipoIdentificacionDelDemandante**
Extrae el tipo de identificación del demandante tal como aparece en el documento, el demandante de igual manera se refiere a la entidad que emite el documento no a la persona que representa esta entidad.

Busca menciones de los siguientes valores estándar:

- **CC**: Cédula de Ciudadanía  
- **CE**: Cédula de Extranjería  
- **NIT**: Número de Identificación Tributaria  
- **TI**: Tarjeta de Identidad  
- **PA**: Pasaporte  
- **NITE**: NIT de Persona Extranjera  
- **NITP**: NIT de Persona Natural  


Valida que el tipo de identificación corresponda específicamente al demandante y no a otra persona o entidad. Asegúrate de no confundir esta información con la del demandado (la persona contra la que se dirige el proceso). Selecciona el que no esté asociado a un término de oposición como "demandado"

---

### **numeroIdentificacionDelDemandante*
Extrae el número de identificación exactamente como aparece en el documento. 

Busca números relacionados con los tipos de identificación mencionados (**CC, NIT, CE, TI, PA, NITE, NITP**).

Ejemplo de Extracción
Entrada en el documento
"PROCESO EJECUTIVO SINGULAR No. 110014189082-2024 00339-00 de AECSA S.A.S. con Nit No. 830.059.718-5 contra ELIANA HASBLEIDY GUTIERREZ DIAZ con C.C. 1.033.778.858."

Salida Esperada

{
  "NombreEmpresaDemandante": "AECSA S.A.S",
  "numeroIdentificacionDelDemandante": "830.059.718-5",
  "tipoIdentificacionDelDemandante": "NIT",
}

Verifica que el número de identificación corresponda específicamente al demandante y no a un demandado, o cualquier otra entidad, este es un solo numero, de no encontrarlo retorna null.

### *** Para la identificación del nombre o la razón social ten en cuenta que si es una persona natural debes extraer el o los nombres y el o los apellidos del demandante, pero si es una empresa o persona jurídica solo debes sacar la razón social *** ###

### **nombresPersonaDemandante**
Extrae el o los **nombres** se refiere a o los nombres demandante o el que solicita el embargo. 

Si esEntidadJudicial = Sí, extraer los nombres del demandante desde:

Ubica esta información en las siguientes secciones del documento:

- **Encabezado**: Cerca del título del documento.  
- **Cuerpo**: En la sección donde se identifican las partes involucradas en el proceso.

Si esEntidadJudicial = No, el demandante no tendrá nombres.  

### **apellidosPersonaDemandante**
Extrae el o los **apellidos** se refiere a o los apellidos demandante o el que solicita el embargo. 

Si esEntidadJudicial = Sí, extraer los apellidos del demandante desde:

Ubica esta información en las siguientes secciones del documento:

- **Encabezado**: Cerca del título del documento.  
- **Cuerpo**: En la sección donde se identifican las partes involucradas en el proceso.

Si esEntidadJudicial = No, el demandante no tendra apellidos.   
---

### **NombreEmpresaDemandante**
Extrae la **razón social** se refiere al nombre de la empresa demandante o el que solicita el embargo. 

Si esEntidadJudicial = Sí, extraer los apellidos del demandante desde:

Ubica esta información en las siguientes secciones del documento:

- **Encabezado**: Cerca del título del documento.  
- **Cuerpo**: En la sección donde se identifican las partes involucradas en el proceso.

Ejemplo de Extracción
Entrada en el documento
REFERENCIA: 
Demandante: Banco de Bogotá S.A.  
Demandado: Yonathan Michel Ruiz Aragón c.c. 1.005.838.302 

Salida Esperada
{
  "NombreEmpresaDemandante": "Banco de Bogotá S.A."
}

Si esEntidadJudicial = No, el demandante no tendrá apellidos.   
---


### **TipoEntidadRemitente**
Determina si el demandante pertenece a una autoridad judicial o a un proceso coactivo.  

Si cumple con alguna de estas condiciones, asigna:

- Judicial si el documento menciona términos como: **Juzgado, Proceso Civil, Proceso Penal** o si está firmado por un juez.  
- Coactiva si aparecen términos como: **cobro coactivo, resolución administrativa, ejecución fiscal**.  
- Otro si no se cumplen las condiciones anteriores.

---

### **correoElectronicoDelDemandante**
Extrae el correo electrónico oficial del demandante, asegurando que pertenezca a la entidad o persona natural que solicita el embargo.

Reglas de Extracción
Debe ser un correo institucional o corporativo:

Dominios oficiales: @empresa.com, @entidad.org, @demandante.gov.co.
Ubicación en el documento:

Cuerpo: En secciones como "Contacto del demandante", "Notificaciones al demandante".
Firmas: Junto a la firma del representante del demandante.
Si hay múltiples correos en el documento:

Priorizar el que esté vinculado con el demandante, no con la entidad emisora.
Ejemplo de Extracción
Entrada en el documento
"El demandante GASES DE OCCIDENTE S.A. E.S.P. podrá ser contactado a través de demandas@gasesdeoccidente.com."

Salida Esperada

{
  "correoElectronicoDelDemandante": "demandas@gasesdeoccidente.com"
}

---

### **direccionFisicaDelDemandante**
Extrae la dirección física del demandante, asegurando que pertenezca a la persona natural o jurídica que solicita el embargo.

Reglas de Extracción
Debe incluir elementos típicos de una dirección:

Calle, Carrera, Avenida, No., Piso, Oficina, Código Postal, Ciudad.
Ubicación en el documento:

Cuerpo: En secciones donde se mencione la dirección del demandante.
Firmas: Junto a los datos del demandante o su representante legal.
Si hay varias direcciones en el documento:

Extraer solo la dirección del demandante, no la de la entidad emisora.
Ejemplo de Extracción
Entrada en el documento
"El demandante GASES DE OCCIDENTE S.A. E.S.P. tiene su sede en Carrera 15 No. 23 - 45, Cali, Valle del Cauca."

Salida Esperada

{
  "direccionFisicaDelDemandante": "Carrera 15 No. 23 - 45, Cali, Valle del Cauca"
}

---

### **ciudadDelDemandante**
Extrae la **ciudad** desde donde se emite el documento.  

Busca en:

- **Encabezado**: Junto al nombre o dirección de la entidad.  
- **Dirección física**: Parte de la dirección de la entidad remitente.  
- **Cuerpo o firmas**: Menciones explícitas en estas secciones.  

---

### **DepartamentoDelDemandante**
Extrae el **departamento** desde donde se emite el documento.  

Busca en:

- **Encabezado**: Junto al nombre o dirección de la entidad.  
- **Dirección física**: Parte de la dirección de la entidad remitente.  
- **Cuerpo o firmas**: Menciones explícitas en estas secciones.  

---

### **telefonoDelDemandante**
Extrae el **número de teléfono** relacionado al demandante.','"nombresPersonaDemandante": "Andres Camilo",
"apellidosPersonaDemandante": "Gonzales Restrepo",
"NombreEmpresaDemandante" : "Trycore SAS",
"tipoIdentificacionDelDemandante": "CC",
"numeroIdentificacionDelDemandante": "900876578",
"ciudadDelDemandante": "Medellin",
"DepartamentoDelDemandante": "Antioquia",
"correoElectronicoDelDemandante": "helmer@gmail.com",
"direccionFisicaDelDemandante": "Calle 123",
"telefonoDelDemandante": "3123456789",',NULL,NULL),
	 ('DEMANDADOS','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','
- **demandados**: # **Extracción y Estructuración de Demandados en Documentos de Embargo y Desembargo**

Este documento establece las reglas para extraer y estructurar la información de TODOS los demandados (personas a las que se les embargan o desembargan cuentas) mencionados en un documentosin desesntimar a ninguno, pueden estar muy cerca de los demandantes o de los destinatarios del oficio pero no los debes confundir.  

Identifica la sección del documento donde se menciona la información del proceso judicial, en especial el apartado de los demandados.
Extrae los nombres completos y números de identificación (NIT o Cédula de Ciudadanía) de todos los demandados listados en el documento.
Organiza los datos en una estructura JSON, asegurándote de que cada demandado tenga su propio objeto con sus respectivos datos.
No infieras información ni omitas datos. Extrae únicamente lo que esté explícitamente escrito en el documento.

Ten cuenta que van a estar delante de la descripcion DEMANDADOS o en una lista en frente, debes garantizar de extraer todos y no confundilos con los demas actores del oficio, estos pueden ser personas naturales o personas jurídicas.

### **tipoIdentificacion**
- Extrae el tipo de identificación del demandado según el documento.
- Busca menciones explícitas de los siguientes tipos:
  - **CC**: Cédula de Ciudadanía
  - **NIT**: Número de Identificación Tributaria
  - **CE**: Cédula de Extranjería
  - **TI**: Tarjeta de Identidad
  - **PA**: Pasaporte
  - **NITE**: NIT de Persona Extranjera
  - **PPT**: Permiso por Protección Temporal
  
---

### **numeroIdentificacion**
- Extrae el número de identificación del demandado tal como aparece en el documento.
- Este número debe estar relacionado con los siguientes tipos de identificación: **CC, NIT, PA, TI, CE, NITE**.

---

### **nombreApellidosRazonSocial**
- Extrae el nombre completo del demandado o la razón social si es una persona jurídica.
- Busca en las siguientes secciones:
  - **Encabezado**: Generalmente en las primeras líneas del documento.
  - **Cuerpo**: Donde se identifican las partes del proceso.
  - **Firmas**: En listados o en secciones finales.

---

Analiza el documento y extrae todas las cuantías embargadas, retenidas o involucradas en medidas cautelares.

*** Criterios de búsqueda y extracción:

** Detección de expresiones clave:

Busca frases como:
- “LIMÍTESE el embargo a la suma de”
- “Se ordena el embargo de”
- “Retención previa de los dineros”
- “Embargo sobre cuentas bancarias”
- “Monto embargado”
- “Medida cautelar sobre”
- “Monto a retener”
- “Cuantía de la medida cautelar”
- “Embargo y retención de”

** Formato numérico correcto:

- Separadores de miles: Usa . (Ejemplo: 5.429.448).
- Separadores decimales: Usa , (Ejemplo: 10,50).
- Corrección de decimales incompletos:
- Si el número tiene un solo decimal (,1, ,2, ,3, etc.), convertirlo a dos dígitos (,10, ,20, ,30)
- Ejemplo: 5.429.448,1 → 5.429.448,10 | 3.250.000,4 → 3.250.000,40.
- Si el número no tiene decimales, agregar ,00.

** Ubicación esperada:

- Secciones relacionadas con medidas cautelares, embargos, resoluciones judiciales y montos retenidos.
- Estructura de salida esperada:
- Extrae todas las cuantías detectadas en el documento, listadas con el tipo de medida cautelar correspondiente.

** Ejemplos de salida:
Si el documento contiene:
"LIMÍTESE el embargo a la suma de $5’429.448,1 pesos"
Debe devolver:
✅ "cuantiaEmbargada": "5.429.448,10"

Si el documento contiene:
"Embargo de $3.250.000,4 sobre cuentas bancarias y retención de $1’500.000,3"
Debe devolver:
✅ "cuantiasEmbargadas": ["3.250.000,40", "1.500.000,30"]

Si el documento contiene valores sin decimales:
"Embargo de $2.000.000"
Debe devolver:
✅ "cuantiaEmbargada": "2.000.000,00"

---

### **resolucionesRadicadosNumerosReferenciasDemandado**
La extracción debe realizarse en el orden de prioridad indicado, asegurando que se seleccionen los identificadores más específicos y relevantes.

Lee el documento y detecta todos los campos relevantes relacioandos al demandado, tales como nombres, fechas, identificadores, direcciones, montos, tablas, subtítulos, firmas y cualquier otro campo presente en el documento.
Proporciona un listado completo de todos los campos identificados para asegurar una extracción completa.
Genera una estructura JSON con los campos identificados, organizando la información de manera clara.
Reglas para la extracción
Extrae solo la información literal contenida en el documento, sin inferencias.
No omitas ningún campo.
Si un campo no puede identificarse claramente, se marcará como null en la estructura JSON.
Si hay datos tabulares, organízalos en listas o matrices.

Números de Resolución Judicial (23 dígitos)
Identificadores de Procesos Coactivos
Otros identificadores administrativos o institucionales

Tipos de Identificadores a Extraer
1. Identificadores Judiciales (23 Dig)

*. Número de proceso
Número de proceso judicial (23 dígitos)
Número de radicado, rad o radicacion
Número de expediente
Referencia de proceso ejecutivo
*. Proceso laboral
*. Proceso ejecutivo
*. Radicado
*. Radicación
*. Expediente
*. Ref Ejecutivo
*. No

2. Identificadores Coactivos y Administrativos

Debes identificarlas en el siguiente orden

1- Resolución
2- Número Proceso / Proceso No.
3- Número Mandamiento de Pago / Mandamiento / MPC
4- Número Expediente / Expediente No. / EXP
5- Número Radicado / Radicado No.
6- Número Auto de Cobro
7- Número Comparendo /  Comparendo No.
8- Número Placa  / Placa No.
9- Número Contrato / No. Contrato /  Contrato
10- Número Proceso de Responsabilidad Fiscal / PRF No.
11- Consecutivo
12- Referencia de Pago
13- Referencia de Ejecución
14- Vigencia
15- Industria
16- Cédula Catastral
17- Matrícula Catastral
Radicación
Número de resolución administrativa
Número de mandamiento de pago
Número de expediente coactivo
Número de auto de cobro
Referencia de ejecución
Números de comparendo
Placas de vehículos (formato: XXX000 o XXX00X)
Referencias catastrales
Números de contrato
Números de proceso de responsabilidad fiscal
Matrículas inmobiliarias
Consecutivos institucionales

Reglas de Extracción
Priorización

Buscar primero en encabezado y sección de referencias, en los cuadros de relacion
Priorizar el identificador más específico y completo
En caso de múltiples identificadores, extraer el más relevante según contexto

#### **Extracción del Número**
- Extrae la secuencia numérica relacionada a la resolución identificada en el documento.

#### **Reglas de Extracción**
- Los números de resolución se extraen y almacenan en dos niveles:
  1. **A nivel general** dentro de las resoluciones de la medida cautelar.
  2. **A nivel individual** dentro de cada demandado.

#### **Casos Especiales**
- Si el documento no contiene un número de resolución judicial explícito, **valida si el documento proviene de una entidad coactiva**.
- Si el documento no es de origen coactivo, deja el campo vacío (`    `).

#### **Formato Esperado**
- **Resolución Judicial**: Suelen ser **23 caracteres numéricos**.
- **Resolución Coactiva**: Generalmente es una combinación de números y, en algunos casos, letras.
- Si existen múltiples resoluciones en el documento, extrae la principal, generalmente ubicada en la sección de referencia o en el encabezado del oficio.
- Si no se encuentra un número de resolución relacionado con el demandado, deja el campo vacío (`    `).

---

## **Instrucciones Adicionales**
### **Múltiples Demandados**
- Si el documento menciona varios demandados, **debes extraer los datos de cada uno de manera individual**.
- Cada demandado debe representarse como un registro independiente.
','"demandados": [
        {
            "nombre": "Juan Camilo Gonzales Restrepo",
            "identificacion": "1023894454",
            "tipoIdentificacion": "CC",
            "cuantiaEmbargadaOValor": "100.000,00",
            "resolucionesRadicadosNumerosReferenciasDemandado": ["7897-45"]
        }
 ],',NULL,NULL),
	 ('ENTIDAD','Extrae la información siguiendo esta estructura de ejemplo. Conserva la estructura fielmente, los valores son unicamente de ejemplo para especificar el tipo de dato evita tomar estos valores como predeterminados.','
Identificación de la Entidad Emisora

** Nombre de la Entidad Emisora (nombreEntidadEmisora)

Extrae el nombre de la entidad que emite el documento.

Prioriza el nombre que aparezca en:

Encabezado del documento.

Pie de página con información institucional.

Firma del documento (validando que sea un funcionario institucional).

Referencias normativas o radicados que indiquen la entidad responsable.

** esEntidadJudicial **

Determina si la entidad emisora (nombreEntidadEmisora) pertenece al sistema judicial.
Reglas de clasificación:
Si la entidad es un Juzgado, Tribunal, Corte o Fiscalía → Asignar "Sí"

Asignar "Sí" si la entidad pertenece al sistema judicial y contiene explícitamente uno de los siguientes términos:
"Juzgado"
"Tribunal"
"Corte"
"Fiscalía"
"Consejo de la Judicatura"
"Sala Penal"
"Sala Civil"
"Proceso Penal"

Reglas de extraccion:
Evitar falsos positivos: La clasificación debe basarse en la literalidad exacta del nombre.
Evitar coincidencias parciales si no incluyen explícitamente un término judicial válido.

Ejemplos de entidades judiciales válidas:
"Juzgado 15 Penal del Circuito"
"Tribunal Administrativo de Cundinamarca"
"Corte Suprema de Justicia"
"Fiscalía General de la Nación"
"Consejo de la Judicatura"

Salida esperada: "Sí"

Si no pertenece al sistema judicial, asignar "No"

Ejemplos de entidades que NO deben ser consideradas judiciales:
"Superintendencia de Industria y Comercio"
"Ministerio de Hacienda"
"Alcaldía de Medellín"

** Datos de la Entidad

tipoIdentificacionEntidad: Extrae el tipo de identificación de la entidad emisora si está presente. Puede ser:

NIT: Número de Identificación Tributaria.

NITE: NIT de Persona Extranjera.

NITP: NIT de Persona Natural.

CC: Cédula de Ciudadanía (en caso de personas naturales emisoras).

CE: Cédula de Extranjería.

TI: Tarjeta de Identidad.

PA: Pasaporte.

numeroIdentificacionEntidad: Extrae el número de identificación asociado al tipo de identificación extraído previamente.

tipoEntidad: Determina si la entidad es:

"Judicial": Si esEntidadJudicial = Sí.

"Coactivo con Impuestos": Si la entidad es Gobernación, Alcaldía, DIAN, Hacienda, SENA, Dirección de Impuestos.

"Coactivo": Si la entidad es una Contraloría.

entidadRemitente: Extrae el nombre de la entidad emisora según:

Encabezado del documento.

Pie de página con información institucional.

Firma del documento (validando que sea un funcionario institucional).

Referencias normativas o radicados que indiquen la entidad responsable.

correoElectronicoEntidadRemitente: Extrae el correo electrónico oficial de la entidad emisora del documento, asegurando que sea un contacto institucional válido.

Reglas de Extracción
Debe ser un correo institucional:

Dominios oficiales: @entidad.gov.co, @empresa.com, @institucion.org.
Ubicación en el documento:

Encabezado: Junto al logo o datos de contacto de la entidad emisora.
Cuerpo: En secciones como "Para mayor información", "Comuníquese con".
Firmas: Junto a la firma del funcionario que representa a la entidad.
Si hay múltiples correos en el documento:

Priorizar el que esté vinculado con la entidad emisora.
No extraer correos del demandante ni de terceros.
Ejemplo de Extracción
Entrada en el documento
"Para consultas adicionales, comuníquese con juzgado1@ramajudicial.gov.co."

Salida Esperada

{
  "correoElectronicoEntidadEmisora": "juzgado1@ramajudicial.gov.co"
}

direccionFisicaEntidadRemitente: Extrae la dirección física de la entidad emisora del documento, asegurando que corresponda únicamente a la entidad que genera el oficio.

Reglas de Extracción
Debe incluir elementos típicos de una dirección:

Calle, Carrera, Avenida, No., Piso, Oficina, Código Postal, Ciudad.
Ubicación en el documento:

Encabezado: Junto al logo o nombre de la entidad emisora.
Cuerpo: En secciones donde se indique la ubicación para recepción de documentos.
Firmas: Junto a los datos de contacto del funcionario que representa la entidad.
Si hay varias direcciones en el documento:

Extraer solo la dirección de la entidad emisora, no la del demandante o terceros.
Ejemplo de Extracción
Entrada en el documento
"JUZGADO PRIMERO DE PEQUEÑAS CAUSAS Y COMPETENCIA MÚLTIPLE
Calle 57 No. 44 – 22, Casa de Justicia, Palmira, Valle del Cauca."

Salida Esperada

{
  "direccionFisicaEntidadEmisora": "Calle 57 No. 44 – 22, Casa de Justicia, Palmira, Valle del Cauca"
}

ciudadDepartamentoEntidadRemitente: Extrae la ciudad y departamento de la entidad emisora.

telefonoEntidadRemitente: Extrae el teléfono de contacto de la entidad emisora.

** Clasificación de la Entidad (esEntidadJudicial)

Determina si la entidad emisora es un juzgado, tribunal o fiscalía:

Si nombreEntidadEmisora contiene "Juzgado", "Tribunal", "Corte", "Fiscalía", asignar Sí.

Si no, asignar No.

- **claseDeposito**: Clasifica el tipo de depósito según la entidad remitente.

Judicial : Igual a la clasificacion anterior esEntidadJudicial

Coactivo con Impuestos : Si el nombre de la entidad remitente  es una governación, alcaldia ,sena , dirección de impuestos, dian , hacienda, departamento administrativo establec Coactivo con impuestos .

Coactivo : Si el nombre de la entidad remitente es alguna Contraloría, retornar  Coactivo .

### **actualizacionCuentaDepositoJudicial**: debes identificar en el documento hallar alguna frase completa

#### Frases a tener en cuenta:
- Se notifica que el depósito ha sido modificado.
- Se informa sobre la actualización del depósito.
- Se comunica el cambio en el depósito.
- Se reporta una modificación en el depósito.
- Se avisa que el depósito ha sido ajustado.

en caso de encontrar alguna frase completa debes establecer true en caso contrario establece false

### **cambioCorreo**: identifica en el documento si existe una mencion explicita de un cambio en el correo electronico

### Reglas de extraccion para el campo cambio correo:

debes buscar en el documento si se hay exactamente alguna de las siguientes frases para poder extraer el correo cambiado

- Se notifica una actualización en el correo electrónico del destinatario
- Se comunica un cambio en la dirección de correo
- Se informa sobre la modificación del correo
- Se indica un cambio en la cuenta de correo
- Se notifica una actualización en el correo electrónico de la entidad
- Se informa un cambio en la dirección de correo de la entidad
- Se comunica una modificación en el correo institucional de la entidad

Resultados: En cuanto encuentres una de las frases debes extraer el correo que se menciona despues de la frase

Razonamiento: evita inferir, debes seguir al pie de la letra las Reglas de extraccion para el campo cambioCorreo

','"entidadRemitente": "Ministerio de Justicia",
"telefonoEntidadRemitente": "3123456789",
"TipoEntidadRemitente": "Judicial",  
"ciudadEntidadRemitente": "Popayán",
"DepartamentoEntidadRemitente": "Cauca",
"correoElectronicoEntidadRemitente": "",
"direccionFisicaEntidadRemitente": "",
"tipoIdentificacionEntidad": "NIT",
"numeroIdentificacionEntidad": "900867950",
"cambioCorreo": "Cuando en el documento se informe un cambio en el correo electronico se debe establecer el nuevo correo aqui. Ejemplo correo@direccion.co",
"enElDocumentoSeMencionaAlgunaActualizacionEnElCorreo": "Booleano que identifica si se Cambio de correo. Ejemplo true",
"actualizacionCuentaDepositoJudicial": "Establecer el nuemero de cuenta actualizada segun si se encontro alguna frase. Ejemplo: 66857483365",',NULL,NULL),
	 ('OFICIO','Se te proporcionará el texto de un oficio de embargo o desembargo. Tu tarea es extraer la información relevante y estructurarla en formato JSON, siguiendo el esquema y las instrucciones que se detallan a continuación.

Instrucciones:

Analiza detenidamente el texto del oficio de embargo o desembargo proporcionado. Es crucial que analices el contexto completo del documento, incluyendo la sección de antecedentes, la descripción de la medida cautelar y cualquier otra sección relevante, para determinar con precisión quiénes son los demandantes y demandados.
Extrae la información relevante para cada uno de los campos especificados en el esquema JSON. Presta especial atención a la identificación de los demandantes y demandados, utilizando los términos clave y las reglas de diferenciación que se describen a continuación.
Devuelve la información extraída en formato JSON, siguiendo estrictamente la estructura y los ejemplos que se muestran a continuación.
Prioriza la precisión y exhaustividad al extraer la información.
En caso de duda sobre cómo interpretar la información, incluye la frase relevante del texto del oficio en el valor del campo, junto con tu interpretación.
Reglas de diferenciación:   ','Tu tarea es extraer información de documentos de embargo y desembargo siguiendo las siguientes reglas de extracción. Asegúrate de que cada metadato se extraiga de manera fiel y sin inferencias. Si un dato no está presente, debe marcarse como vacío ("").

Aquí están las reglas de extracción:

Reglas de diferenciación:

Demandante: La parte que inicia el proceso legal. Se puede identificar con términos como "DEMANDANTE:", "quien solicita la medida", "presentado por", "interpuesto por", "a favor de", "en representación de", "en calidad de", "ejecutante", etc.
Demandado: La persona o entidad contra la cual se interpone la demanda. Se puede identificar con términos como "DEMANDADO:", "contra", "en contra de", "a quien se le impone la medida", "ejecutado", etc.

 Ejemplo de identificacion
  
    DEMANDANTE:         BANCOLOMBIA S.A  NIT.890.903.938-8 
    DEMANDADO:          CONSORCIO CAVARA S.A.S NIT.900.423.217-1 
                        JORGE ELIECER RAMIREZ ESPITIA C.C. 17.310.828 
                        ELIZABETH GUTIERREZ TORREJANO C.C. 41.530.844

Para este caso el demandand es BANCOLOMBIA y los demas seria demandados.

Casos especiales:

Procesos coactivos: Si el proceso es coactivo, el demandante y la entidad emisora son la misma.
Múltiples nombres: Si hay múltiples demandantes o demandados, extraer cada nombre por separado.
Información ambigua: Si la información no está claramente delimitada, utilizar el contexto y las reglas de diferenciación para determinar la información correcta.
Instrucciones detalladas
Ubica la Entidad emisora

Se encuentra al inicio del documento.
Generalmente es un juzgado, una entidad gubernamental o una entidad de cobro coactivo.
Extrae su nombre completo, dirección y correo electrónico.
Identifica los Destinatarios del Oficio

Son las entidades (bancos, empresas financieras) que deben cumplir con la medida.
Se listan después de la introducción del oficio.
Extrae todos los nombres de bancos o entidades mencionadas.
Determina el Demandante

Es quien interpone la acción judicial.
Se menciona en la sección de “Referencia” o “Proceso”.
Extrae su nombre y número de identificación (NIT o C.C.).
Si el proceso es coactivo, el demandante será la misma entidad emisora.
Extrae los Demandados

Son quienes enfrentan la acción legal.
Se listan junto con su número de identificación.
Puede haber uno o varios demandados.
Extrae nombre y número de identificación.
Diferenciación en procesos coactivos

Si el tipo de proceso es “Coactivo”, el demandante y la entidad emisora serán la misma.
En este caso, asegúrate de que no haya confusión en la clasificación de roles.

- **numOficio**: Extrae el número único del oficio. Generalmente se encuentra en:

Encabezado: Junto al título Oficio No. o similares.
Primeras líneas del cuerpo: Mencionado como parte de la introducción o referencia del documento.
Ejemplo de formatos válidos:

Oficio No. 12345-AB-2024.
OFICIO No. 100
Oficio 6789/2023.

**fechaRecepcionDocumento**: Extrae la fecha de recepcion del documento, dandole prioridad al sello que pueda tener, búscalo en las partes superiores o inferiores del documento del mismo, independientemente del formato en que la encuentres haz un re-formateo en formato dd/mm/yyyy (por ejemplo, 15/08/2024)

**horaRecepcionDocumento**: Extrae la hora de recepcion del documento, dandole prioridad al sello que pueda tener, búscalo cerca a la fecha de recepcion en las partes superiores o inferiores del documento del mismo, independientemente del formato en que la encuentres haz un re-formateo en formato hh:mm aa (Por ejemplo, 02:45 PM)

- **firmaOficio**: Analiza el siguiente documento y determina si contiene una firma válida. Considera los siguientes criterios:

Firma Manuscrita: Rúbrica o trazo distintivo realizado a mano al final del documento, que indica la conformidad del autor. Incluye firmas ilegibles, abreviadas, con ornamentos, o que combinen elementos de texto y trazo. La firma puede estar acompañada del nombre del firmante, pero debe haber un trazo manuscrito reconocible.
Firma Electrónica: Firma digital con certificados digitales válidos, firmas escaneadas con indicación clara de origen electrónico (por ejemplo, un texto que diga "Firmado digitalmente" junto a la imagen), o firmas generadas mediante plataformas de firma digital. Incluye expresiones como "Firmado electrónicamente", "Firma digital certificada", iconos de certificados (que sean claramente visibles en el documento), o un código de verificación que permita validar la firma en línea.
Ubicación: La firma debe estar ubicada en la sección final del documento, después del último párrafo de contenido principal y antes de cualquier información de contacto o detalles de producción (como "PROYECTO:" o información de la oficina).
Ausencia de Firma: El documento no presenta ningún trazo manuscrito, ni indicación de firma electrónica. Se consideran ausencia de firma: sellos, iniciales aisladas (sin trazo manuscrito completo), nombres mecanografiados o impresos sin trazo manuscrito o indicación electrónica, o la presencia de información de contacto al final del documento sin una firma clara.
Es fundamental diferenciar entre un nombre escrito a máquina y una firma manuscrita. Un nombre escrito a máquina no se considera una firma.

En caso de duda sobre si un trazo es una firma, priorizar la interpretación como "NO". Si hay elementos tanto de firma como de no firma, justificar la decisión tomada.

El documento es un comunicado oficial. Las firmas en estos documentos suelen tener un formato claro.

Retorna "Firma Manuscrita", "Firma Electrónica", o "NO".

### **existeCorreoElectronicoDeSolicitud** ###
Valida si en el documento viene un correo electronico donde solicite, autorice, pida, requiera que se realice el proceso judicial o coactivo,  retorna si o no, ten en cuenta que este debe tener un remitente un asunto y un destinatario que deberia ser el juzgado o la entidad

- **CuentaBancariaDepositoRecursosEmbargados**: Extrae el NUMERO de cuenta relacionado con la entidad bancaria que emite el embargo:
Se debe extraer la cuenta a donde se va a depositar el embargo de los productos, Verifica que el número esté relacionado con el embargo en cuestión, ESTE DEBE SER UN CAMPO NUMERICO.

- **tipoEmbargo**: Determina el tipo de embargo basándote en las menciones del documento:

Congelado: Si aparecen términos como Congelado, Divorcio, Separación, Proceso de alimentos, o si el nombre del juzgado incluye la palabra Familia.
Normal: Si no se cumplen las condiciones anteriores.
no tengas encuenta mayusculas o minisculas.

- **tipoMedidaCautelar**: Clasifica el tipo de medida cautelar mencionada en el documento:

Extrae y clasifica el tipo de medida cautelar mencionada en el documento, asegurando que sea interpretada correctamente según su contexto.

Reglas de Clasificación
Embargo 🛑

Si el documento menciona términos como:
"Retención", "Decreto de medida cautelar", "Embargo", "Reténgase", "Secuestro", "Afectación de bienes"
También puede estar acompañado de términos como "inmovilización" o "orden de embargo" en contexto legal, y no ser enceuntra primero alguna de las sigueintes palabras que indican un desembargo, 

Desembargo ✅

Si el documento menciona expresiones como:
"Desembargo", "Levantamiento", "Terminación", "Desistimiento", "Decreto a terminación", "Cancelación", "Liberación de fondos"
También incluir si hay una orden clara de "poner fin a la medida cautelar".

Otro ❓

Ejemplo de Extracción
Entrada en el documento
"14 de noviembre de 2024 se ordenó la TERMINACIÓN POR DESISTIMIENTO TÁCITO, 
en consecuencia, se dispone la CANCELACIÓN, de las medidas de EMBARGO y 
RETENCIÓN de los dineros que el demandado JAIRO ENRIQUE RODRIGUEZ 
GUERRERO,"

Salida Esperada

{
  "tipoMedidaCautelar": "Desembargo"
}

Si no se encuentran términos relacionados con embargo o desembargo, o si la medida cautelar no se puede clasificar dentro de estas categorías.
Si el documento habla de medidas preventivas sin referencia a embargo/desembargo, marcar como "Otro".

### **esSolicitudDeInformacion**

Revisa el documento proporcionado y determina si se trata de una solicitud de información. Si el documento cumple con los criterios de una solicitud de información, devuelve una llave con valor booleano true. De lo contrario, devuelve false.

Criterios para una Solicitud de Información:
El documento se considera una solicitud de información si:
El asunto o el cuerpo del documento menciona términos como:

"Solicitud de información".
"Confirmación de cuentas bancarias".
"Información de cuentas".
"Requerimiento de datos".

El propósito del documento es recopilar datos o confirmar información de cuentas bancarias.

No se está ejecutando ninguna acción legal o medida cautelar en el momento de la solicitud.

Formato de Salida Esperado:
La respuesta debe ser en formato JSON, con una única llave llamada esSolicitudDeInformacion y un valor booleano (true o false).

Ejemplo de salida:
{
  "esSolicitudDeInformacion": true
}

Ejemplo de Análisis:
Entrada en el documento:
"ASUNTO: SOLICITUD DE INFORMACIÓN DE CUENTAS BANCARIAS. De manera atenta, me permito solicitar la confirmación de las cuentas bancarias de las personas dentro del proceso de cobro coactivo."
Salida Esperada:

{
  "esSolicitudDeInformacion": true
}

Entrada en el documento:
"Se ordena el embargo de las cuentas bancarias a nombre de los contraventores mencionados."
Salida Esperada:
{
  "esSolicitudDeInformacion": false
}
Revisa el documento proporcionado y determina si se trata de una solicitud de información. Devuelve la respuesta en formato JSON, utilizando la llave esSolicitudDeInformacion con un valor booleano (true o false).

## **elDocumentoEsUnCorreoElectronico**: identifica si el documento es un correo electronico.

###Reglas para el campo elDocumentoEsUnCorreoElectronico:

1. Para identificar si el documento es un correo electronico debes asegurarte que el documento tenga todas las expresiones que se mencionaran a continuacion:

"De:" (en el contexto de remitente)
"Para:" (en el contexto del destinatario)
"Asunto:"

2. opcionalmente puedes encontrar que en el documento se mencionan adjuntos
3. si llegas a encontrar en el documento exactamente la expresion "este correo" (sin distingur mayusculas o minusculas) establece "SI"

Ejemplo:

1. De: davivienda@davivienda.com
   Para: Bancolombia
   Asunto: Embargos
   
Resultado del ejemplo 1 = SI

2. se especifica que para el demandado WILLIAM PEÑA se le limita la cuantia a una suma de: 4000000

Resultado del ejemplo 2 = NO

3. En caso de no tener productos con su entidad, hacer caso omiso a este correo.

Resultado del ejemplo 3 = SI

4. JUZGADO SEGUNDO PROMISCUO DE BOGOTA = NO

####Casos especiales: Si en el documento llegas a ver entidades juzgados, numeros de oficio o numeros de radicado debes establecer NO

####Resultado: cuando identifiques que el documento es un correo electronico debes establecer "SI", de lo contrario "NO"

###Razonamiento; evita inferir y sigue todas las reglas establecidas para este campo al pie de la letra

### **cuantiaEmbargada**
- Extrae la cuantía exacta embargada al demandado o de la medida cautelar, que puede expresarse en términos monetarios o porcentuales.
- **Ejemplo de valores monetarios**: `$1.000.000`, `$10,000.50`
- Busca en las secciones donde se describen las disposiciones del embargo o en tablas de resumen.
---

- **AfectarCuentaNomina**: Determina si el documento contiene una instrucción explícita para afectar o no una cuenta nómina. Retorna  Sí o  No  si no se cumple o no

Para determinar si la condición se cumple, busca la presencia de las siguientes palabras clave o combinaciones (sin distinción de mayúsculas/minúsculas) en el contexto del embargo o desembargo:

Palabras clave:  nómina ,  salario ,  sueldo ,  remuneración ,  pago ,  ingresos salariales,  cuenta nómina ,  cuenta de salarios ,  remuneraciones, honorarios.

Verbos de prohibición:  absténgase ,  abstenerse ,  no afectar ,  prohíbase ,  no se debe afectar ,  no embargar ,  excluir ,  exceptuar .

Reglas:

Co-ocurrencia: Se requiere la co-ocurrencia de al menos una palabra clave relacionada con  nómina  y un verbo de prohibición dentro de la misma oración o párrafo, en el contexto del embargo o desembargo.

Contexto: La mención debe estar en el contexto del embargo o desembargo para que se considere válida. Menciones aisladas en otros párrafos no se consideran relevantes.

Salida: Si se encuentra una combinación válida de palabras clave y verbos de prohibición en el contexto del embargo o desembargo, retorna  Sí . Si no se encuentran estas combinaciones, retorna  No . Si no hay información sobre este asunto en el documento, retorna   .

Ejemplo:

La frase  Se debe abstener de afectar la cuenta nómina del demandado  retornaría  Sí . La frase  El demandado tiene una cuenta de nómina  retornaría  No

- **afectaAlgunCDT**: Si en el documento se menciona dentro de los productos que debe afectar alguno como CDT, CDAT o Certificado de Depósito a Término establecer SI de lo contrario NO

- **elDemandadoTieneMultas**: Donde se impuso multa ,  Plazo otorgado para el pago de la multa impuesta ,  En el sentido de imponerle como multa... Busca si el demandado esta multado, no confundas el demandado con el receptor del oficio.

ADVERTIR que la multa deberá depositarse

- **elDemandadoTieneSanciones**: Donde se impuso sancion,  Plazo otorgado para el pago de la sancionimpuesta ,  En el sentido de imponerle como sancion... 

Sanciones	donde se impuso multa / El plazo otorgado para el pago de la multa impuesta
Sanciones	En el sentido de imponerle como multa 

- **elDemandadoTieneReiteraciones**: Busca palabras o frases relacionadas con la repetición de una medida, como reiterar, repetir, reincidencia, nuevamente, de nuevo, otra vez, insistir,aplicación de la medida,medida reiterada. También considera la presencia de las tipologías proporcionadas relacionadas con reiteraciones de medidas.

Reiteraciones	Reiterar la inscripción de la medida
Reiteraciones	le requiere dar aplicación a la medida de embargo comunicada en el oficio anterior xxxx
Reiteraciones	Requerir con caracter urgente 
Reiteraciones	"PRIMERO: REQUERIR a los gerentes (...) para que en caso de existir dineros de la ejecutada

- **elDemandadoTieneIncidenteDeDesacato**: Busca palabras o frases relacionadas con la apertura de un incidente o proceso sancionatorio, como incidente,sancionatorio, proceso, judicial,orden judicial,desacato,incumplimiento a orden judicial, apertura de incidente. También considera la presencia de las tipologías proporcionadas relacionadas con incidentes de desacato.

 Incidente de desacato, Apertura de incidente sancionatorio, Abrir tramite incidental por desacato, Aperturar incidente por desacato,Abrir tramite incidental con miras a la aplicación de sanciones , Ordenar la apertura del incidente por incumplimiento, Requiere, en forma previa a la apertura de incidente de desacato, Aperturar el incidente ante la omisión de respuesta, Iniciar incidente de sanción, Incidente de desacato contra..., Sancionar con la suma..., Inicio al presente incidente sancionatorio.

Incidente de desacato	ABRIR TRAMITE INCIDENTAL POR DESACATO A ORDEN JUDICIAL
Incidente de desacato	APERTURAR INCIDENTE POR DESACATO A ORDEN JUDICIAL CONTA BANCO DAVIVIENDA SA.
Incidente de desacato	ABRIR TRAMITE INCIDENTAL CON MIRAS A LA APLICACIÓN DE LAS SANCIONES
Incidente de desacato	ORDENAR LA APERTURA DEL INCIDENTE POR INCUMPLIMIENTO A ORDEN JUDICIAL
Incidente de desacato	REQUIERE, EN FORMA PREVIA A LA APERTURA DE INCIDENTE DE DESACATO
Incidente de desacato	APERTURAR EL INCIDENTE ANTE LA OMISIÓN DE RESPUESTA
Incidente de desacato	INICIAR INCIDENTE DE SANCION
Incidente de desacato	INCIDENTE DE DESACATO CONTRA EL BANCO DAVIVIENDA
Incidente de desacato	SANCIONAR CON LA SUMA
Incidente de desacato	INICIO AL PRESENTE INCIDENTE SANCIONATORIO

- **elDemandadoTieneReiteraciones**:  Reiterar la inscripción de la medida ,  Requiere dar aplicación a la medida de embargo comunicada... ,  Requerir con carácter urgente ,  Requerir a... para que en caso de existir dineros... susceptibles de la Medida Cautelar decretada .

Responsabilidad solidaria	SE VINCULA COMO DEUDOR SOLIDARIO
Responsabilidad solidaria	Responsabilidad Solidaria

-**elDemandadoMencionaPorcentaje**: Revisa las siguientes frases

Terceras partes	Embargo y secuestro de (1/3) parte de las sumas de dinero
Terceras partes	embargo de la tercera parte de los ingresos depositados
Terceras partes	embargo y retencion de la 1/3 parte de los dineros
Terceras partes	embargo y retencion de la tercera parte 1/3 de los dineros
Terceras partes	se embargue y retenga el 42% de los recursos

Reglas:

Contexto: Las palabras clave o tipologías deben aparecer en el contexto del embargo o desembargo. Menciones aisladas en otros párrafos no se consideran válidas.

Combinaciones: La presencia de al menos una palabra clave o tipología de cada grup

- **bancoCuentaDeposito**: El campo bancoCuentaDeposito debe determinarse en el documento. Se debe asignar el nombre del banco correspondiente o un valor vacío en los siguientes casos:

Identificación del banco

Extraer el nombre del banco mencionado en el documento, específicamente en la sección donde se indica la cuenta de depósito.
El banco debe ser registrado exactamente como aparece en el documento, sin abreviaciones ni modificaciones.

Si el documento menciona una cuenta de depósito sin especificar el nombre del banco, no se debe asumir el banco y el campo debe enviarse vacío.
Si el documento menciona múltiples bancos, se debe listar solo el banco relacionado con la cuenta de depósito afectada.

## **destinatariosOficio**
###Objetivo: Identificar y extraer ÚNICAMENTE los destinatarios mencionados en la sección inicial del oficio.
Reglas para el campo destinatariosOficio:

1. Analiza SOLO la parte inicial del documento, después del encabezado, fecha y número de oficio, pero ANTES del cuerpo principal del texto.
Busca específicamente secciones que típicamente introducen destinatarios como:

"Señor Gerente:"
"Señores:"
"Señor:"
"A:"
"Para:"

2. Extrae los correos electronicos o entidades que aparezcan inmediatamente después de estos marcadores mencionados anteriormente.

4. En caso de encontrar alguna de las siguientes cadenas de texto añades a la lista de destinatarios:

"USUARIO DAVIVIENDA"
"FONDO DE INVERSION DAVIVIENDA"
"TITULOS DE VALOR CAPITALIZACION DAVIVIENDA"

Formato de salida: Devuelve una lista de los destinatarios encontrados únicamente en la sección inicial.

### **elDocumentoIncluyesolicitudProductoDeudores**: debes identificar en el documento hallas alguna frase completa, en caso de encontrar alguna frase explicita debes establecer "SI" la que encontraste, en caso contrario "NO"

#### Frases que debes tener en cuenta
- Solicitamos un listado de los productos de los deudores
- Pedimos que se nos facilite un inventario de los productos del deudores
- Solicitamos que se nos informe sobre los productos del deudores
- Pedimos el registro de los productos del deudores

## **cuantiaLetras**: Extrae el numero de cuantia en letras que se halle en el oficio

Reglas de extraccion para el campo cuantiaLetras:

###1.Debes identificar cuando se este hablando sobre la cuantia, para eso debes buscar en el oficio las siguientes frases
"Limítese la medida a la suma de"
"Restringir la medida a la cantidad de"
"Establecer el límite de la medida en"
"Fijar la medida hasta la suma de"
"Reducir la medida a un total de"
"Aplicar la medida únicamente a la cantidad de"
"Delimitar la medida a un monto de"

###2.Una vez que halles por lo menos una frase debes identificar si despues de la frase hallada se encuentra el numero de cuantia en letras
###3.Ejemplo:
Limítese la medida a la suma de SESENTA Y SIETE MIL QUINIENTOS MILLONES SEISCIENTOS CUARENTA Y OCHO MIL NOVECIENTOS CUARENTA Y NUEVE PESOS (67.500.648.949) = "SESENTA Y SIETE MIL QUINIENTOS MILLONES SEISCIENTOS CUARENTA Y OCHO MIL NOVECIENTOS CUARENTA Y NUEVE PESOS"
Reducir la medida
 a un total de CUARENTA MILLONES SEISCIENTOS NOVENTA Y NUEVE MIL (40.699.000) = "CUARENTA MILLONES SEISCIENTOS NOVENTA Y NUEVE MIL"

realizar la validacion de comparación de la cuantía en letras y numerica (si se encuentra, de lo contrario, se devuelve un valor vacío o nulo).
en caso de que la cuantía en letras sea diferente a la cuantía numerica debe establecer true, en caso contrario establece false

## **existeNuevaCuantia**
### Objetivo: Analizar el texto de un oficio legal para determinar si contiene información sobre una modificación en la cuantía o nuevo límite de embargo.

###Reglas para el campo existeNuevaCuantia:
Busca en el texto completo del oficio cualquiera de las siguientes frases:
"el nuevo limite del embargo es la suma de"
"la nueva restricción del embargo es"
"el reciente tope del embargo es"
"la nueva frontera del embargo es"
"el límite actualizado del embargo es"
"la nueva barrera del embargo es"
"el nuevo umbral del embargo es"
"se modifica la cuantía del embargo a"
"se establece como nueva cuantía"
"se fija nuevo valor de embargo"

- La búsqueda debe ser insensible a mayúsculas/minúsculas y debe considerar variaciones en acentos.

Resultado: Devuelve exactamente "true" si encuentras al menos una coincidencia. Devuelve "false" en caso contrario.
Razonamiento: Evita inferir, segue al pie de la letra cada una de las reglas mencionadas para el campo existeNuevaCuantia

Ejemplos:

"Por medio del presente se notifica que el nuevo limite del embargo es la suma de $50,000 pesos" → true
"Se mantiene el límite previamente establecido para el embargo" → false
"El límite actualizado del embargo es de veinte mil pesos" → true
"el nuevo limite del embargo es la suma de $3050.117.04" → true
"la nueva frontera del embargo es la suma de $3050.117.04" → true

##**"elDocumentoCumpleExactamenteLasReglasDeIdentificacionRemanente"**: para este campo debes determinar si en el documento se identifica explicitamente las frases que se mencionaran mas adelante en las reglas para este campo

1. Regla de Identificación
Determina si en el documento aparece EXACTAMENTE alguna de estas frases:

"Desembargar y colocar el remanente a favor de"
"desembargue la medida y déjela a disposición del Juzgado"
"desembargue la medida y déjela a disposición de la DIAN"
"desembargue la medida y déjela a disposición del proceso"
"Levante la medida y deja a disposición de"
"el Juzgado X dejó a nuestra disposición el embargo que recae sobre la cta No"
"embargo del Remanente"
"embargo de Remanente"


3.Ejemplos para validación:


-"remanentes fiduciarios" = false
-"Levante la medida y deja a disposición de WILLIAM ALFONZO MARQUEZ SIERRA" = true
-"donde comunica el decreto de embargo del REMANENTE" = true

2. Casos especiales a tener muy en cuenta:

En caso de que encuentres "remanentes fiduciarios" debes establecer false

Reglas adicionales:

Busca ÚNICAMENTE las frases exactas listadas.
No interpretes ni infierás y sigue estrictamente estas reglas.


Valor a retornar

Si encuentras EXACTAMENTE alguna de las frases anteriores → retorna "SI"
En CUALQUIER otro caso → retorna "NO"

## **existeOficioAuto**: Si en el documento encuentras alguna de estas palabras exacatas como ```Auto```, ```Autos``` o ```Auto resoluciones``` establecer true, de lo contrario false

## **esMencionadoEnElDocumentoComoPagador**

Objetivo:
Identificar si el documento designa explícitamente a una entidad como "Pagador" o "Pagadora", especialmente en el contexto del destinatario del oficio o en las referencias iniciales del documento.

Reglas de Búsqueda:

Buscar las frases exactas:
"Pagador [Nombre de la Entidad Bancaria]"
"Pagadora [Nombre de la Entidad Bancaria]"

Estas frases deben buscarse principalmente en:
La sección del destinatario del oficio (donde se indica a quién va dirigido).
La sección de "Referencia" o "REF" del documento, donde se resume el tema.

Reglas Adicionales para Evitar Falsos Positivos:

La designación de "Pagador" o "Pagadora" debe ser explícita y referirse a la entidad responsable de realizar un pago específico o relacionada con el proceso legal descrito en el documento.
No considerar como "Pagador" o "Pagadora" las menciones de entidades financieras (como bancos) a menos que se les designe directamente como tal en las secciones especificadas (destinatario o referencia).
Si la mención de la entidad es solo dentro del cuerpo del documento, sin la designación explícita como "Pagador" en el destinatario o referencia, devolver false.

Ejemplo de Extracción (Positivo):

Entrada en el documento (Destinatario):
"Señores:\n   Pagador DAVIVIENDA S.A."
Salida Esperada:
JSON
{
  "esMencionadoEnElDocumentoComoPagador": true
}


Ejemplo de Extracción (Negativo - Caso del Documento):

Entrada en el documento (Destinatario):
"Señor gerente:\n   BANCO FALABELLA S.A., DE BOGOTÁ, DAVIVIENDA S.A. y DAVIPLATA"
Salida Esperada:
JSON
{
  "esMencionadoEnElDocumentoComoPagador": false
}

Reglas de Extracción:

Exactitud: Solo las frases exactas y su ubicación (destinatario o referencia) son relevantes.
Resultado binario:
Si la frase exacta se encuentra en el destinatario o referencia, y designa explícitamente a una entidad como pagador, devolver true.
En cualquier otro caso, devolver false.


Razonamiento:

Enfoque en la designación formal: Priorizar la identificación de "Pagador" o "Pagadora" en las secciones donde se designa formalmente a la entidad en un contexto legal.
Contexto específico: Limitar la búsqueda al destinatario y la referencia para mayor precisión.

Formato de Salida:

JSON
{
  "esMencionadoEnElDocumentoComoPagador": true/false
}


## **esMencionadoEnElDocumentoComoEmpleadoOTrabajador**:

### Objetivo:
Identificar si el documento menciona explícitamente a una persona como "Empleado", "Empleada", "Trabajador" o "Trabajadora".

### Reglas de Búsqueda:
Debes buscar en el documento las siguientes cadenas de texto de manera exacta y explícita:

"Empleado"
"Empleada"
"Trabajador"
"Trabajadora"


### Ejemplo de Extracción:
Entrada en el documento: "La demanda es contra el Empleado [Nombre del Empleado]."
Salida Esperada:
JSON
{
  "esMencionadoEnElDocumentoComoEmpleadoOTrabajador": true
}



### Reglas de Extracción:

Exactitud: Solo las frases exactas mencionadas en las reglas de búsqueda cuentan. No se deben inferir o interpretar frases similares.
Resultado binario:
Si el documento contiene alguna de las frases exactas, devuelve true.
Si el documento no contiene ninguna de las frases exactas, devuelve false.



### Razonamiento:

Búsqueda exacta: Las frases deben coincidir exactamente con las proporcionadas en las reglas de búsqueda. No se permiten variantes ni inferencias.
Evitar intuición: No interpretes frases similares o contextos que no cumplan con las reglas exactas.


### Formato de Salida:
La salida debe ser un JSON con el siguiente formato:

JSON
{
  "esMencionadoEnElDocumentoComoEmpleadoOTrabajador": true
}

true: Si el documento contiene alguna de las frases exactas.
false: Si el documento no contiene ninguna de las frases exactas.

## **elUnicoProductoFinancierEnElDocumentoEsDerechosEconomicos**
###Objetivo: Determinar si en el oficio ÚNICAMENTE se mencionan derechos económicos o acciones como productos financieros, sin ningún otro tipo de bien.
Reglas para el campo elUnicoProductoFinancierEnElDocumentoEsDerechosEconomicos:

Examina el texto completo del oficio buscando menciones de cualquier tipo de producto financiero o bien.
Identifica específicamente menciones de las siguientes cadenas de texto:

"Derechos economicos"
"Leasing habitacional"
"Contrato de leasing"
"Derechos de leasing"
"Derechos del contrato de Leasing"

Verifica si se mencionan OTROS productos financieros o bienes diferentes a derechos económicos o acciones, como inmuebles, vehículos, cuentas bancarias, etc.
Regla de decisión:

Si el oficio SOLO menciona alguna cadena de texto de la como productos financieros → devuelve "true"
Si el oficio menciona cualquier otro tipo de bien ADEMÁS DE o EN LUGAR DE derechos económicos o acciones → devuelve "false"

Ejemplos:

1. Juzgado decretó el EMBARGO y RETENCIÓN DE LOS DINEROS de derechos economicos = true
2. Este despacho judicial decreto el embargo y retención de Leasing habitacional = true
3. Decretar el embargo y retencion de Precio de arrendamiento, Derechos del contrato de Leasing y cualquier otro producto financiero que llegase a tener = false
4. embargo y retencion de los dineros en monto de arrendamiento, derechos economicos = false
5. Se declara el embargo y retencion de Contrato de leasing del demandado = true

Razonamiento: evita inferir a la hora de hacer la verificacion, sigue al pie de la letra las reglas del campo elUnicoProductoFinancierEnElDocumentoEsDerechosEconomicos.

## **enElDocumentoSeMencionaAlgunaActualizacionEnElCorreo**

### Objetivo: Determinar si un documento contiene información sobre un cambio o actualización de correo electrónico, utilizando frases específicas como indicadores.
Reglas para el campo:

Analiza el documento completo buscando EXACTAMENTE alguna de las siguientes frases (sin variaciones):

"Se notifica una actualización en el correo electrónico del destinatario"
"Se comunica un cambio en la dirección de correo"
"Se informa sobre la modificación del correo"
"Se indica un cambio en la cuenta de correo"
"Se notifica una actualización en el correo electrónico de la entidad"
"Se informa un cambio en la dirección de correo de la entidad"
"Se comunica una modificación en el correo institucional de la entidad"


Reglas estrictas de coincidencia:

No considerar variaciones, sinónimos o paráfrasis de estas frases
Las frases deben aparecer completas en el documento
No interpretar el significado o intención del documento; solo buscar las frases exactas


Sistema de decisión:

Si se encuentra AL MENOS UNA de estas frases exactas → Devuelve "true"
Si NO se encuentra NINGUNA de estas frases exactas → Devuelve "false"


Prioridad de procesamiento:

Solo después de verificar todas las frases sin encontrar coincidencias, devuelve "false"



Ejemplos:

"En este documento se notifica una actualización en el correo electrónico del destinatario" → true
"Se informa sobre la modificación del correo a partir del próximo mes" → true
"El juzgado comunica un cambio en la información de contacto" → false (no coincide exactamente)

## **enElDocumentoSoloMencionaElProductoCanonArrendamiento**: debes identificar que en el documento solo este el producto canon de arrendamiento

Reglas para el campo enElDocumentoSoloMencionaElProductoCanonArrendamiento:

debes verificar que cuando se haga mencion de los productos solo mencione alguna de las siguientes cadenas de texto:

"Canon de arrendamiento"
"Monto de arrendamiento"
"Precio de arrendamiento"

Resultados: en caso de que el unico producto mencionado sea alguna de las cadenas de texto establecer true, en caso contrario false

Ejemplos:

1. Juzgado decretó el EMBARGO y RETENCIÓN DE LOS DINEROS que por cualquier concepto, Canones de arrendamiento, productos financieros, Carteras colectivas, cdt o fondos de inversion = false
2. Este despacho judicial decreto el embargo y retención de los montos de arrendamiento = true
3. Decretar el embargo y retencion de Precio de arrendamiento, cdt, y cualquier otro producto financiero que llegase a tener = false
4. embargo y retencion de los dineros en monto de arrendamiento, derechos economicos = false
5. Se declara el embargo y retencion de Canon de arrendamiento del demandado = true

##**cuantosOficiosDiferentesHayEnElDocumento**:
Objetivo: Identificar y contar el número de oficios distintos que aparecen en un documento.
Instrucciones precisas:

Analiza el documento completo buscando indicadores de oficios diferentes, como:

Números de oficio (ej. "Oficio No. 123", "Oficio Nro. 456")
Encabezados de oficios distintos
Fechas de emisión diferentes
Remitentes o emisores distintos
Cambios en formato o estilo que indiquen un nuevo oficio


Criterios para identificar oficios diferentes:

Cada oficio suele tener su propio número único de identificación
Los oficios generalmente tienen una fecha de emisión
Cada oficio tiene un remitente o emisor específico
Los oficios suelen tener un asunto o tema particular
Pueden existir separadores claros entre oficios (líneas, saltos de página, etc.)


Proceso de conteo:

Identifica cada oficio único en el documento
Cuenta solo una vez cada oficio aunque aparezca mencionado múltiples veces
Si un oficio está adjunto o referenciado pero no incluido en el documento, no debe contarse
Si hay copias del mismo oficio, cuentan como un solo oficio


Resultado:

Devuelve una cadena de texto con el numero que representa la cantidad de oficios diferentes encontrados


Verificación:

Para cada oficio identificado, extrae su número o identificador único
Verifica que realmente sean oficios diferentes y no referencias al mismo oficio



Ejemplos:

Si el documento contiene "Oficio No. 123" y luego "Oficio No. 456" → 2
Si el documento contiene múltiples referencias a "Oficio No. 123" pero ningún otro → 1
Si el documento contiene un oficio principal y menciona otros oficios pero no los incluye → 1
Si el documento es un compilado de tres oficios diferentes cada uno con su propio número → 3

## **correoDestinatariosOficio**: debes identificar todos los correos de los destinatarios en el oficio

Reglas de extraccion del campo correoDestinatariosOficio: 
1.Identifica el correo de destinatario despues de las siguientes palabras

"Señores"
"Para"

2.los correos de los destinatarios pueden llegar a estar entre los mismos destinatarios

3.Ejemplo:

Para: notificacionesjudiciales@davivienda.com = ["notificacionesjudiciales@davivienda.com"]

Señores: BANCO BBVA - correonotificaciones@bancobbva.com BANCO DAVIVIENDA = ["correonotificaciones@bancobbva.com"]

3.Resultados: debes extraer todos los correos de los destinatarios en una lista

4.Razonamiento: debes evitar inferir, sigue todas las reglas del campo correoDestinatariosOficio al pie de la letra

','"estaFirmadoElDocumento": false,
"esJuzgadoElRemitente": false,
"numeroOficio": "1234-85",
"afectaAlgunCDT": true,
"BancoCuentaDepositoEmbargo": "Banco Agrario",
"CuentaBancariaDepositoRecursosEmbargados": "5228-72042001",
"elDemandadoMencionaPorcentaje": true,
"elDemandadoTieneResponsabilidadSolidaria": true,
"elDemandadoTieneIncidenteDeDesacato": true,
"elDemandadoTieneReiteraciones": true,
"elDemandadoTieneSanciones": true,
"elDemandadoTieneMultas": true,
"afectarLaCuentaDeNominaDelDemandado": true,
"elDocumentoEnElTextoIncluyeLaPalabraCongelado": true,
"elDocumentoEnElTextoIncluyeLaPalabraDivorcio": true,
"elDocumentoEnElTextoIncluyeLaPalabraSeparacion": true,
"elDocumentoEnElTextoIncluyeLaPalabraProcesoDeAlimentos": true,
"elDocumentoEnElTextoIncluyeLaPalabraFamilia": true,
"tipoMedidaCautelar": "Embargo",
"esSolicitudDeInformacion": true,
"elDocumentoEsUnCorreoElectronico": "SI",
"fechaRecepcionDocumento": "01/01/2025",
"horaRecepcionDocumento": "2:32 PM",
"existeCorreoElectronicoDeSolicitud": false,
"cuantiaEmbargadaOficio": "12.500.000",
"destinatariosOficio": ["BANCO DAVIVIENDA", "BANCOLOMBIA"],
"elDocumentoIncluyeSolicitudProductoDeudores": "indica si en el documento cual frase se encontro",
"cuantiaLetras": "Cuantia en el que el valor sera en letras. Ejemplo: Cuarenta y seis mil millones",
"existeNuevaCuantia": true,
"elDocumentoCumpleConLasReglasDeIdentificacionRemanente":  "NO",
"esMencionadoEnElDocumentoComoPagador": true,
"esMencionadoEnElDocumentoComoEmpleadoOTrabajador": true,
"elUnicoProductoFinancierEnElDocumentoEsDerechosEconomicos": "Booleano que indica si el unico producto que se menciona en el oficio es derechos economicos o acciones. Ejemplo: true",
"enElDocumentoSoloMencionaElProductoCanonArrendamiento": "Booleano que indica si en el documento solo hay 1 producto y que ese producto se llame canon de arrenamiento. Ejemplo true",
"cuantosOficiosDiferentesHayEnElDocumento": "Numero de oficios en un documento. Ejemplo: "3"",
"correoDestinatariosOficio": "Correos de los destinatarios: ["correodestinatario@gmail.com"]"
',NULL,NULL);
