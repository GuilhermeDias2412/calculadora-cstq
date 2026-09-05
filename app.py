import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Precificação CSTQJr", layout="wide")
st.title("📊 Calculadora de Precificação - CSTQJr")

# 2. Banco de Dados de Serviços
SERVICOS = {
    "Consultoria em Conservação": {"horas": 40, "lab": 0.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Estudo Legislativo": {"horas": 30, "lab": 0.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Estudo Bibliográfico": {"horas": 35, "lab": 0.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Manual de Boas Práticas": {"horas": 50, "lab": 0.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Otimização Lab/Indústria": {"horas": 60, "lab": 0.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Rotulagem Nutricional": {"horas": 25, "lab": 0.0, "P": 1.0, "M": 1.8, "G": 3.0},
    "Prototipagem": {"horas": 80, "lab": 400.0, "P": 1.0, "M": 2.0, "G": 3.5},
    "Análise de Água": {"horas": 15, "lab": 400.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Análise Físico-Química": {"horas": 20, "lab": 400.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Análise Alimentícia": {"horas": 20, "lab": 400.0, "P": 1.0, "M": 1.5, "G": 2.5},
    "Caracterização de Amostra": {"horas": 25, "lab": 400.0, "P": 1.0, "M": 1.5, "G": 2.5}
}

CUSTO_HORA = 8.00
TAXA_EJ = 0.15

# 3. Carrinho de Orçamentos
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# 4. Interface de Controles
col1, col2 = st.columns([1, 2])
with col1:
    margem_lucro = st.slider("Margem de Lucro Desejada (%)", min_value=20, max_value=85, value=50, step=5) / 100.0

st.markdown("---")

# Legenda de Tamanhos adicionada aqui
st.info("""
**Guia de Dimensionamento de Projetos:**
* **P (Pequeno):** Escopo reduzido. Ideal para demandas pontuais, 1 produto ou análises simples.
* **M (Médio):** Escopo padrão. Complexidade moderada, múltiplas amostras ou estudos aprofundados.
* **G (Grande):** Escopo amplo. Alta complexidade, linhas de produção inteiras ou muitos pontos de coleta.
""")

# Formulário para adicionar serviços
with st.form("form_adicionar"):
    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
    servico_sel = c1.selectbox("Serviço", list(SERVICOS.keys()))
    tamanho_sel = c2.selectbox("Tamanho do Projeto", ["P", "M", "G"])
    qte_sel = c3.number_input("Quantidade", min_value=1, value=1, step=1)
    btn_add = c4.form_submit_button("➕ Adicionar Serviço")

    if btn_add:
        st.session_state.carrinho.append({"Serviço": servico_sel, "Tamanho": tamanho_sel, "Quantidade": qte_sel})
        st.success("Adicionado ao orçamento!")

if st.button("🗑️ Limpar Orçamento"):
    st.session_state.carrinho = []
    st.rerun()

# 5. Lógica de Cálculo e Exibição Visual
if st.session_state.carrinho:
    resultados = []
    totais = {"horas": 0, "custos": 0, "lucro": 0, "preco": 0}

    for item in st.session_state.carrinho:
        s = SERVICOS[item["Serviço"]]
        mult = s[item["Tamanho"]]
        qte = item["Quantidade"]
        
        horas = s["horas"] * mult * qte
        c_lab = s["lab"] * mult * qte
        c_op = horas * CUSTO_HORA
        c_tot = c_op + c_lab
        
        divisor = 1 - margem_lucro - TAXA_EJ
        preco = c_tot / divisor if divisor > 0 else c_tot
        lucro = preco - c_tot - (preco * TAXA_EJ)
        
        resultados.append({
            "Qtd": qte,
            "Serviço": f"{item['Serviço']} ({item['Tamanho']})",
            "Horas": f"{horas:.1f}h",
            "Custos CSTQJr": f"R$ {c_tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Lucro Líquido": f"R$ {lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Preço ao Cliente": f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        })
        
        totais["horas"] += horas
        totais["custos"] += c_tot
        totais["lucro"] += lucro
        totais["preco"] += preco

    st.table(pd.DataFrame(resultados))
    
    st.markdown("### 💰 Resumo Geral da Proposta")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Horas Totais", f"{totais['horas']:.1f} h")
    m2.metric("Custos (Lab + Op)", f"R$ {totais['custos']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m3.metric("Lucro Líquido", f"R$ {totais['lucro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    m4.metric("PREÇO FINAL", f"R$ {totais['preco']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
