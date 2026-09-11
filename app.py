from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="TFM — Learning Analytics",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TEMA VISUAL UNIFICADO
# ============================================================

PALETA_NIVELES = {
    "SIN_NIVEL": "#94A3B8",
    "HABILITANTE": "#93C5FD",
    "INICIAL": "#60A5FA",
    "AVANZADO": "#2563EB",
    "EXPERTO": "#0F2747"
}

PALETA_BASE = ["#2563EB", "#0F766E", "#F59E0B", "#64748B", "#0F2747"]

ETIQUETAS = {
    "nivel_aprobado_corte": "Nivel Aprobado",
    "tipo_vinculacion": "Tipo de Vinculación",
    "dias_desde_ultima_actividad": "Días desde Última Actividad",
    "dias_desde_ultimo_avance": "Días desde Último Avance",
    "riesgo_medio": "Riesgo Medio",
    "probabilidad_media": "Probabilidad Media",
    "unidad_academica": "Unidad Académica",
    "carga_asignada": "Carga Asignada",
    "actividades_ultimos_90_dias": "Actividades Últimos 90 Días",
    "cursos_aprobados_corte": "Cursos Aprobados",
    "cursos_reprobados_corte": "Cursos Reprobados",
    "sede": "Sede",
    "jornada": "Jornada",
    "modelo": "Modelo",
    "metrica": "Métrica",
    "valor": "Valor",
    "docentes": "Docentes"
}

VARIABLES_IA = {
    "dias_desde_ultima_actividad_imp": "Días sin actividad",
    "actividades_ultimos_90_dias_imp": "Actividad últimos 90 días",
    "tasa_aprobacion_corte_imp": "Tasa de aprobación",
    "actividades_ultimos_180_dias_imp": "Actividad últimos 180 días",
    "cursos_aprobados_corte_imp": "Cursos aprobados",
    "dias_desde_ultimo_avance_imp": "Días desde último avance",
    "cursos_realizados_corte_imp": "Cursos realizados",
    "cursos_reprobados_corte_imp": "Cursos reprobados",
    "promedio_final_score_corte_imp": "Promedio de calificación",
    "promedio_dias_entre_actividades_imp": "Intervalo entre actividades"
}

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = PALETA_BASE
px.defaults.labels = ETIQUETAS

st.markdown(
    """
    <style>
    :root {
        --bg:#F8FAFC;
        --card:#FFFFFF;
        --text:#0F172A;
        --muted:#64748B;
        --navy:#0F2747;
        --primary:#2563EB;
        --success:#0F766E;
        --warning:#F59E0B;
        --danger:#DC2626;
        --border:#E2E8F0;
        --shadow:0 10px 30px rgba(15,39,71,.07);
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--navy) !important;
        letter-spacing: -0.015em;
    }

    h1 {
        font-weight: 760 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    div[data-baseweb="tab-list"] {
        gap: .25rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.1rem;
    }

    button[data-baseweb="tab"] {
        color: var(--muted);
        font-weight: 650;
        padding-left: 1rem;
        padding-right: 1rem;
        border-radius: .55rem .55rem 0 0;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary) !important;
        background: rgba(37,99,235,.05);
        border-bottom: 3px solid var(--primary);
    }

    div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        border-color: #CBD5E1;
        border-radius: .6rem;
        background: #FFFFFF;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: .75rem;
        overflow: hidden;
        background: #FFFFFF;
    }

    .kpi-grid {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
        gap:14px;
        margin: .4rem 0 1.25rem;
    }

    .kpi-card {
        position:relative;
        overflow:hidden;
        min-height:108px;
        padding:18px 18px 16px;
        background:#FFFFFF;
        border:1px solid var(--border);
        border-radius:14px;
        box-shadow:var(--shadow);
    }

    .kpi-card:before {
        content:"";
        position:absolute;
        top:0;
        bottom:0;
        left:0;
        width:4px;
        background:var(--primary);
    }

    .kpi-card.success:before { background:var(--success); }
    .kpi-card.warning:before { background:var(--warning); }
    .kpi-card.danger:before { background:var(--danger); }
    .kpi-card.slate:before { background:#475569; }

    .kpi-label {
        color:var(--muted);
        font-size:11px;
        font-weight:700;
        letter-spacing:.045em;
        text-transform:uppercase;
        margin-bottom:8px;
    }

    .kpi-value {
        color:var(--navy);
        font-size:29px;
        font-weight:780;
        line-height:1.1;
    }

    .sim-note {
        margin-top:.6rem;
        color:var(--muted);
        font-size:.82rem;
    }

    .tfm-footer {
        text-align:center;
        color:#94A3B8;
        font-size:.76rem;
        padding:1.8rem 0 .5rem;
        margin-top:2.2rem;
        border-top:1px solid var(--border);
    }
    </style>
    """,
    unsafe_allow_html=True
)

def formato_nivel(valor):
    valor = str(valor)
    if valor == "SIN_NIVEL":
        return "Sin Nivel"
    return valor.replace("_", " ").title()

def aplicar_estilo_figura(fig, altura=430):
    if fig.layout.title.text and not str(fig.layout.title.text).startswith("<b>"):
        fig.layout.title.text = f"<b>{fig.layout.title.text}</b>"
    fig.update_layout(
        template="plotly_white",
        height=altura,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, Segoe UI, Arial, sans-serif",
            size=13,
            color="#0F172A"
        ),
        title=dict(
            x=.5,
            xanchor="center",
            font=dict(size=18, color="#0F2747")
        ),
        margin=dict(l=70, r=30, t=70, b=70),
        legend=dict(
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0)"
        )
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#E5E7EB",
        tickfont=dict(color="#64748B")
    )
    fig.update_yaxes(
        gridcolor="#E5E7EB",
        gridwidth=1,
        zeroline=False,
        linecolor="#E5E7EB",
        tickfont=dict(color="#64748B")
    )
    return fig

def render_kpis(tarjetas):
    html = '<div class="kpi-grid">'
    for etiqueta, valor, tono in tarjetas:
        html += (
            f'<div class="kpi-card {tono}">'
            f'<div class="kpi-label">{etiqueta}</div>'
            f'<div class="kpi-value">{valor}</div>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def footer_tfm():
    st.markdown(
        '<div class="tfm-footer">TFM UCLM · Datos sintéticos · Learning Analytics y Analítica Curricular</div>',
        unsafe_allow_html=True
    )


BASE = Path(__file__).parent
DATA = BASE / "data"

ORDEN_NIVELES = ["SIN_NIVEL", "HABILITANTE", "INICIAL", "AVANZADO", "EXPERTO"]

@st.cache_data
def cargar_datos():
    df = pd.read_csv(DATA / "dashboard_docentes.csv")
    ruta = pd.read_csv(DATA / "ruta_docentes.csv")
    metricas = pd.read_csv(DATA / "metricas_modelos.csv")
    importancias = pd.read_csv(DATA / "importancia_variables.csv")
    temporal = pd.read_csv(DATA / "temporal_ruta.csv")

    columnas_numericas = [
        "cursos_realizados_corte", "cursos_aprobados_corte", "cursos_reprobados_corte",
        "tasa_aprobacion_corte", "dias_desde_ultima_actividad", "dias_desde_ultimo_avance",
        "actividades_ultimos_90_dias", "target_progreso_6m", "prediccion_progreso_6m",
        "probabilidad_progreso_6m", "riesgo_no_progreso_6m", "carga_asignada"
    ]
    for c in columnas_numericas:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ["auc_roc", "auc_pr", "accuracy", "f1", "precision", "recall"]:
        if c in metricas.columns:
            metricas[c] = pd.to_numeric(metricas[c], errors="coerce")

    if "importancia" in importancias.columns:
        importancias["importancia"] = pd.to_numeric(importancias["importancia"], errors="coerce")

    temporal["mes"] = pd.to_datetime(temporal["mes"], errors="coerce")
    temporal["cursos_finalizados"] = pd.to_numeric(temporal["cursos_finalizados"], errors="coerce")

    df["nombre_docente"] = df["nombre_docente"].fillna(df["id_docente"])
    df["nivel_riesgo"] = pd.cut(
        df["riesgo_no_progreso_6m"],
        bins=[-0.01, 0.30, 0.60, 1.01],
        labels=["BAJO", "MEDIO", "ALTO"]
    )

    return df, ruta, metricas, importancias, temporal

df, df_ruta, df_metricas, df_importancias, df_temporal = cargar_datos()

st.title("Learning Analytics y Analítica Curricular")
st.caption("Datos sintéticos · Horizonte predictivo: 6 meses")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Resumen",
    "Descriptiva",
    "Predictiva",
    "Modelos",
    "Docentes y riesgo",
    "Simulador"
])

with tab1:
    modelo_ganador = df_metricas.sort_values("auc_roc", ascending=False).iloc[0]["modelo"]

    render_kpis([
        ("Docentes", f"{len(df):,}", "primary"),
        ("Progreso Predicho", f"{df['prediccion_progreso_6m'].mean()*100:.1f}%", "success"),
        ("Probabilidad Media", f"{df['probabilidad_progreso_6m'].mean()*100:.1f}%", "primary"),
        ("Riesgo Medio", f"{df['riesgo_no_progreso_6m'].mean()*100:.1f}%", "warning"),
        ("Riesgo Alto", f"{int((df['nivel_riesgo'] == 'ALTO').sum()):,}", "danger")
    ])

with tab2:
    st.subheader("Distribución interactiva por nivel")

    f1, f2, f3, f4 = st.columns(4)
    sedes = f1.multiselect("Sede", sorted(df_ruta["sede"].dropna().unique()))
    niveles = f2.multiselect(
        "Nivel",
        ORDEN_NIVELES,
        format_func=formato_nivel
    )
    unidades = f3.multiselect("Unidad Académica", sorted(df_ruta["unidad_academica"].dropna().unique()))
    contratos = f4.multiselect("Tipo de contrato", sorted(df_ruta["jornada"].dropna().unique()))
    agrupar = st.selectbox(
        "Visualizar por",
        ["sede", "unidad_academica", "tipo_vinculacion", "jornada"],
        format_func=lambda x: ETIQUETAS.get(x, x)
    )

    tmp = df.copy()
    tmp_ruta = df_ruta.copy()

    if sedes:
        tmp = tmp[tmp["sede"].isin(sedes)]
        tmp_ruta = tmp_ruta[tmp_ruta["sede"].isin(sedes)]
    if niveles:
        tmp = tmp[tmp["nivel_aprobado_corte"].isin(niveles)]
        tmp_ruta = tmp_ruta[tmp_ruta["nivel_aprobado_corte"].isin(niveles)]
    if unidades:
        tmp = tmp[tmp["unidad_academica"].isin(unidades)]
        tmp_ruta = tmp_ruta[tmp_ruta["unidad_academica"].isin(unidades)]
    if contratos:
        tmp = tmp[tmp["jornada"].isin(contratos)]
        tmp_ruta = tmp_ruta[tmp_ruta["jornada"].isin(contratos)]
    dist = (
        tmp_ruta.groupby([agrupar, "nivel_aprobado_corte"], dropna=False)
        .size()
        .reset_index(name="docentes")
    )

    dist["Nivel Aprobado"] = dist["nivel_aprobado_corte"].map(formato_nivel)

    if agrupar == "unidad_academica" and dist[agrupar].nunique() > 10:
        fig_dist = px.bar(
            dist,
            y=agrupar,
            x="docentes",
            color="Nivel Aprobado",
            orientation="h",
            color_discrete_sequence=list(PALETA_NIVELES.values()),
            title="Distribución de docentes por nivel",
            labels={agrupar: "Unidad Académica", "docentes": "Docentes"}
        )
        aplicar_estilo_figura(fig_dist, altura=max(500, dist[agrupar].nunique() * 30))
        fig_dist.update_layout(margin=dict(l=250, r=30, t=70, b=60))
    else:
        fig_dist = px.bar(
            dist,
            x=agrupar,
            y="docentes",
            color="Nivel Aprobado",
            color_discrete_sequence=list(PALETA_NIVELES.values()),
            title="Distribución de docentes por nivel",
            labels={agrupar: ETIQUETAS.get(agrupar, agrupar), "docentes": "Docentes"}
        )
        aplicar_estilo_figura(fig_dist)

    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown(
        f"""
        <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;
                    background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                    border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
            Esta distribución utiliza la población completa de la Ruta Formativa:
            <strong>{len(df_ruta):,} docentes en Ruta</strong> analizados al corte,
            incluyendo a quienes ya alcanzaron el nivel Experto.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Unidad Académica × Nivel Formativo")

    hm = (
        tmp_ruta.groupby(["unidad_academica", "nivel_aprobado_corte"], dropna=False)
        .size()
        .reset_index(name="docentes")
    )
    hm["porcentaje"] = hm["docentes"] / hm.groupby("unidad_academica")["docentes"].transform("sum") * 100

    pivot = hm.pivot(
        index="unidad_academica",
        columns="nivel_aprobado_corte",
        values="porcentaje"
    ).fillna(0)

    for nivel in ORDEN_NIVELES:
        if nivel not in pivot.columns:
            pivot[nivel] = 0
    pivot = pivot[ORDEN_NIVELES]
    pivot.columns = [formato_nivel(c) for c in pivot.columns]

    fig_hm = px.imshow(
        pivot,
        aspect="auto",
        text_auto=".1f",
        color_continuous_scale="Blues",
        labels={"x": "Nivel Formativo", "y": "Unidad Académica", "color": "% Docentes"},
        title="Distribución porcentual por unidad académica"
    )
    st.markdown(
        """
        <div style="margin-top:4px;margin-bottom:14px;padding:12px 14px;
                    background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                    border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
            <strong>Este es un mapa de calor.</strong>
            <strong>Cómo leerlo:</strong> las filas corresponden a las unidades académicas y las columnas a los niveles
            <strong>Sin Nivel, Habilitante, Inicial, Avanzado y Experto</strong>. Cada celda muestra el porcentaje de docentes
            de esa unidad que se encuentra en ese nivel; cuanto más intenso es el azul, mayor es la proporción.
            <strong>Qué representa:</strong> la composición del avance formativo dentro de cada unidad académica.
            <strong>Para qué sirve:</strong> permite comparar unidades, identificar dónde se concentra el rezago o el avance
            y detectar patrones que puedan orientar acciones de acompañamiento formativo.
        </div>
        """,
        unsafe_allow_html=True
    )

    aplicar_estilo_figura(fig_hm, altura=max(850, len(pivot) * 27 + 170))
    fig_hm.update_layout(
        margin=dict(l=300, r=60, t=90, b=90),
        autosize=True
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    st.subheader("Evolución temporal de la ruta formativa")

    temp_display = df_temporal.copy()
    temp_display["Nivel"] = temp_display["nivel"].map(formato_nivel)

    fig_temp = px.line(
        temp_display.dropna(subset=["mes"]),
        x="mes",
        y="cursos_finalizados",
        color="Nivel",
        markers=True,
        color_discrete_sequence=list(PALETA_NIVELES.values()),
        title="Cursos finalizados por mes y nivel",
        labels={"mes": "Mes", "cursos_finalizados": "Cursos Finalizados"}
    )
    fig_temp.update_traces(line=dict(width=2.5), marker=dict(size=6))
    aplicar_estilo_figura(fig_temp)
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown(
        """
        <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;
                    background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                    border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
            <strong>Este gráfico muestra cursos finalizados, no docentes.</strong>
            Cada punto representa la cantidad de cursos completados durante un mes en cada nivel formativo.
            Un mismo docente puede aportar más de un curso. La serie utiliza el historial completo de la
            Ruta Formativa disponible hasta diciembre de 2025.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Carga docente × participación")

        fig_carga = px.scatter(
            tmp,
            x="carga_asignada",
            y="actividades_ultimos_90_dias",
            color="tipo_vinculacion",
            symbol="jornada",
            hover_data=["nombre_docente", "nivel_aprobado_corte"],
            color_discrete_sequence=PALETA_BASE,
            title="Carga asignada y actividad reciente",
            labels={
                "carga_asignada": "Carga Asignada",
                "actividades_ultimos_90_dias": "Actividades Últimos 90 Días",
                "tipo_vinculacion": "Tipo de Vinculación",
                "jornada": "Jornada",
                "nombre_docente": "Docente",
                "nivel_aprobado_corte": "Nivel Aprobado"
            }
        )
        fig_carga.update_traces(marker=dict(size=9, opacity=.72))
        aplicar_estilo_figura(fig_carga)
        st.plotly_chart(fig_carga, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;
                        background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                        border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
                <strong>Este es un gráfico de dispersión.</strong>
                En el eje X se muestra la <strong>Carga Asignada</strong> y en el eje Y las
                <strong>Actividades de los Últimos 90 Días</strong>. Cada punto representa un docente;
                el color y la forma distinguen combinaciones de <strong>Tipo de Vinculación + Jornada</strong>.
                Su propósito es explorar si existe relación entre carga docente y participación reciente,
                y detectar patrones como docentes con alta carga y baja actividad o diferencias entre perfiles contractuales.
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.subheader("Perfil descriptivo previo al riesgo")

        perfil = tmp.copy()
        perfil["perfil_actividad"] = np.where(
            perfil["actividades_ultimos_90_dias"] == 0,
            "Sin Actividad 90 Días",
            "Con Actividad 90 Días"
        )

        perfil = (
            perfil.groupby("perfil_actividad")
            .agg(
                tasa_aprobacion=("tasa_aprobacion_corte", "mean"),
                cursos_aprobados=("cursos_aprobados_corte", "mean"),
                dias_desde_actividad=("dias_desde_ultima_actividad", "mean"),
                carga_asignada=("carga_asignada", "mean")
            )
            .reset_index()
        )

        perfil_long = perfil.melt(
            id_vars="perfil_actividad",
            var_name="variable",
            value_name="valor"
        )

        nombres_perfil = {
            "tasa_aprobacion": "Tasa de Aprobación",
            "cursos_aprobados": "Cursos Aprobados",
            "dias_desde_actividad": "Días desde Última Actividad",
            "carga_asignada": "Carga Asignada"
        }
        perfil_long["Variable"] = perfil_long["variable"].map(nombres_perfil).fillna(perfil_long["variable"])

        fig_perfil = px.bar(
            perfil_long,
            x="Variable",
            y="valor",
            color="perfil_actividad",
            barmode="group",
            color_discrete_sequence=["#2563EB", "#F59E0B"],
            title="Docentes con y sin actividad reciente",
            labels={"valor": "Valor", "perfil_actividad": "Perfil de Actividad"}
        )
        aplicar_estilo_figura(fig_perfil)
        st.plotly_chart(fig_perfil, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;
                        background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                        border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
                <strong>Este gráfico compara el perfil descriptivo de docentes con y sin actividad reciente.</strong>
                Cada grupo de barras corresponde a una característica del perfil, y los colores distinguen
                <strong>Con Actividad 90D</strong> y <strong>Sin Actividad 90D</strong>.
                Barras más altas indican valores medios mayores en esa característica.
                Su propósito es resumir diferencias de perfil previas al análisis de riesgo y mostrar qué variables
                distinguen a docentes con y sin participación reciente.
            </div>
            """,
            unsafe_allow_html=True
        )

with tab3:
    n_progreso_predicho = int(df["prediccion_progreso_6m"].fillna(0).sum())
    n_riesgo_alto = int((df["nivel_riesgo"].astype(str) == "ALTO").sum())

    st.markdown(
        f"""
        <div style="margin-bottom:18px;padding:13px 15px;background:#F8FAFC;
                    border:1px solid #E2E8F0;border-left:4px solid #2563EB;
                    border-radius:10px;color:#334155;font-size:13px;line-height:1.6;">
            El modelo predictivo trabaja con <strong>{len(df):,} docentes elegibles para predicción</strong>
            de los <strong>{len(df_ruta):,} docentes en Ruta</strong>. Se excluyen los 83 docentes que ya
            habían alcanzado <strong>Experto</strong> al corte, porque se encuentran en el nivel máximo
            de la Ruta Formativa y no pueden progresar a un nivel siguiente durante el horizonte de seis meses.
            Entre los docentes elegibles, <strong>{n_progreso_predicho:,} presentan progreso predicho</strong>
            y <strong>{n_riesgo_alto:,} se clasifican en riesgo alto</strong>.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        riesgo = (
            df.groupby("nivel_riesgo", observed=False)
            .size()
            .reset_index(name="docentes")
        )
        riesgo["Nivel de Riesgo"] = riesgo["nivel_riesgo"].astype(str).str.title()

        fig = px.bar(
            riesgo,
            x="Nivel de Riesgo",
            y="docentes",
            color="Nivel de Riesgo",
            color_discrete_map={"Bajo": "#0F766E", "Medio": "#F59E0B", "Alto": "#DC2626"},
            title="Distribución por nivel de riesgo",
            labels={"docentes": "Docentes"}
        )
        fig.update_layout(showlegend=False)
        aplicar_estilo_figura(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;
                        border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;
                        color:#334155;font-size:13px;line-height:1.55;">
                <strong>Cómo leerlo:</strong> la altura de cada barra indica cuántos docentes elegibles se clasifican
                con riesgo bajo, medio o alto de no progresar en los próximos seis meses.
                <strong>Para qué sirve:</strong> permite dimensionar la concentración del riesgo y estimar cuántos docentes
                podrían requerir seguimiento o apoyo.
            </div>
            """, unsafe_allow_html=True
        )

    with c2:
        riesgo_nivel = (
            df.groupby("nivel_aprobado_corte")
            .agg(riesgo_medio=("riesgo_no_progreso_6m", "mean"))
            .reset_index()
        )
        riesgo_nivel["Nivel Aprobado"] = riesgo_nivel["nivel_aprobado_corte"].map(formato_nivel)

        fig = px.bar(
            riesgo_nivel,
            x="Nivel Aprobado",
            y="riesgo_medio",
            color="Nivel Aprobado",
            color_discrete_sequence=list(PALETA_NIVELES.values()),
            title="Riesgo medio por nivel formativo",
            labels={"riesgo_medio": "Riesgo Medio"}
        )
        fig.update_layout(showlegend=False)
        aplicar_estilo_figura(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;
                        border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;
                        color:#334155;font-size:13px;line-height:1.55;">
                <strong>Cómo leerlo:</strong> cada barra representa el riesgo medio estimado de los docentes de un nivel formativo;
                una barra más alta indica mayor riesgo promedio de no progresar.
                <strong>Para qué sirve:</strong> permite comparar en qué niveles se concentra mayor riesgo.
                Experto no aparece porque ya corresponde al nivel máximo y esos docentes no son elegibles para predicción.
            </div>
            """, unsafe_allow_html=True
        )

    c3, c4 = st.columns(2)

    with c3:
        riesgo_sede = (
            df.groupby("sede")
            .agg(riesgo_medio=("riesgo_no_progreso_6m", "mean"))
            .reset_index()
        )

        fig = px.bar(
            riesgo_sede,
            x="sede",
            y="riesgo_medio",
            color_discrete_sequence=["#2563EB"],
            title="Riesgo medio por sede",
            labels={"sede": "Sede", "riesgo_medio": "Riesgo Medio"}
        )
        aplicar_estilo_figura(fig)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;
                        border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;
                        color:#334155;font-size:13px;line-height:1.55;">
                <strong>Cómo leerlo:</strong> cada barra muestra el riesgo medio estimado de los docentes elegibles de una sede;
                una barra más alta indica mayor riesgo promedio de no progreso.
                <strong>Para qué sirve:</strong> permite comparar las sedes y detectar diferencias territoriales que puedan orientar
                acciones de acompañamiento.
            </div>
            """, unsafe_allow_html=True
        )

    with c4:
        top_imp = df_importancias.head(15).copy()
        top_imp["Variable"] = top_imp["variable"].map(VARIABLES_IA).fillna(
            top_imp["variable"].str.replace("_imp", "", regex=False).str.replace("_", " ").str.title()
        )
        top_imp = top_imp.sort_values("importancia")

        fig = px.bar(
            top_imp,
            x="importancia",
            y="Variable",
            orientation="h",
            color_discrete_sequence=["#2563EB"],
            title="Variables de mayor importancia",
            labels={"importancia": "Importancia"}
        )
        aplicar_estilo_figura(fig, altura=500)
        fig.update_layout(margin=dict(l=190, r=30, t=70, b=60))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;
                        border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;
                        color:#334155;font-size:13px;line-height:1.55;">
                <strong>Cómo leerlo:</strong> las variables se ordenan según su importancia; una barra más larga indica mayor
                contribución a las predicciones del modelo seleccionado.
                <strong>Para qué sirve:</strong> permite identificar qué información utiliza con mayor peso el modelo.
                La importancia indica contribución predictiva, no causalidad.
            </div>
            """, unsafe_allow_html=True
        )

with tab4:
    nombres_metricas = {
        "auc_roc": "ROC-AUC",
        "auc_pr": "PR-AUC",
        "accuracy": "Exactitud",
        "f1": "F1",
        "precision": "Precisión",
        "recall": "Sensibilidad"
    }

    metricas_long = df_metricas.melt(
        id_vars=["modelo"],
        value_vars=["auc_roc", "auc_pr", "accuracy", "f1", "precision", "recall"],
        var_name="metrica",
        value_name="valor"
    )
    metricas_long["Métrica"] = metricas_long["metrica"].map(nombres_metricas)
    metricas_long["Modelo"] = metricas_long["modelo"].str.replace("_", " ").str.title()

    fig = px.bar(
        metricas_long,
        x="Métrica",
        y="valor",
        color="Modelo",
        barmode="group",
        color_discrete_sequence=PALETA_BASE,
        title="Comparación de modelos",
        labels={"valor": "Valor"}
    )
    aplicar_estilo_figura(fig)
    st.plotly_chart(fig, use_container_width=True)

    tabla_metricas = df_metricas.rename(columns={
        "modelo": "Modelo",
        "auc_roc": "ROC-AUC",
        "auc_pr": "PR-AUC",
        "accuracy": "Exactitud",
        "f1": "F1",
        "precision": "Precisión",
        "recall": "Sensibilidad"
    })
    st.dataframe(tabla_metricas, use_container_width=True)

    st.markdown(
        f"""
        <div style="margin-top:10px;margin-bottom:18px;padding:12px 14px;background:#F8FAFC;
                    border:1px solid #E2E8F0;border-left:4px solid #475569;border-radius:10px;
                    color:#334155;font-size:13px;line-height:1.55;">
            <strong>Modelo seleccionado: {str(modelo_ganador).replace("_", " ").title()}.</strong>
            Se eligió después del entrenamiento y la comparación de los modelos candidatos mediante sus métricas de desempeño.
            Las predicciones del dashboard corresponden a este modelo.
        </div>
        """,
        unsafe_allow_html=True
    )

with tab5:
    st.subheader("Docentes y riesgo")

    # 1. Unidad académica × % docentes en riesgo alto
    unidad_riesgo = (
        df.groupby("unidad_academica")
          .agg(
              docentes=("id_docente","count"),
              riesgo_alto=("nivel_riesgo", lambda s: int((s.astype(str) == "ALTO").sum()))
          )
          .reset_index()
    )
    unidad_riesgo["pct_riesgo_alto"] = 100 * unidad_riesgo["riesgo_alto"] / unidad_riesgo["docentes"]
    unidad_riesgo = unidad_riesgo.sort_values("pct_riesgo_alto")
    fig = px.bar(unidad_riesgo, x="pct_riesgo_alto", y="unidad_academica", orientation="h",
                 color_discrete_sequence=["#2563EB"], title="Unidad académica × % docentes en riesgo alto",
                 labels={"pct_riesgo_alto":"% Docentes en Riesgo Alto","unidad_academica":"Unidad Académica"})
    fig.update_xaxes(range=[0,100], ticksuffix="%")
    aplicar_estilo_figura(fig, altura=max(520,len(unidad_riesgo)*25))
    fig.update_layout(margin=dict(l=250,r=30,t=70,b=60),showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> cada barra corresponde a una unidad académica y muestra el porcentaje de sus docentes elegibles clasificados en riesgo alto. <strong>Qué representa:</strong> la concentración del riesgo dentro de cada unidad. <strong>Para qué sirve:</strong> permite priorizar unidades donde una mayor proporción de docentes podría requerir seguimiento.</div>""",unsafe_allow_html=True)

    # 2. Sede × nivel formativo × riesgo
    sede_nivel = df.groupby(["sede","nivel_aprobado_corte"]).agg(riesgo_medio=("riesgo_no_progreso_6m","mean")).reset_index()
    sede_nivel["Nivel Aprobado"] = sede_nivel["nivel_aprobado_corte"].map(formato_nivel)
    fig = px.bar(sede_nivel,x="Nivel Aprobado",y="riesgo_medio",color="sede",barmode="group",
                 color_discrete_sequence=PALETA_BASE,title="Sede × nivel formativo × riesgo",
                 labels={"riesgo_medio":"Riesgo Medio","sede":"Sede"})
    aplicar_estilo_figura(fig); st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> para cada nivel formativo se comparan las sedes y la altura de las barras representa el riesgo medio. <strong>Qué representa:</strong> la combinación entre sede, nivel alcanzado y riesgo de no progreso. <strong>Para qué sirve:</strong> permite detectar si las diferencias se concentran más por nivel formativo o por sede.</div>""",unsafe_allow_html=True)

    # 3. Unidad académica × inactividad × riesgo
    dfi = df.copy()
    dfi["actividad_reciente"] = np.where(dfi["actividades_ultimos_90_dias"]==0,"Sin Actividad 90D","Con Actividad 90D")
    top_u = dfi.groupby("unidad_academica")["id_docente"].count().sort_values(ascending=False).head(12).index
    ui = dfi[dfi["unidad_academica"].isin(top_u)].groupby(["unidad_academica","actividad_reciente"]).agg(riesgo_medio=("riesgo_no_progreso_6m","mean")).reset_index()
    fig = px.bar(ui,y="unidad_academica",x="riesgo_medio",color="actividad_reciente",orientation="h",barmode="group",
                 color_discrete_sequence=["#2563EB","#F59E0B"],title="Unidad académica × inactividad × riesgo",
                 labels={"unidad_academica":"Unidad Académica","riesgo_medio":"Riesgo Medio","actividad_reciente":"Actividad reciente"})
    aplicar_estilo_figura(fig,altura=max(700,len(top_u)*42))
    fig.update_layout(margin=dict(l=250,r=30,t=155,b=60),legend=dict(orientation="h",y=1.22,x=.5,xanchor="center",yanchor="bottom"))
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> cada unidad académica compara docentes con actividad y sin actividad reciente; barras más largas indican mayor riesgo medio. <strong>Qué representa:</strong> la relación entre inactividad reciente y riesgo dentro de cada unidad. <strong>Para qué sirve:</strong> ayuda a identificar unidades donde la falta de actividad coincide con mayor riesgo de no progreso.</div>""",unsafe_allow_html=True)

    # 4. Tipo de contrato × riesgo
    contrato = df.groupby("jornada").agg(riesgo_medio=("riesgo_no_progreso_6m","mean")).reset_index()
    fig = px.bar(contrato,x="jornada",y="riesgo_medio",color="jornada",color_discrete_sequence=["#2563EB","#0F766E"],
                 title="Tipo de contrato × riesgo",labels={"jornada":"Tipo de contrato","riesgo_medio":"Riesgo Medio"})
    fig.update_layout(showlegend=False); aplicar_estilo_figura(fig); st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> cada barra corresponde a un tipo de contrato, <strong>Por Horas</strong> o <strong>Contratado</strong>, y muestra su riesgo medio. <strong>Qué representa:</strong> diferencias de riesgo asociadas al tipo de contratación. <strong>Para qué sirve:</strong> permite comparar directamente los dos perfiles contractuales sin duplicar vinculación y jornada.</div>""",unsafe_allow_html=True)

    # 5. Tasa de aprobación × riesgo — escala 0–100 corregida
    dft = df.copy()
    dft["rango_tasa"] = pd.cut(pd.to_numeric(dft["tasa_aprobacion_corte"],errors="coerce"),
                               bins=[-0.01,50,70,85,100.01],labels=["≤50%","50–70%","70–85%",">85%"],include_lowest=True)
    ta = dft.dropna(subset=["rango_tasa"]).groupby("rango_tasa",observed=False).agg(riesgo_medio=("riesgo_no_progreso_6m","mean"),docentes=("id_docente","count")).reset_index()
    fig = px.bar(ta,x="rango_tasa",y="riesgo_medio",color_discrete_sequence=["#2563EB"],title="Tasa de aprobación × riesgo",
                 labels={"rango_tasa":"Tasa de Aprobación","riesgo_medio":"Riesgo Medio"},hover_data={"docentes":True})
    aplicar_estilo_figura(fig); st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> los docentes se agrupan por tasa de aprobación (≤50%, 50–70%, 70–85% y >85%); la altura indica el riesgo medio. <strong>Qué representa:</strong> la relación entre desempeño histórico y riesgo predicho. <strong>Para qué sirve:</strong> permite observar si una mayor tasa de aprobación se asocia con menor riesgo de no progreso.</div>""",unsafe_allow_html=True)

    # 6. Cursos aprobados × riesgo
    dfc = df.copy()
    dfc["rango_cursos"] = pd.cut(pd.to_numeric(dfc["cursos_aprobados_corte"],errors="coerce"),bins=[-1,3,6,9,1000],labels=["0–3","4–6","7–9","10+"])
    ca = dfc.groupby("rango_cursos",observed=False).agg(riesgo_medio=("riesgo_no_progreso_6m","mean")).reset_index()
    fig = px.bar(ca,x="rango_cursos",y="riesgo_medio",color_discrete_sequence=["#2563EB"],title="Cursos aprobados × riesgo",
                 labels={"rango_cursos":"Cursos Aprobados","riesgo_medio":"Riesgo Medio"})
    aplicar_estilo_figura(fig); st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> los docentes se agrupan por número de cursos aprobados y cada barra muestra el riesgo medio del grupo. <strong>Qué representa:</strong> la relación entre avance acumulado en la Ruta y riesgo futuro. <strong>Para qué sirve:</strong> permite identificar si quienes han aprobado más cursos presentan un perfil de riesgo diferente.</div>""",unsafe_allow_html=True)

    # 7. Actividad reciente × riesgo
    dfa = df.copy()
    dfa["rango_actividad"] = pd.cut(pd.to_numeric(dfa["actividades_ultimos_90_dias"],errors="coerce"),bins=[-1,0,2,5,1000],labels=["0","1–2","3–5","6+"])
    aa = dfa.groupby("rango_actividad",observed=False).agg(riesgo_medio=("riesgo_no_progreso_6m","mean")).reset_index()
    fig = px.bar(aa,x="rango_actividad",y="riesgo_medio",color_discrete_sequence=["#0F766E"],title="Actividad reciente × riesgo",
                 labels={"rango_actividad":"Actividad Reciente","riesgo_medio":"Riesgo Medio"})
    aplicar_estilo_figura(fig); st.plotly_chart(fig,use_container_width=True)
    st.markdown("""<div style="margin-top:-4px;margin-bottom:18px;padding:12px 14px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;border-radius:10px;color:#334155;font-size:13px;line-height:1.55;"><strong>Cómo leerlo:</strong> los docentes se agrupan según su actividad reciente (0, 1–2, 3–5 y 6+ actividades) y la barra muestra el riesgo medio. <strong>Qué representa:</strong> la asociación entre participación reciente y riesgo de no progreso. <strong>Para qué sirve:</strong> ayuda a identificar si una mayor actividad reciente coincide con menor riesgo y aporta una señal interpretable para seguimiento.</div>""",unsafe_allow_html=True)


    st.subheader("Exploración de docentes y riesgo")

    f1, f2, f3 = st.columns(3)
    sedes_r = f1.multiselect("Sede ", sorted(df["sede"].dropna().unique()))
    niveles_r = f2.multiselect("Nivel ", sorted(df["nivel_aprobado_corte"].dropna().unique()))
    unidades_r = f3.multiselect("Unidad Académica ", sorted(df["unidad_academica"].dropna().unique()))

    tmp_r = df.copy()
    if sedes_r:
        tmp_r = tmp_r[tmp_r["sede"].isin(sedes_r)]
    if niveles_r:
        tmp_r = tmp_r[tmp_r["nivel_aprobado_corte"].isin(niveles_r)]
    if unidades_r:
        tmp_r = tmp_r[tmp_r["unidad_academica"].isin(unidades_r)]

    tabla_riesgo = tmp_r[[
        "id_docente", "nombre_docente", "sede", "unidad_academica",
        "nivel_aprobado_corte", "probabilidad_progreso_6m", "riesgo_no_progreso_6m"
    ]].sort_values("riesgo_no_progreso_6m", ascending=False).rename(columns={
        "id_docente": "ID Docente",
        "nombre_docente": "Docente",
        "sede": "Sede",
        "unidad_academica": "Unidad Académica",
        "nivel_aprobado_corte": "Nivel Aprobado",
        "probabilidad_progreso_6m": "Probabilidad de Progreso",
        "riesgo_no_progreso_6m": "Riesgo de No Progreso"
    })

    tabla_riesgo["Nivel Aprobado"] = tabla_riesgo["Nivel Aprobado"].map(formato_nivel)
    tabla_riesgo["Probabilidad de Progreso"] = (tabla_riesgo["Probabilidad de Progreso"] * 100).round(1).astype(str) + "%"
    tabla_riesgo["Riesgo de No Progreso"] = (tabla_riesgo["Riesgo de No Progreso"] * 100).round(1).astype(str) + "%"

    st.dataframe(tabla_riesgo, use_container_width=True)

with tab6:
    opciones = (
        df["nombre_docente"].astype(str) + " — " + df["id_docente"].astype(str)
    ).tolist()

    eleccion = st.selectbox("Seleccione un docente", opciones, index=0)
    idx = opciones.index(eleccion)
    r = df.iloc[idx]

    render_kpis([
        ("Probabilidad de Progreso", f"{r['probabilidad_progreso_6m']*100:.1f}%", "success"),
        ("Riesgo de No Progreso", f"{r['riesgo_no_progreso_6m']*100:.1f}%", "danger"),
        ("Nivel Aprobado", formato_nivel(r["nivel_aprobado_corte"]), "primary")
    ])

    st.write({
        "Sede": r["sede"],
        "Unidad Académica": r["unidad_academica"],
        "Cursos Aprobados": int(r["cursos_aprobados_corte"]),
        "Actividades Últimos 90 Días": int(r["actividades_ultimos_90_dias"]),
        "Tasa de Aprobación": f"{float(r['tasa_aprobacion_corte']):.1f}%"
    })

    st.markdown(
        """
        <div style="margin-top:12px;margin-bottom:18px;padding:12px 14px;
                    background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #2563EB;
                    border-radius:10px;color:#334155;font-size:13px;line-height:1.55;">
            <strong>¿Qué hace este simulador?</strong> Permite seleccionar un docente y consultar su resultado predictivo ya calculado:
            probabilidad estimada de progreso, riesgo de no progreso, nivel aprobado y variables formativas relevantes.
            <strong>¿Para qué sirve?</strong> Facilita la revisión de casos individuales y apoya la priorización de seguimiento o acompañamiento.
            <strong>Alcance actual:</strong> consulta predicciones generadas previamente por el modelo seleccionado y no ejecuta inferencia
            para registros nuevos porque esta versión trabaja con el conjunto de docentes ya procesado por el pipeline predictivo.
            La incorporación de inferencia en tiempo real para nuevos docentes o nuevos registros se plantea como una extensión posterior del trabajo.
        </div>
        """,
        unsafe_allow_html=True
    )

footer_tfm()
