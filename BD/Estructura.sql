--
-- PostgreSQL database dump
--

-- Dumped from database version 17.3 (Debian 17.3-3.pgdg120+1)
-- Dumped by pg_dump version 17.3 (Debian 17.3-3.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: rpa_trycore
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO rpa_trycore;

--
-- Name: clasedeposito; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.clasedeposito AS ENUM (
    'ENTE_COACTIVO',
    'ENTE_COACTIVO_POR_COBRO_DE_IMPUESTOS',
    'DEPOSITO_JUDICIAL',
    'OTRA'
);


ALTER TYPE public.clasedeposito OWNER TO rpa_trycore;

--
-- Name: tipodocumento; Type: TYPE ; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipodocumento AS ENUM (
    'WORD',
    'EXCEL',
    'PDF',
    'IMAGEN',
    'DESCONOCIDO'
);


ALTER TYPE public.tipodocumento OWNER TO rpa_trycore;

--
-- Name: tipoembargo; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipoembargo AS ENUM (
    'CONGELADO',
    'NORMAL'
);


ALTER TYPE public.tipoembargo OWNER TO rpa_trycore;

--
-- Name: tipoentidad; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipoentidad AS ENUM (
    'JUDICIAL',
    'COACTIVA',
    'OTRA',
    '_alias'
);


ALTER TYPE public.tipoentidad OWNER TO rpa_trycore;

--
-- Name: tipoidentificacion; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipoidentificacion AS ENUM (
    'CC',
    'CE',
    'NIT',
    'TI',
    'PA',
    'NITE',
    'NITP',
    'DESCONOCIDO',
    '_alias'
);


ALTER TYPE public.tipoidentificacion OWNER TO rpa_trycore;

--
-- Name: tipomedida; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipomedida AS ENUM (
    'EMBARGO',
    'DESEMBARGO',
    'REQUERIMIENTO',
    'OTRO'
);


ALTER TYPE public.tipomedida OWNER TO rpa_trycore;

--
-- Name: tipoprocesamiento; Type: TYPE; Schema: public; Owner: rpa_trycore
--

CREATE TYPE public.tipoprocesamiento AS ENUM (
    'SIMPLE',
    'COMPLEJO_EXCEL',
    'COMPLEJO_PDF',
    'REPORTE'
);


ALTER TYPE public.tipoprocesamiento OWNER TO rpa_trycore;

--
-- Name: actualizar_relaciones_documentos(); Type: FUNCTION; Schema: public; Owner: rpa_trycore
--

-- DROP FUNCTION public.eliminar_tipificaciones(int4);

CREATE OR REPLACE FUNCTION public.eliminar_tipificaciones(p_doc_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    medida_id_var INT;
BEGIN
    -- Obtener la medida asociada al documento
    SELECT "medida_id" INTO medida_id_var FROM "Documento" WHERE id = p_doc_id;

    -- Si no hay medida_id, salir
    IF medida_id_var IS NULL THEN
        RETURN;
    END IF;

    -- Eliminar relaciones de muchos a muchos en MedidaMotivo
    DELETE FROM "MedidaMotivo" WHERE "medidaId" = medida_id_var;

    -- Marcar documento como 'Procesado'
    UPDATE "Documento" SET "estadoProceso" = 'Procesado' WHERE id = p_doc_id;

END;
$function$
;

-- DROP FUNCTION public.reprocesar_tipificaciones();

CREATE OR REPLACE FUNCTION public.reprocesar_tipificaciones()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    doc_id INT;
BEGIN
    FOR doc_id IN (SELECT id FROM "Documento" WHERE "estadoProceso" = 'Retipificacion') LOOP

        -- Eliminar relaciones del documento
        PERFORM eliminar_tipificaciones(doc_id);

    END LOOP;
END;
$function$
;


-- DROP FUNCTION public.actualizar_relaciones_documentos();

CREATE OR REPLACE FUNCTION public.actualizar_relaciones_documentos()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    WITH archivos_base AS (
        SELECT
            id,
            "rutaDocumento",
            regexp_replace(split_part("rutaDocumento", '\', -1), '[A-Z]?\.[a-zA-Z]+$', '') AS nombre_base
        FROM public."Documento"
    ),
    padres AS (
        SELECT
            id AS id_padre,
            nombre_base
        FROM archivos_base
        WHERE NOT split_part("rutaDocumento", '\', -1) ~ '[A-Z]\.[a-zA-Z]+$'
    ),
    hijos AS (
        SELECT
            hijos.id AS id_hijo,
            padres.id_padre
        FROM archivos_base hijos
        JOIN padres
        ON hijos.nombre_base = padres.nombre_base
        WHERE split_part(hijos."rutaDocumento", '\', -1) ~ '[A-Z]\.[a-zA-Z]+$'
    )
    UPDATE public."Documento"
    SET "idPadre" = hijos.id_padre
    FROM hijos
    WHERE public."Documento".id = hijos.id_hijo;
END;
$function$
;



ALTER FUNCTION public.actualizar_relaciones_documentos() OWNER TO rpa_trycore;

--
-- Name: eliminar_relaciones_documento(integer); Type: FUNCTION; Schema: public; Owner: rpa_trycore
--

CREATE OR REPLACE FUNCTION public.eliminar_relaciones_documento(p_doc_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    medida_id_var INT;
    demandante_id_var INT;
    demandado_id_var INT;
    resolucion_id_var INT;
    producto_id_var INT;
    tiene_demandante_not_null BOOLEAN;
BEGIN
    -- Obtener la medida asociada al documento
    SELECT "medida_id" INTO medida_id_var FROM "Documento" WHERE id = p_doc_id;

    -- Si no hay medida_id, actualizar estado a 'Pendiente' y salir
    IF medida_id_var IS NULL THEN
        UPDATE "Documento" SET "estadoProceso" = 'Pendiente' WHERE id = p_doc_id;
        RETURN;
    END IF;

    -- Desvincular la medida del documento
    UPDATE "Documento" SET "medida_id" = NULL WHERE "medida_id" = medida_id_var;

    -- Obtener demandante asociado a la medida
    SELECT "demandante_id" INTO demandante_id_var FROM "MedidaCautelar" WHERE id = medida_id_var;

    -- Verificar si la columna "demandante_id" permite valores NULL
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'MedidaCautelar'
        AND column_name = 'demandante_id'
        AND is_nullable = 'NO'
    ) INTO tiene_demandante_not_null;

    -- Eliminar resoluciones asociadas
    FOR resolucion_id_var IN (SELECT id FROM "Resolucion" WHERE "medida_id" = medida_id_var) LOOP
        DELETE FROM "Resolucion" WHERE id = resolucion_id_var;
    END LOOP;

    -- Eliminar productos asociados
    FOR producto_id_var IN (SELECT id FROM "Producto" WHERE "medida_id" = medida_id_var) LOOP
        DELETE FROM "Producto" WHERE id = producto_id_var;
    END LOOP;

    -- Eliminar demandados asociados
    FOR demandado_id_var IN (SELECT id FROM "Demandado" WHERE "medida_id" = medida_id_var) LOOP
        DELETE FROM "Producto" WHERE "demandado_id" = demandado_id_var;
        DELETE FROM "Resolucion" WHERE "demandado_id" = demandado_id_var;

        -- Si el demandado no tiene más relaciones, eliminarlo
        IF NOT EXISTS (SELECT 1 FROM "Demandado" WHERE id = demandado_id_var AND "medida_id" != medida_id_var) THEN
            DELETE FROM "Demandado" WHERE id = demandado_id_var;
        ELSE
            -- Si tiene otras relaciones, solo desvincularlo de esta medida
            UPDATE "Demandado" SET "medida_id" = NULL WHERE id = demandado_id_var;
        END IF;
    END LOOP;

    -- Eliminar relaciones de muchos a muchos en MedidaMotivo
    DELETE FROM "MedidaMotivo" WHERE "medidaId" = medida_id_var;

    -- Si el demandante no tiene más medidas asociadas, eliminarlo
    IF demandante_id_var IS NOT NULL THEN
        IF (SELECT COUNT(*) FROM "MedidaCautelar" WHERE "demandante_id" = demandante_id_var) = 1 THEN
            DELETE FROM "MedidaCautelar" WHERE id = medida_id_var;
            DELETE FROM "Demandante" WHERE id = demandante_id_var;
        ELSE
            -- Si la columna permite NULL, desvincularlo
            IF NOT tiene_demandante_not_null THEN
                UPDATE "MedidaCautelar" SET "demandante_id" = NULL WHERE id = medida_id_var;
            END IF;
        END IF;
    END IF;

    -- Si no hay más documentos asociados a la medida, eliminarla
    IF NOT EXISTS (SELECT 1 FROM "Documento" WHERE "medida_id" = medida_id_var) THEN
        DELETE FROM "MedidaCautelar" WHERE id = medida_id_var;
    END IF;

    -- Marcar documento como 'Pendiente'
    UPDATE "Documento" SET "estadoProceso" = 'Pendiente' WHERE id = p_doc_id;

    -- Eliminar relación padre-hijo en "Documento" y actualizar estado de hijos
    UPDATE "Documento" 
    SET "idPadre" = NULL, "estadoProceso" = 'Pendiente' 
    WHERE "idPadre" = p_doc_id;

END;
$function$
;


ALTER FUNCTION public.eliminar_relaciones_documento(p_doc_id integer) OWNER TO rpa_trycore;

CREATE OR REPLACE FUNCTION public.eliminar_registros_reporte(doc_corte text)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    DELETE FROM "ReporteCruce"
    WHERE "corte" = doc_corte;
END;
$function$
;

ALTER FUNCTION public.eliminar_registros_reporte(doc_corte text) OWNER TO rpa_trycore;

--
-- Name: reprocesar_documentos(); Type: FUNCTION; Schema: public; Owner: rpa_trycore
--

CREATE OR REPLACE FUNCTION public.reprocesar_documentos()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    doc_id INT;
    doc_tipo_procesamiento TEXT;
    doc_corte TEXT;
BEGIN
    FOR doc_id IN (SELECT id FROM "Documento" WHERE "estadoProceso" = 'Reprocesamiento') LOOP
        -- Obtener tipoProcesamiento y corte del documento
        SELECT "tipoProcesamiento", "corte"
        INTO doc_tipo_procesamiento, doc_corte
        FROM "Documento"
        WHERE id = doc_id;

        -- Si el tipoProcesamiento es 'REPORTE', eliminar registros en ReporteCruce
        IF doc_tipo_procesamiento = 'REPORTE' THEN
            PERFORM eliminar_registros_reporte(doc_corte);
        END IF;

        -- Eliminar relaciones del documento
        PERFORM eliminar_relaciones_documento(doc_id);

        -- Actualizar relaciones después de la eliminación
        PERFORM actualizar_relaciones_documentos();
    END LOOP;
END;
$function$
;

ALTER FUNCTION public.reprocesar_documentos() OWNER TO rpa_trycore;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Demandado; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Demandado" (
    id integer NOT NULL,
    "tipoIdentificacion" public.tipoidentificacion,
    "numeroIdentificacion" character varying,
    dv character varying,
    "nombreApellidosRazonSocial" character varying,
    "cuantiaEmbargada" character varying,
    "cuantiaLetras" character varying,
    "embargoConLimite" boolean,
    medida_id integer,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Demandado" OWNER TO rpa_trycore;

--
-- Name: Demandado_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Demandado_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Demandado_id_seq" OWNER TO rpa_trycore;

--
-- Name: Demandado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Demandado_id_seq" OWNED BY public."Demandado".id;


--
-- Name: Demandante; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Demandante" (
    id integer NOT NULL,
    "tipoIdentificacion" public.tipoidentificacion,
    "numeroIdentificacion" character varying,
    dv integer,
    nombre character varying,
    apellido character varying,
    "razonSocial" character varying,
    "correoElectronico" character varying,
    "direccionFisica" character varying,
    "ciudadDepartamento" character varying,
    telefono character varying,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Demandante" OWNER TO rpa_trycore;

--
-- Name: Demandante_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Demandante_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Demandante_id_seq" OWNER TO rpa_trycore;

--
-- Name: Demandante_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Demandante_id_seq" OWNED BY public."Demandante".id;


--
-- Name: Documento; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Documento" (
    id integer NOT NULL,
    "fechaRecepcion" character varying,
    "rutaDocumento" character varying,
    "rutaDocumentoConvertido" character varying,
    "tipoDocumento" public.tipodocumento,
    "hashDocumento" character varying,
    "tipoProcesamiento" public.tipoprocesamiento,
    "estadoOficio" character varying,
    "estadoProceso" character varying,
    "motivoNovedad" character varying,
    "idPadre" integer,
    corte character varying NOT NULL,
    "cantidadPaginas" integer,
    medida_id integer,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Documento" OWNER TO rpa_trycore;

--
-- Name: Documento_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Documento_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Documento_id_seq" OWNER TO rpa_trycore;

--
-- Name: Documento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Documento_id_seq" OWNED BY public."Documento".id;


--
-- Name: Entidad; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Entidad" (
    id integer NOT NULL,
    "tipoIdentificacionEntidad" public.tipoidentificacion,
    "numeroIdentificacionEntidad" character varying,
    "tipoEntidad" public.tipoentidad,
    entidad character varying,
    "correoElectronicoEntidad" character varying,
    "direccionFisicaEntidad" character varying,
    "ciudadDepartamentoEntidad" character varying,
    "telefonoEntidad" character varying,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Entidad" OWNER TO rpa_trycore;

--
-- Name: Entidad_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Entidad_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Entidad_id_seq" OWNER TO rpa_trycore;

--
-- Name: Entidad_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Entidad_id_seq" OWNED BY public."Entidad".id;


--
-- Name: MedidaCautelar; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."MedidaCautelar" (
    id integer NOT NULL,
    demandante_id integer NOT NULL,
    entidad_id integer NOT NULL,
    "numeroCarteroWeb" character varying,
    "numeroIq" character varying,
    "cuentaEnte" character varying,
    "numeroOficio" character varying,
    "firmaOficio" boolean,
    "correoOrigen" boolean,
    "bancoCuentaDeposito" character varying,
    "tipoEmbargo" public.tipoembargo,
    "claseDeposito" public.clasedeposito,
    "tipoMedida" public.tipomedida,
    "noAfectarCuentaNomina" boolean,
    "afectarCdt" boolean,
    "multasSancionesReiteraciones" boolean,
    "tercerasPartes" boolean,
    "asociacionProductoEspecifico" boolean,
    "codDespachoJudicial" character varying,
    "annoRadicadoJudicial" character varying,
    "consAsignadoJudicial" character varying,
    "codInstanciaJudicial" character varying,
    incluir boolean,
    "removerCuantia" boolean,
    "solicitudProductosDeudores" boolean,
    "cambioCorreo" character varying,
    "existeNuevoCorreo" boolean,
    "cambioCuentaEnte" boolean,
    "existeNuevaCuantia" boolean,
    "cuantiaEnLetras" character varying,
    "procesoRemanante" boolean,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone,
    "destinatariosOficio" character varying,
    "existeOficioAuto" boolean,
    "imagenOficioEmbargo" boolean,
    "existeDerechosEconomicos" boolean,
    "canonArrendamiento" boolean,
    "numeroOficios" character varying,
    "correoDestinatariosOficio" character varying,
    "esCorreoElectronico" boolean
);


ALTER TABLE public."MedidaCautelar" OWNER TO rpa_trycore;

--
-- Name: MedidaCautelar_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."MedidaCautelar_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."MedidaCautelar_id_seq" OWNER TO rpa_trycore;

--
-- Name: MedidaCautelar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."MedidaCautelar_id_seq" OWNED BY public."MedidaCautelar".id;


--
-- Name: MedidaMotivo; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."MedidaMotivo" (
    "medidaId" integer NOT NULL,
    "motivoId" integer NOT NULL,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."MedidaMotivo" OWNER TO rpa_trycore;

--
-- Name: Motivos; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Motivos" (
    id integer NOT NULL,
    nombre character varying NOT NULL,
    etapa character varying NOT NULL,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Motivos" OWNER TO rpa_trycore;

--
-- Name: Motivos_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Motivos_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Motivos_id_seq" OWNER TO rpa_trycore;

--
-- Name: Motivos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Motivos_id_seq" OWNED BY public."Motivos".id;


--
-- Name: Parametros; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Parametros" (
    id integer NOT NULL,
    "ramaPadre" character varying,
    llave character varying NOT NULL,
    valor character varying,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Parametros" OWNER TO rpa_trycore;

--
-- Name: Parametros_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Parametros_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Parametros_id_seq" OWNER TO rpa_trycore;

--
-- Name: Parametros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Parametros_id_seq" OWNED BY public."Parametros".id;


--
-- Name: Producto; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Producto" (
    id integer NOT NULL,
    "tipoProducto" character varying,
    "numeroProducto" character varying,
    sigla character varying,
    demandado_id integer,
    medida_id integer,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Producto" OWNER TO rpa_trycore;

--
-- Name: Producto_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Producto_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Producto_id_seq" OWNER TO rpa_trycore;

--
-- Name: Producto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Producto_id_seq" OWNED BY public."Producto".id;


--
-- Name: Prompts; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Prompts" (
    id integer NOT NULL,
    "tipoPrompt" character varying NOT NULL,
    prompt text,
    context text,
    "json" text,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."Prompts" OWNER TO rpa_trycore;

--
-- Name: Prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Prompts_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Prompts_id_seq" OWNER TO rpa_trycore;

--
-- Name: Prompts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Prompts_id_seq" OWNED BY public."Prompts".id;


--
-- Name: ReporteCruce; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."ReporteCruce" (
    id integer NOT NULL,
    "numRadicado" character varying,
    masivo character varying,
    "cantidadMedidas" integer,
    "cantidadAnexos" integer,
    corte character varying,
    "rutaArchivo" character varying,
    "cantidadPaginas" integer,
    fecha_creacion timestamp without time zone,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public."ReporteCruce" OWNER TO rpa_trycore;

--
-- Name: ReporteCruce_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."ReporteCruce_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."ReporteCruce_id_seq" OWNER TO rpa_trycore;

--
-- Name: ReporteCruce_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."ReporteCruce_id_seq" OWNED BY public."ReporteCruce".id;


--
-- Name: Resolucion; Type: TABLE; Schema: public; Owner: rpa_trycore
--

CREATE TABLE public."Resolucion" (
    id integer NOT NULL,
    numero character varying,
    tipo character varying,
    medida_id integer,
    demandado_id integer
);


ALTER TABLE public."Resolucion" OWNER TO rpa_trycore;

--
-- Name: Resolucion_id_seq; Type: SEQUENCE; Schema: public; Owner: rpa_trycore
--

CREATE SEQUENCE public."Resolucion_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Resolucion_id_seq" OWNER TO rpa_trycore;

--
-- Name: Resolucion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: rpa_trycore
--

ALTER SEQUENCE public."Resolucion_id_seq" OWNED BY public."Resolucion".id;


--
-- Name: Demandado id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Demandado" ALTER COLUMN id SET DEFAULT nextval('public."Demandado_id_seq"'::regclass);


--
-- Name: Demandante id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Demandante" ALTER COLUMN id SET DEFAULT nextval('public."Demandante_id_seq"'::regclass);


--
-- Name: Documento id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Documento" ALTER COLUMN id SET DEFAULT nextval('public."Documento_id_seq"'::regclass);


--
-- Name: Entidad id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Entidad" ALTER COLUMN id SET DEFAULT nextval('public."Entidad_id_seq"'::regclass);


--
-- Name: MedidaCautelar id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaCautelar" ALTER COLUMN id SET DEFAULT nextval('public."MedidaCautelar_id_seq"'::regclass);


--
-- Name: Motivos id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Motivos" ALTER COLUMN id SET DEFAULT nextval('public."Motivos_id_seq"'::regclass);


--
-- Name: Parametros id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Parametros" ALTER COLUMN id SET DEFAULT nextval('public."Parametros_id_seq"'::regclass);


--
-- Name: Producto id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Producto" ALTER COLUMN id SET DEFAULT nextval('public."Producto_id_seq"'::regclass);


--
-- Name: Prompts id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Prompts" ALTER COLUMN id SET DEFAULT nextval('public."Prompts_id_seq"'::regclass);


--
-- Name: ReporteCruce id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."ReporteCruce" ALTER COLUMN id SET DEFAULT nextval('public."ReporteCruce_id_seq"'::regclass);


--
-- Name: Resolucion id; Type: DEFAULT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Resolucion" ALTER COLUMN id SET DEFAULT nextval('public."Resolucion_id_seq"'::regclass);


--
-- Name: Demandado Demandado_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Demandado"
    ADD CONSTRAINT "Demandado_pkey" PRIMARY KEY (id);


--
-- Name: Demandante Demandante_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Demandante"
    ADD CONSTRAINT "Demandante_pkey" PRIMARY KEY (id);


--
-- Name: Documento Documento_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Documento"
    ADD CONSTRAINT "Documento_pkey" PRIMARY KEY (id);


--
-- Name: Entidad Entidad_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Entidad"
    ADD CONSTRAINT "Entidad_pkey" PRIMARY KEY (id);


--
-- Name: MedidaCautelar MedidaCautelar_numeroCarteroWeb_key; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaCautelar"
    ADD CONSTRAINT "MedidaCautelar_numeroCarteroWeb_key" UNIQUE ("numeroCarteroWeb");


--
-- Name: MedidaCautelar MedidaCautelar_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaCautelar"
    ADD CONSTRAINT "MedidaCautelar_pkey" PRIMARY KEY (id);


--
-- Name: MedidaMotivo MedidaMotivo_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaMotivo"
    ADD CONSTRAINT "MedidaMotivo_pkey" PRIMARY KEY ("medidaId", "motivoId");


--
-- Name: Motivos Motivos_nombre_key; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Motivos"
    ADD CONSTRAINT "Motivos_nombre_key" UNIQUE (nombre);


--
-- Name: Motivos Motivos_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Motivos"
    ADD CONSTRAINT "Motivos_pkey" PRIMARY KEY (id);


--
-- Name: Parametros Parametros_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Parametros"
    ADD CONSTRAINT "Parametros_pkey" PRIMARY KEY (id);


--
-- Name: Producto Producto_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Producto"
    ADD CONSTRAINT "Producto_pkey" PRIMARY KEY (id);


--
-- Name: Prompts Prompts_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Prompts"
    ADD CONSTRAINT "Prompts_pkey" PRIMARY KEY (id);


--
-- Name: Prompts Prompts_tipoPrompt_key; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Prompts"
    ADD CONSTRAINT "Prompts_tipoPrompt_key" UNIQUE ("tipoPrompt");


--
-- Name: ReporteCruce ReporteCruce_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."ReporteCruce"
    ADD CONSTRAINT "ReporteCruce_pkey" PRIMARY KEY (id);


--
-- Name: Resolucion Resolucion_pkey; Type: CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Resolucion"
    ADD CONSTRAINT "Resolucion_pkey" PRIMARY KEY (id);


--
-- Name: Documento fk_documento_id_padre; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Documento"
    ADD CONSTRAINT fk_documento_id_padre FOREIGN KEY ("idPadre") REFERENCES public."Documento"(id);


--
-- Name: Documento fk_documento_medida; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Documento"
    ADD CONSTRAINT fk_documento_medida FOREIGN KEY (medida_id) REFERENCES public."MedidaCautelar"(id);


--
-- Name: MedidaCautelar fk_medida_demandante; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaCautelar"
    ADD CONSTRAINT fk_medida_demandante FOREIGN KEY (demandante_id) REFERENCES public."Demandante"(id);


--
-- Name: MedidaCautelar fk_medida_entidad; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaCautelar"
    ADD CONSTRAINT fk_medida_entidad FOREIGN KEY (entidad_id) REFERENCES public."Entidad"(id);


--
-- Name: MedidaMotivo fk_medida_motivo_medida; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaMotivo"
    ADD CONSTRAINT fk_medida_motivo_medida FOREIGN KEY ("medidaId") REFERENCES public."MedidaCautelar"(id);


--
-- Name: MedidaMotivo fk_medida_motivo_motivo; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."MedidaMotivo"
    ADD CONSTRAINT fk_medida_motivo_motivo FOREIGN KEY ("motivoId") REFERENCES public."Motivos"(id);


--
-- Name: Producto fk_producto_demandado; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Producto"
    ADD CONSTRAINT fk_producto_demandado FOREIGN KEY (demandado_id) REFERENCES public."Demandado"(id);


--
-- Name: Demandado fk_producto_medida; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Demandado"
    ADD CONSTRAINT fk_producto_medida FOREIGN KEY (medida_id) REFERENCES public."MedidaCautelar"(id);


--
-- Name: Producto fk_producto_medida; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Producto"
    ADD CONSTRAINT fk_producto_medida FOREIGN KEY (medida_id) REFERENCES public."MedidaCautelar"(id);


--
-- Name: Resolucion fk_resolucion_demandado; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Resolucion"
    ADD CONSTRAINT fk_resolucion_demandado FOREIGN KEY (demandado_id) REFERENCES public."Demandado"(id);


--
-- Name: Resolucion fk_resolucion_medida; Type: FK CONSTRAINT; Schema: public; Owner: rpa_trycore
--

ALTER TABLE ONLY public."Resolucion"
    ADD CONSTRAINT fk_resolucion_medida FOREIGN KEY (medida_id) REFERENCES public."MedidaCautelar"(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: rpa_trycore
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

