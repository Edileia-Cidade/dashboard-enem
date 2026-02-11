import streamlit as st
import pandas as pd
from datetime import datetime

# ======================
# CONFIGURAÇÃO DA PÁGINA
# ======================
st.set_page_config(
    page_title="Dashboard ENEM Medicina",
    page_icon="📊",
    layout="wide"
)

# ======================
# FUNÇÃO PARA CARREGAR DADOS
# ======================
@st.cache_data
def carregar_dados():
    arquivo = "Planilha_ENEM_Medicina_Preenchida_4_Semanas.xlsx"

    controle = pd.read_excel(arquivo, sheet_name="Controle da Semana")
    erros = pd.read_excel(arquivo, sheet_name="Caderno de Erros")
    revisoes = pd.read_excel(arquivo, sheet_name="Revisões")

    # Ajuste de nomes
    controle.columns = controle.columns.str.strip()
    controle = controle.rename(columns={"Matéria Foco": "Matéria"})

    # Datas BR
    controle["Data"] = pd.to_datetime(controle["Data"], dayfirst=True)
    revisoes["Revisão 24h"] = pd.to_datetime(revisoes["Revisão 24h"], dayfirst=True)
    revisoes["Revisão 7 dias"] = pd.to_datetime(revisoes["Revisão 7 dias"], dayfirst=True)
    revisoes["Revisão 30 dias"] = pd.to_datetime(revisoes["Revisão 30 dias"], dayfirst=True)

    return controle, erros, revisoes

# ======================
# BOTÃO ATUALIZAR DADOS
# ======================
col_btn, _ = st.columns([2, 8])
with col_btn:
    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.experimental_rerun()

# ======================
# CARREGAR DADOS
# ======================
controle, erros, revisoes = carregar_dados()
hoje = pd.to_datetime(datetime.today().date())

# ======================
# TÍTULO
# ======================
st.title("📊 Dashboard de Estudos – ENEM Medicina")

# ======================
# KPIs BONITOS
# ======================
total_horas = controle["Tempo (h)"].sum()
total_questoes = controle["Questões Feitas"].sum()
total_acertos = controle["Acertos"].sum()
taxa_acerto = (total_acertos / total_questoes) * 100 if total_questoes > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("⏱️ Horas Estudadas", f"{total_horas:.1f}")
c2.metric("📝 Questões", int(total_questoes))
c3.metric("✅ Acertos", int(total_acertos))
c4.metric("📈 Aproveitamento", f"{taxa_acerto:.1f}%")

# ======================
# DESEMPENHO POR MATÉRIA (COM CORES)
# ======================
st.subheader("📚 Desempenho por Matéria")

desempenho = controle.groupby("Matéria")[["Questões Feitas", "Acertos"]].sum()
desempenho["Taxa (%)"] = (desempenho["Acertos"] / desempenho["Questões Feitas"]) * 100

def cor_taxa(val):
    if val >= 70:
        return "background-color: #c6f6d5"  # verde
    elif val >= 50:
        return "background-color: #fefcbf"  # amarelo
    else:
        return "background-color: #fed7d7"  # vermelho

st.dataframe(
    desempenho.style
    .format({"Taxa (%)": "{:.1f}%"})
    .applymap(cor_taxa, subset=["Taxa (%)"])
)

# ======================
# ALERTAS DE REVISÃO
# ======================
st.subheader("⏰ Alertas de Revisão")

def status_revisao(data):
    if data < hoje:
        return "🔴 Atrasada"
    elif data == hoje:
        return "🟡 Hoje"
    else:
        return "🟢 Em dia"

revisoes["24h"] = revisoes["Revisão 24h"].apply(status_revisao)
revisoes["7d"] = revisoes["Revisão 7 dias"].apply(status_revisao)
revisoes["30d"] = revisoes["Revisão 30 dias"].apply(status_revisao)

st.dataframe(
    revisoes[
        ["Matéria", "Assunto",
         "Revisão 24h", "24h",
         "Revisão 7 dias", "7d",
         "Revisão 30 dias", "30d"]
    ]
)

# ======================
# ALERTA GERAL (CHAMADA DE ATENÇÃO)
# ======================
atrasadas = revisoes[
    (revisoes["24h"] == "🔴 Atrasada") |
    (revisoes["7d"] == "🔴 Atrasada") |
    (revisoes["30d"] == "🔴 Atrasada")
]

if not atrasadas.empty:
    st.error(f"⚠️ Você tem {len(atrasadas)} revisões ATRASADAS!")
else:
    st.success("🎉 Nenhuma revisão atrasada! Continue assim!")

# ======================
# CADERNO DE ERROS (VISUAL)
# ======================
st.subheader("❌ Caderno de Erros")

col_e1, col_e2 = st.columns(2)

with col_e1:
    st.write("Tipos de erro")
    st.bar_chart(erros["Tipo de Erro (Conteúdo/Leitura/Distração)"].value_counts())

with col_e2:
    st.write("Assuntos que mais erram")
    st.bar_chart(erros["Assunto"].value_counts())

st.caption("Dashboard inteligente – estudos orientados por dados 🚀")

