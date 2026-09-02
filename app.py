
import boto3
import pandas as pd
import streamlit as st
import plotly.express as px
import time


# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="TFM 2026 - Ruta Formativa Docente",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CONFIGURACIÓN AWS
# ============================================================

REGION = "us-east-1"
BASE_DATOS = "tfm_2026"
CATALOGO = "AwsDataCatalog"

BUCKET = "tfm-2026"

SALIDA_ATHENA = (
    "s3://tfm-2026/athena-results/"
)


# ============================================================
# CONEXIÓN CON ATHENA
# ============================================================

@st.cache_resource
def obtener_cliente_athena():

    # --------------------------------------------------------
    # MODO NUBE: Streamlit Community Cloud
    # --------------------------------------------------------
    # Si existe una sección [aws] en st.secrets,
    # se utilizan las credenciales almacenadas allí.
    # --------------------------------------------------------

    if "aws" in st.secrets:

        return boto3.client(
            "athena",
            region_name=st.secrets["aws"]["region"],
            aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
            aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
            aws_session_token=st.secrets["aws"]["aws_session_token"]
        )

    # --------------------------------------------------------
    # MODO LOCAL
    # --------------------------------------------------------
    # Si no existen Secrets de Streamlit, Boto3 utiliza
    # automáticamente las credenciales configuradas
    # localmente en ~/.aws/credentials.
    # --------------------------------------------------------

    return boto3.client(
        "athena",
        region_name=REGION
    )


athena = obtener_cliente_athena()


# ============================================================
# FUNCIÓN PARA EJECUTAR CONSULTAS ATHENA
# ============================================================

def ejecutar_athena(sql):

    respuesta = (
        athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={
                "Database": BASE_DATOS,
                "Catalog": CATALOGO
            },
            ResultConfiguration={
                "OutputLocation":
                    SALIDA_ATHENA
            }
        )
    )

    query_id = (
        respuesta[
            "QueryExecutionId"
        ]
    )

    while True:

        ejecucion = (
            athena.get_query_execution(
                QueryExecutionId=query_id
            )
        )

        estado = (
            ejecucion[
                "QueryExecution"
            ][
                "Status"
            ]
        )

        if estado["State"] == "SUCCEEDED":
            break

        if estado["State"] in [
            "FAILED",
            "CANCELLED"
        ]:

            raise RuntimeError(
                estado.get(
                    "StateChangeReason",
                    "Error ejecutando Athena"
                )
            )

        time.sleep(1)

    filas = []
    columnas = None
    token = None

    while True:

        parametros = {
            "QueryExecutionId":
                query_id,
            "MaxResults":
                1000
        }

        if token:

            parametros[
                "NextToken"
            ] = token

        resultado = (
            athena.get_query_results(
                **parametros
            )
        )

        if columnas is None:

            columnas = [
                columna["Name"]
                for columna
                in resultado[
                    "ResultSet"
                ][
                    "ResultSetMetadata"
                ][
                    "ColumnInfo"
                ]
            ]

        filas.extend(
            resultado[
                "ResultSet"
            ][
                "Rows"
            ]
        )

        token = (
            resultado.get(
                "NextToken"
            )
        )

        if not token:
            break

    if not filas:

        return pd.DataFrame(
            columns=columnas
        )

    primera_fila = [
        valor.get(
            "VarCharValue"
        )
        for valor
        in filas[0].get(
            "Data",
            []
        )
    ]

    if primera_fila == columnas:
        filas = filas[1:]

    datos = []

    for fila in filas:

        valores = [
            valor.get(
                "VarCharValue"
            )
            for valor
            in fila.get(
                "Data",
                []
            )
        ]

        valores += (
            [None]
            * (
                len(columnas)
                - len(valores)
            )
        )

        datos.append(
            valores[
                :len(columnas)
            ]
        )

    return pd.DataFrame(
        datos,
        columns=columnas
    )


# ============================================================
# CARGAR DATASET ANALÍTICO DESDE ATHENA
# ============================================================

@st.cache_data(
    ttl=600
)
def cargar_docentes():

    sql = """
    SELECT
        d.id_docente,
        d.nombre_docente,
        d.sede,
        d.facultad,

        CASE

            WHEN
                m.maximo_nivel_aprobado
                IS NULL
            THEN 'En progreso'

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'SIN NIVEL COMPLETADO'
            THEN 'En progreso'

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'HABILITANTE'
            THEN 'Habilitante'

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'INICIAL'
            THEN 'Inicial'

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'AVANZADO'
            THEN 'Avanzado'

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'EXPERTO'
            THEN 'Experto'

            ELSE 'En progreso'

        END AS nivel_avance,

        CASE

            WHEN
                m.maximo_nivel_aprobado
                IS NULL
            THEN 0

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'SIN NIVEL COMPLETADO'
            THEN 0

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'HABILITANTE'
            THEN 1

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'INICIAL'
            THEN 2

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'AVANZADO'
            THEN 3

            WHEN UPPER(
                TRIM(
                    CAST(
                        m.maximo_nivel_aprobado
                        AS VARCHAR
                    )
                )
            ) = 'EXPERTO'
            THEN 4

            ELSE 0

        END AS orden_nivel

    FROM docentes_modelo d

    LEFT JOIN maximo_nivel_docente m
        ON d.id_docente
        = m.id_docente

    ORDER BY d.id_docente
    """

    df = ejecutar_athena(
        sql
    )

    df[
        "orden_nivel"
    ] = pd.to_numeric(
        df["orden_nivel"]
    )

    return df


# ============================================================
# TÍTULO
# ============================================================

st.title(
    "Dashboard de Ruta Formativa Docente"
)

st.caption(
    "Amazon S3 → AWS Glue → "
    "Amazon Athena → Boto3 → Streamlit"
)


# ============================================================
# CARGAR DATOS
# ============================================================

try:

    df = cargar_docentes()

except Exception as error:

    st.error(
        "No fue posible consultar "
        "Amazon Athena."
    )

    st.exception(
        error
    )

    st.stop()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header(
    "Filtros"
)


sedes = sorted(
    df[
        "sede"
    ]
    .dropna()
    .unique()
    .tolist()
)


facultades = sorted(
    df[
        "facultad"
    ]
    .dropna()
    .unique()
    .tolist()
)


orden_niveles = [
    "En progreso",
    "Habilitante",
    "Inicial",
    "Avanzado",
    "Experto"
]


filtro_sede = (
    st.sidebar.multiselect(
        "Sede",
        sedes
    )
)


filtro_facultad = (
    st.sidebar.multiselect(
        "Facultad",
        facultades
    )
)


filtro_nivel = (
    st.sidebar.multiselect(
        "Nivel de avance",
        orden_niveles
    )
)


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


if filtro_sede:

    df_filtrado = (
        df_filtrado[
            df_filtrado[
                "sede"
            ].isin(
                filtro_sede
            )
        ]
    )


if filtro_facultad:

    df_filtrado = (
        df_filtrado[
            df_filtrado[
                "facultad"
            ].isin(
                filtro_facultad
            )
        ]
    )


if filtro_nivel:

    df_filtrado = (
        df_filtrado[
            df_filtrado[
                "nivel_avance"
            ].isin(
                filtro_nivel
            )
        ]
    )


# ============================================================
# KPI
# ============================================================

total_docentes = (
    df_filtrado[
        "id_docente"
    ].nunique()
)


total_sedes = (
    df_filtrado[
        "sede"
    ].nunique()
)


total_facultades = (
    df_filtrado[
        "facultad"
    ].nunique()
)


con_nivel = (
    df_filtrado[
        df_filtrado[
            "orden_nivel"
        ] > 0
    ][
        "id_docente"
    ].nunique()
)


col1, col2, col3, col4 = (
    st.columns(4)
)


col1.metric(
    "Docentes",
    f"{total_docentes:,}"
)


col2.metric(
    "Sedes",
    total_sedes
)


col3.metric(
    "Facultades",
    total_facultades
)


col4.metric(
    "Con nivel aprobado",
    f"{con_nivel:,}"
)


# ============================================================
# DOCENTES POR SEDE
# ============================================================

sede_df = (
    df_filtrado
    .groupby(
        "sede"
    )[
        "id_docente"
    ]
    .nunique()
    .reset_index(
        name="total_docentes"
    )
    .sort_values(
        "total_docentes",
        ascending=True
    )
)


fig_sede = px.bar(
    sede_df,
    x="total_docentes",
    y="sede",
    orientation="h",
    text="total_docentes",
    title="Docentes por sede"
)


fig_sede.update_layout(
    xaxis_title=(
        "Número de docentes"
    ),
    yaxis_title="Sede"
)


# ============================================================
# DOCENTES POR FACULTAD
# ============================================================

facultad_df = (
    df_filtrado
    .groupby(
        "facultad"
    )[
        "id_docente"
    ]
    .nunique()
    .reset_index(
        name="total_docentes"
    )
    .sort_values(
        "total_docentes",
        ascending=True
    )
)


fig_facultad = px.bar(
    facultad_df,
    x="total_docentes",
    y="facultad",
    orientation="h",
    text="total_docentes",
    title="Docentes por facultad"
)


fig_facultad.update_layout(
    xaxis_title=(
        "Número de docentes"
    ),
    yaxis_title="Facultad"
)


# ============================================================
# NIVEL DE AVANCE
# ============================================================

nivel_df = (
    df_filtrado[
        "nivel_avance"
    ]
    .value_counts()
    .reindex(
        orden_niveles,
        fill_value=0
    )
    .rename_axis(
        "nivel_avance"
    )
    .reset_index(
        name="total_docentes"
    )
)


fig_nivel = px.bar(
    nivel_df,
    x="nivel_avance",
    y="total_docentes",
    text="total_docentes",
    title=(
        "Máximo nivel aprobado "
        "en la ruta formativa"
    )
)


fig_nivel.update_layout(
    xaxis_title=(
        "Nivel de avance"
    ),
    yaxis_title=(
        "Número de docentes"
    )
)


# ============================================================
# MOSTRAR GRÁFICOS
# ============================================================

grafico_1, grafico_2 = (
    st.columns(2)
)


with grafico_1:

    st.plotly_chart(
        fig_sede,
        use_container_width=True
    )


with grafico_2:

    st.plotly_chart(
        fig_facultad,
        use_container_width=True
    )


st.plotly_chart(
    fig_nivel,
    use_container_width=True
)


# ============================================================
# TABLA DETALLADA
# ============================================================

with st.expander(
    "Ver detalle de docentes"
):

    st.dataframe(
        df_filtrado[
            [
                "id_docente",
                "nombre_docente",
                "sede",
                "facultad",
                "nivel_avance"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.caption(
    "Fuente: Amazon Athena | "
    "Base de datos: tfm_2026"
)
