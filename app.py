
import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
st.set_page_config(page_title="Rifa Digital 🍀", page_icon="🎟️", layout="centered")

DB_FILE = "data/rifa_dados.csv"

# --- FUNÇÕES ---
def carregar_ocupados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df['numero'].tolist()
    return []

def salvar_venda(nome, telefone, numero):
    novo_dado = pd.DataFrame([[nome, telefone, numero]],
                             columns=['nome', 'telefone', 'numero'])
    if not os.path.exists(DB_FILE):
        novo_dado.to_csv(DB_FILE, index=False)
    else:
        novo_dado.to_csv(DB_FILE, mode='a', header=False, index=False)

# --- ESTADO ---
if "step" not in st.session_state:
    st.session_state.step = 1

if "numero" not in st.session_state:
    st.session_state.numero = None

if "dados" not in st.session_state:
    st.session_state.dados = {}

# --- HEADER ---
st.title("🍀 Rifa Digital")
st.caption("Escolha seu número e participe!")

# Barra de progresso
progresso = st.session_state.step / 4
st.progress(progresso)

# =========================
# STEP 1 - DADOS
# =========================
if st.session_state.step == 1:
    st.subheader("👤 1. Seus dados")

    nome = st.text_input("Nome completo")
    telefone = st.text_input("WhatsApp")

    if st.button("Continuar ➡️", use_container_width=True):
        if nome and telefone:
            st.session_state.dados = {
                "nome": nome,
                "telefone": telefone
            }
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

# =========================
# STEP 2 - ESCOLHER NÚMERO
# =========================
elif st.session_state.step == 2:
    st.subheader("🎯 2. Escolha seu número")

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
        st.success(f"Você escolheu o número **{st.session_state.numero}**")

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

    nome = st.session_state.dados["nome"]
    numero = st.session_state.numero

    st.info(f"👤 {nome} | 🎟️ Número: {numero}")

    st.markdown("### PIX para pagamento")

    chave_pix = "00020101021126330014br.gov.bcb.pix0111suachaveaqui"
    st.code(chave_pix)

    st.caption("Após o pagamento, confirme abaixo.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Voltar", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

    with col2:
        if st.button("✅ Já paguei", use_container_width=True):
            salvar_venda(
                st.session_state.dados["nome"],
                st.session_state.dados["telefone"],
                st.session_state.numero
            )
            st.session_state.step = 4
            st.rerun()

# =========================
# STEP 4 - SUCESSO
# =========================
elif st.session_state.step == 4:
    st.balloons()
    st.success("🎉 Reserva confirmada!")

    st.markdown(f"""
    ### Obrigado, {st.session_state.dados['nome']}! 🙌

    Seu número: **{st.session_state.numero}**

    Boa sorte! 🍀
    """)

    if st.button("🔄 Fazer nova reserva", use_container_width=True):
        st.session_state.step = 1
        st.session_state.numero = None
        st.session_state.dados = {}
        st.rerun()

