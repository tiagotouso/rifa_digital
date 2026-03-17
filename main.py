import streamlit as st
import pandas as pd
import os

# Configuração da Página
st.set_page_config(page_title="Rifa Digital 🍀", page_icon="🎟️")

DB_FILE = "rifa_dados.csv"

# Função para carregar os números já ocupados do CSV
def carregar_ocupados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        return df['numero'].tolist()
    return []

# Função para salvar a venda no CSV
def salvar_venda(nome, telefone, numero):
    novo_dado = pd.DataFrame([[nome, telefone, numero]], columns=['nome', 'telefone', 'numero'])
    if not os.path.exists(DB_FILE):
        novo_dado.to_csv(DB_FILE, index=False)
    else:
        novo_dado.to_csv(DB_FILE, mode='a', header=False, index=False)

# --- INTERFACE PRINCIPAL ---
st.title("🍀 Rifa Digital")

# Inicializa estados de controle
if 'sucesso' not in st.session_state:
    st.session_state.sucesso = None
if 'temp_numero' not in st.session_state:
    st.session_state.temp_numero = None

# LÓGICA DE EXIBIÇÃO
# Se o usuário JÁ confirmou uma reserva, mostramos APENAS o agradecimento e o PIX
if st.session_state.sucesso:
    reserva = st.session_state.sucesso
    st.balloons()
    st.success(f"🎉 **{reserva['nome']}**, sua reserva do número **{reserva['num']}** foi concluída!")
    
    st.markdown(f"""
    ---
    ### 💸 Pagamento via PIX
    Copie a chave abaixo e cole no seu aplicativo do banco:
    """)
    
    # Substitua pela sua chave real
    chave_pix = "00020101021126330014br.gov.bcb.pix0111suachaveaqui" 
    st.code(chave_pix, language="text")
    
    st.markdown(f"""
    ### Muito obrigado! 🙏✨
    Sua participação foi registrada. Boa sorte! 🎊🍀
    
    *Dica: Envie o comprovante para o organizador.*
    ---
    """)
    
    if st.button("🔄 Fazer outra reserva"):
        st.session_state.sucesso = None
        st.session_state.temp_numero = None
        st.rerun()

else:
    # Se ele ainda NÃO confirmou, mostramos o formulário e a grade
    st.markdown("Preencha os campos abaixo para escolher seu número!")
    
    # PASSO 1: Identificação
    st.subheader("1️⃣ Informe seus dados")
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone / WhatsApp")

    if nome and telefone:
        st.divider()
        
        # PASSO 2: Escolha do Número
        st.subheader("2️⃣ Escolha seu número")
        numeros_ocupados = carregar_ocupados()
        
        if len(numeros_ocupados) >= 25:
            st.error("🎉 A rifa está encerrada! Todos os números foram vendidos.")
        else:
            cols = st.columns(5)
            for i in range(1, 26):
                col_idx = (i - 1) % 5
                with cols[col_idx]:
                    if i in numeros_ocupados:
                        st.button(f"❌", key=f"btn_{i}", disabled=True, use_container_width=True)
                    else:
                        tipo_botao = "primary" if st.session_state.temp_numero == i else "secondary"
                        if st.button(f"{i}", key=f"btn_{i}", type=tipo_botao, use_container_width=True):
                            st.session_state.temp_numero = i

            # PASSO 3: Botão de Confirmação Final
            if st.session_state.temp_numero:
                st.info(f"Número selecionado: **{st.session_state.temp_numero}**")
                if st.button("✅ CONFIRMAR E GERAR PIX", use_container_width=True):
                    salvar_venda(nome, telefone, st.session_state.temp_numero)
                    st.session_state.sucesso = {"nome": nome, "num": st.session_state.temp_numero}
                    st.rerun()




# import streamlit as st
# import pandas as pd
# import os

# # Configuração da Página
# st.set_page_config(page_title="Rifa Digital 🍀", page_icon="🎟️")

# DB_FILE = "rifa_dados.csv"

# # Função para carregar os números já ocupados do CSV
# def carregar_ocupados():
#     if os.path.exists(DB_FILE):
#         df = pd.read_csv(DB_FILE)
#         return df['numero'].tolist()
#     return []

# # Função para salvar a venda no CSV
# def salvar_venda(nome, telefone, numero):
#     novo_dado = pd.DataFrame([[nome, telefone, numero]], columns=['nome', 'telefone', 'numero'])
#     if not os.path.exists(DB_FILE):
#         novo_dado.to_csv(DB_FILE, index=False)
#     else:
#         novo_dado.to_csv(DB_FILE, mode='a', header=False, index=False)

# # --- INTERFACE PRINCIPAL ---
# st.title("🍀 Rifa Digital")
# st.markdown("Preencha os campos abaixo para participar!")

# # PASSO 1: Identificação
# st.subheader("1️⃣ Informe seus dados")
# nome = st.text_input("Nome Completo")
# telefone = st.text_input("Telefone / WhatsApp")

# if nome and telefone:
#     st.divider()
    
#     # PASSO 2: Escolha do Número
#     st.subheader("2️⃣ Escolha seu número")
#     numeros_ocupados = carregar_ocupados()
    
#     if len(numeros_ocupados) >= 25:
#         st.error("🎉 A rifa está encerrada! Todos os números foram vendidos.")
#     else:
#         # Criar a grade de botões
#         cols = st.columns(5)
        
#         # Inicializa o estado do número selecionado se não existir
#         if 'temp_numero' not in st.session_state:
#             st.session_state.temp_numero = None

#         for i in range(1, 26):
#             col_idx = (i - 1) % 5
#             with cols[col_idx]:
#                 if i in numeros_ocupados:
#                     st.button(f"❌", key=f"btn_{i}", disabled=True, use_container_width=True)
#                 else:
#                     # Se o número for o selecionado no momento, destaca o botão
#                     tipo_botao = "primary" if st.session_state.temp_numero == i else "secondary"
#                     if st.button(f"{i}", key=f"btn_{i}", type=tipo_botao, use_container_width=True):
#                         st.session_state.temp_numero = i

#         # PASSO 3: Botão de Confirmação
#         if st.session_state.temp_numero:
#             st.markdown(f"### Você selecionou o número: **{st.session_state.temp_numero}**")
#             if st.button("✅ CONFIRMAR RESERVA", use_container_width=True):
#                 # Grava no CSV apenas agora
#                 salvar_venda(nome, telefone, st.session_state.temp_numero)
#                 st.session_state.sucesso = {"nome": nome, "num": st.session_state.temp_numero}
#                 st.session_state.temp_numero = None # Limpa seleção temporária
#                 st.rerun()

# # PASSO 4: Tela Final de Agradecimento e PIX
# if 'sucesso' in st.session_state:
#     reserva = st.session_state.sucesso
#     st.divider()
    
#     st.success(f"🎉 **{reserva['nome']}**, sua reserva foi concluída!")
#     st.balloons()
    
#     st.markdown(f"""
#     ### 🎟️ Seu número: **{reserva['num']}**
    
#     ---
#     ### 💸 Pagamento via PIX
#     Copie a chave abaixo e cole no seu banco:
#     """)
    
#     # Chave PIX Exemplo
#     chave_pix = "00020101021126330014br.gov.bcb.pix0111suachaveaqui" 
#     st.code(chave_pix, language="text")
    
#     st.markdown(f"""
#     ### Muito obrigado! 🙏✨
#     Boa sorte! Não esqueça de enviar o comprovante ao organizador. 🎊🍀
#     """)
    
#     if st.button("Fazer outra reserva"):
#         del st.session_state.sucesso
#         st.rerun()