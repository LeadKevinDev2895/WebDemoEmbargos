import enum
from enum import Enum as PyEnum

class TipoEntidad(enum.Enum):
    JUDICIAL = "JUDICIAL"
    COACTIVA = "COACTIVA"
    OTRA = "OTRA"

    _alias = {
        OTRA : "OTRO",
        COACTIVA : "COACTIVO"
    }

    def alias(self):
        """Devuelve el alias si existe, de lo contrario el valor original."""
        return self._alias.get(self.value, self.value)

class TipoEmbargo(enum.Enum):
    CONGELADO = "CONGELADO"
    NORMAL = "NORMAL"

class ClaseDeposito(enum.Enum):
    ENTE_COACTIVO = "ENTE COACTIVO"
    ENTE_COACTIVO_POR_COBRO_DE_IMPUESTOS = "ENTE COACTIVO POR COBRO DE IMPUESTOS"
    DEPOSITO_JUDICIAL = "DEPOSITO JUDICIAL"
    OTRA = "OTRA"

    # _alias = {
    #     COACTIVO_IMPUESTOS: "COACTIVO CON IMPUESTOS",
    #     COACTIVO: "COACTIVA"
    # }

    # def alias(self):
    #     """Devuelve el alias si existe, de lo contrario el valor original."""
    #     return self._alias.get(self.value, self.value)

class TipoMedida(enum.Enum):
    EMBARGO = "EMBARGO"
    DESEMBARGO = "DESEMBARGO"
    REQUERIMIENTO = "REQUERIMIENTO"
    OTRO = "OTRO"

class TipoIdentificacion(enum.Enum):
    CC = "CC"
    CE = "CE"
    NIT = "NIT"
    TI = "TI"
    PA = "PA"
    NITE = "NITE"
    NITP = "NITP"
    DESCONOCIDO = "DESCONOCIDO"

    _alias = {
        CC: "C.C"
    }

    def alias(self):
        """Devuelve el alias si existe, de lo contrario el valor original."""
        return self._alias.get(self.value, self.value)
    
    
class EstadoProceso(enum.Enum):
    DESGARGADO = "Descargado"
    PENDIENTE = "Pendiente"
    ANEXADO = "Anexado"
    EXITOSO = "Exitoso"

class TipoDocumento(enum.Enum):
    WORD = "WORD"
    EXCEL = "EXCEL"
    PDF = "PDF"
    IMAGEN = "IMAGEN"
    DESCONOCIDO = "DESCONOCIDO"

class TipoProcesamiento(enum.Enum):
    OFICIO = "OFICIO"
    REPORTE = "REPORTE"
    ANEXO_PDF = "ANEXO_PDF"
    ANEXO_EXCEL = "ANEXO_EXCEL"

class Novedades(enum.Enum):    
    REITERACION = "Reiteraciones"
    INICIO_PROCESO = "Inicio o apertura del proceso"
    SANCIONES = "Incidentes sancionatorios"
    RESPONSABILIDAD = "Responsabilidad solidaria"
