import PyPDF2

def validar_pdf(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        numero_paginas = len(lector.pages)
        if numero_paginas > 0:
            return True  # El PDF es válido y tiene al menos una página
        else:
            return False  # El PDF no tiene páginas
    except Exception as e:
        return False  # Ocurrió un error, el PDF puede estar corrupto
