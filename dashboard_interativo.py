import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Educacional - Versão 4",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# ESTILO
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
.card {
    background-color: #111827;
    border: 1px solid #374151;
    border-radius: 14px;
    padding: 18px;
}
.exec-box {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# FUNÇÕES
# -----------------------------
@st.cache_data
def carregar_dados(arquivo):
    df = pd.read_excel(arquivo)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    for col in ["nivel", "turma", "serie", "menor_nota"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "nota_media" in df.columns:
        df["nota_media"] = pd.to_numeric(df["nota_media"], errors="coerce")

    return df


def valor_seguro(valor):
    if pd.isna(valor):
        return "-"
    return f"{valor:.2f}"


def classificar(media):
    if pd.isna(media):
        return "Sem dados"
    if media >= 7:
        return "🟢 Bom"
    elif media >= 5:
        return "🟡 Atenção"
    return "🔴 Crítico"


def moda(df, col):
    if col in df.columns:
        s = df[col].dropna()
        if not s.empty:
            return s.value_counts().idxmax()
    return "N/A"


# -----------------------------
# TÍTULO
# -----------------------------
st.title("📊 Dashboard Executivo Escolar")

# -----------------------------
# CARREGAMENTO
# -----------------------------
arquivo = st.sidebar.file_uploader("Planilha", type=["xlsx"])

if arquivo:
    df = carregar_dados(arquivo)
else:
    try:
        df = carregar_dados("base_consolidada.xlsx")
    except:
        st.error("Arquivo não encontrado")
        st.stop()

if "nota_media" not in df.columns:
    st.error("Coluna nota_media não encontrada")
    st.write(df.columns)
    st.stop()

df_f = df.copy()

# -----------------------------
# MÉTRICAS
# -----------------------------
media = df_f["nota_media"].mean()
maior = df_f["nota_media"].max()
menor = df_f["nota_media"].min()

nivel = moda(df_f, "nivel")
dificuldade = moda(df_f, "menor_nota")

melhor = "N/A"
pior = "N/A"

if "turma" in df_f.columns:
    temp = df_f.groupby("turma")["nota_media"].mean().dropna().sort_values()
    if not temp.empty:
        pior = temp.index[0]
        melhor = temp.index[-1]

# -----------------------------
# CONCLUSÃO
# -----------------------------
st.markdown(f"""
<div class="exec-box">
<b>Resumo:</b><br>
Média geral: <b>{valor_seguro(media)}</b><br>
Nível predominante: <b>{nivel}</b><br>
Melhor turma: <b>{melhor}</b><br>
Pior turma: <b>{pior}</b><br>
Disciplina crítica: <b>{dificuldade}</b>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# CARDS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Alunos", len(df_f))
c2.metric("Média", valor_seguro(media))
c3.metric("Maior", valor_seguro(maior))
c4.metric("Menor", valor_seguro(menor))

st.divider()

# -----------------------------
# GRÁFICOS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if "nivel" in df_f.columns:
        fig = px.bar(df_f["nivel"].value_counts().reset_index(),
                     x="nivel", y="count",
                     title="Níveis")
        st.plotly_chart(fig, width="stretch")

with col2:
    fig = px.histogram(df_f, x="nota_media", nbins=20)
    st.plotly_chart(fig, width="stretch")

# -----------------------------
# TURMAS
# -----------------------------
if "turma" in df_f.columns:
    ranking = df_f.groupby("turma")["nota_media"].mean().sort_values(ascending=False).reset_index()

    fig = px.bar(ranking, x="turma", y="nota_media", text_auto=".2f")
    st.plotly_chart(fig, width="stretch")

    st.dataframe(ranking, width="stretch")

# -----------------------------
# BASE
# -----------------------------
st.dataframe(df_f, width="stretch")

csv = df_f.to_csv(index=False).encode("utf-8-sig")
st.download_button("Baixar CSV", csv, "dados.csv")
