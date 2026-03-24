import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
st.set_page_config(page_title="🍀 Rifa Digital da Cecília 🍀", page_icon="🎟️", layout="centered")

# Cria a pasta data se não existir
if not os.path.exists("data"):
    os.makedirs("data")

DB_FILE = "data/rifa_dados.csv"

# --- FUNÇÕES ---
def carregar_ocupados():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            return df['numero'].tolist()
        except:
            return []
    return []

def salvar_venda(nome, telefone, numero):
    # --- ALTERAÇÃO CRUCIAL: Verificação de segurança ---
    # Recarregamos os dados do arquivo no momento exato do clique para checar duplicidade
    ocupados_agora = carregar_ocupados()
    
    if numero in ocupados_agora:
        return False  # Bloqueia a venda se o número já foi levado
    
    # Se estiver livre, prossegue com o salvamento
    novo_dado = pd.DataFrame([[nome, telefone, numero]],
                             columns=['nome', 'telefone', 'numero'])
    
    if not os.path.exists(DB_FILE):
        novo_dado.to_csv(DB_FILE, index=False)
    else:
        novo_dado.to_csv(DB_FILE, mode='a', header=False, index=False)
    return True

# --- ESTADO INICIAL ---
if "step" not in st.session_state:  
    st.session_state.step = 1

if "numero" not in st.session_state:
    st.session_state.numero = None

if "dados" not in st.session_state:
    st.session_state.dados = {"nome": "", "telefone": ""}

if "dados_travados" not in st.session_state:
    st.session_state.dados_travados = False

# --- HEADER ---
st.title("🍀 Rifa Digital da Cecília 🍀")
st.caption("Escolha seu número e participe!")

progresso = st.session_state.step / 4
st.progress(progresso)

# =========================
# STEP 1 - DADOS
# =========================
if st.session_state.step == 1:
    st.subheader("👤 1. Seus dados")

    nome = st.text_input(
        "Nome completo",
        value=st.session_state.dados.get("nome", ""),
        disabled=st.session_state.dados_travados
    )

    telefone = st.text_input(
        "WhatsApp",
        value=st.session_state.dados.get("telefone", ""),
        disabled=st.session_state.dados_travados
    )

    if st.button("Continuar ➡️", use_container_width=True):
        if nome and telefone:
            st.session_state.dados = {"nome": nome, "telefone": telefone}
            st.session_state.dados_travados = True
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

# =========================
# STEP 2 - ESCOLHER NÚMERO
# =========================
elif st.session_state.step == 2:
    st.subheader("🎯 2. Escolha seu número")
    
    nome = st.session_state.dados.get("nome")
    telefone = st.session_state.dados.get("telefone")
    st.info(f"👤 {nome} | 📱 {telefone}")

    numeros_ocupados = carregar_ocupados()
    cols = st.columns(5)

    for i in range(1, 26):
        col_idx = (i - 1) % 5
        with cols[col_idx]:
            if i in numeros_ocupados:
                st.button("❌", disabled=True, key=f"num_{i}", use_container_width=True)
            else:
                tipo = "primary" if st.session_state.numero == i else "secondary"
                if st.button(f"{i}", key=f"num_{i}", type=tipo, use_container_width=True):
                    st.session_state.numero = i

    if st.session_state.numero:
        st.success(f"Selecionado: **{st.session_state.numero}**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Voltar", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("Continuar ➡️", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

# =========================
# STEP 3 - PAGAMENTO
# =========================
elif st.session_state.step == 3:
    st.subheader("💸 3. Pagamento")
    st.info(f"🎟️ Número: {st.session_state.numero}")
    st.code("d3c59165-6dc8-4a07-b487-18d1a1f1cac5")

    # Criamos uma variável para controlar o erro fora das colunas
    erro_duplicado = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("✅ Já paguei", use_container_width=True):
            sucesso = salvar_venda(
                st.session_state.dados["nome"],
                st.session_state.dados["telefone"],
                st.session_state.numero
            )
            
            if sucesso:
                st.session_state.step = 4
                st.rerun()
            else:
                # Se falhar, avisamos o estado do erro para exibir fora da coluna
                st.session_state.conflito_numero = True

    # EXIBIÇÃO FORA DAS COLUNAS (LINHA INTEIRA)
    if st.session_state.get("conflito_numero", False):
        st.error("⚠️ Sinto muito! Este número acabou de ser reservado por outra pessoa.")
        if st.button("Escolher outro número", use_container_width=True):
            st.session_state.numero = None
            st.session_state.step = 2
            st.session_state.conflito_numero = False # Limpa o erro
            st.rerun()

# =========================
# STEP 4 - SUCESSO
# =========================
elif st.session_state.step == 4:
    st.balloons()
    st.success(f"🎉 Reserva confirmada para {st.session_state.dados['nome']}!")

    if st.button("🔄 Escolher outro número", use_container_width=True):
        st.session_state.step = 1
        st.session_state.numero = None
        st.session_state.dados_travados = False 
        st.rerun()


