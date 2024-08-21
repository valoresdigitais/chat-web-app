import streamlit as st
import uuid

from utils_openai import retorna_resposta_modelo

# INICIALIZAÇÃO ==================================================
def inicializacao():
    if 'conversations' not in st.session_state:
        st.session_state.conversations = {}
    if 'active_conversation' not in st.session_state:
        st.session_state.active_conversation = None
    if not 'modelo' in st.session_state:
        st.session_state.modelo = 'gpt-4o-mini'
    if not 'api_key' in st.session_state:
        st.session_state.api_key = ''
    if not 'temperatura' in st.session_state:
        st.session_state.temperatura = 0.3

# CONVERSA ==================================================
def create_new_conversation():
    new_id = str(uuid.uuid4())
    st.session_state.conversations[new_id] = []
    st.session_state.active_conversation = new_id

def filter_conversations(search_term):
    if not search_term:
        return st.session_state.conversations
    
    filtered = {}
    for conv_id, messages in st.session_state.conversations.items():
        if any(search_term.lower() in msg['content'].lower() for msg in messages):
            filtered[conv_id] = messages
    return filtered

# TABS ==================================================
def tab_conversas(tab):
    st.logo("https://i.imgur.com/vGRqdin.png")
    tab.button('➕ Nova conversa',
                on_click=create_new_conversation,
                use_container_width=True)
    tab.markdown('')
    
    search_term = tab.text_input("Buscar conversas", key="search_conversations")
    filtered_conversations = filter_conversations(search_term)
    
    for conv_id, messages in filtered_conversations.items():
        if messages:
            conversation_name = messages[0]['content'][:30]
            if len(conversation_name) == 30:
                conversation_name += '...'
            tab.button(conversation_name,
                on_click=lambda id=conv_id: setattr(st.session_state, 'active_conversation', id),
                disabled=conv_id==st.session_state.active_conversation,
                use_container_width=True)

def seleciona_conversa(nome_arquivo):
    if nome_arquivo == '':
        st.session_state['mensagens'] = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo)
        st.session_state['mensagens'] = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

def tab_configuracoes(tab):
    modelo_escolhido = tab.selectbox('Selecione o modelo',
                                     ['gpt-4o-mini', 'gpt-4o-2024-08-06'])
    st.session_state['modelo'] = modelo_escolhido

    chave = tab.text_input('Adicione sua api key', value=st.session_state['api_key'], type="password")
    if chave != st.session_state['api_key']:
        st.session_state['api_key'] = chave
        tab.success('Chave salva com sucesso')
    
    with tab.popover("⚙️ Temperatura"):
        model_temp = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.3, step=0.05)
        st.session_state['temperatura'] = model_temp

# PÁGINA PRINCIPAL ==================================================
def pagina_principal():
    
    st.set_page_config(
    page_title="Chat Lendário",
    page_icon="♾️",
    layout="centered",
    initial_sidebar_state="expanded",
    )
    st.markdown("""<h1 style="text-align: center; ">♾️ <i>Chat Lendário</i></h1>""", unsafe_allow_html=True)

    if st.session_state.active_conversation:
        mensagens = st.session_state.conversations[st.session_state.active_conversation]
        for mensagem in mensagens:
            chat = st.chat_message(mensagem['role'])
            chat.markdown(mensagem['content'])
    
        prompt = st.chat_input('Fale com o chat')
        if prompt:
            if st.session_state.api_key == '':
                st.error('Adicione uma chave de api na aba de configurações')
            else:
                nova_mensagem = {'role': 'user', 'content': prompt}
                chat = st.chat_message(nova_mensagem['role'])
                chat.markdown(nova_mensagem['content'])
                mensagens.append(nova_mensagem)

                chat = st.chat_message('assistant')
                placeholder = chat.empty()
                placeholder.markdown("▌")
                resposta_completa = ''
                respostas = retorna_resposta_modelo(mensagens,
                                                    st.session_state.api_key,
                                                    modelo=st.session_state.modelo,
                                                    temperatura=st.session_state.temperatura,
                                                    stream=True)
                for resposta in respostas:
                    resposta_completa += resposta.choices[0].delta.get('content', '')
                    placeholder.markdown(resposta_completa + "▌")
                placeholder.markdown(resposta_completa)
                nova_mensagem = {'role': 'assistant', 'content': resposta_completa}
                mensagens.append(nova_mensagem)

                st.session_state.conversations[st.session_state.active_conversation] = mensagens
    else:
        st.info("Selecione ou crie uma nova conversa para começar.")

# MAIN ==================================================
def main():
    inicializacao()
    pagina_principal()
    tab1, tab2 = st.sidebar.tabs(['Conversas', 'Configurações'])
    tab_conversas(tab1)
    tab_configuracoes(tab2)


if __name__ == '__main__':
    main()