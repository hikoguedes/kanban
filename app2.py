import streamlit as st
import json
import os
import uuid
from streamlit_kanban_board_goviceversa import kanban_board # Componente em uso

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Kanban Board Dinâmico")

FILE_PATH = "kanban_data.json"

# --- Cores/Prioridades para o Kanban ---
PRIORITY_COLORS = {
    "Alta": "#FF6347",  # Vermelho
    "Média": "#FFD700", # Amarelo
    "Baixa": "#3CB371", # Verde
    "Nenhuma": "#A9A9A9", # Cinza
}

# --- Funções de JSON (Salvar e Carregar) ---

def load_data():
    """Carrega os dados do arquivo JSON ou retorna um modelo padrão."""
    # A lista de colunas ainda é necessária para os SELECTBOXES no Streamlit!
    # Mas o componente kanban pode não precisar dela diretamente.
    default_columns = [
        {"id": "TODO", "title": "🛠 A Fazer"},
        {"id": "DEV", "title": "⚙️ Em Desenvolvimento"},
        {"id": "TEST", "title": "🔍 Em Teste"},
        {"id": "REVIEW", "title": "🧐 Para Revisão"},
        {"id": "DONE", "title": "✅ Concluído"},
    ]
    
    default_cards = [
        {"id": str(uuid.uuid4()), "title": "Criar Design Moderno", "description": "Usar CSS para um visual dinâmico.", "column_id": "TODO", "priority": "Alta", "color": PRIORITY_COLORS["Alta"]},
        {"id": str(uuid.uuid4()), "title": "Implementar Drag-and-Drop", "description": "Usar o componente Kanban.", "column_id": "DEV", "priority": "Média", "color": PRIORITY_COLORS["Média"]},
        {"id": str(uuid.uuid4()), "title": "Testar Funcionalidades JSON", "description": "Verificar se o salvamento está correto.", "column_id": "TEST", "priority": "Baixa", "color": PRIORITY_COLORS["Baixa"]},
    ]
    
    default_data = {
        "columns": default_columns,
        "cards": default_cards
    }
    
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "columns" in data and "cards" in data:
                    # Trata cards antigos que não têm cor (para compatibilidade)
                    for card in data["cards"]:
                        if "color" not in card:
                            card["color"] = PRIORITY_COLORS.get(card.get("priority", "Nenhuma"), PRIORITY_COLORS["Nenhuma"])
                    return data
        except json.JSONDecodeError:
            st.warning("Arquivo JSON corrompido ou vazio. Usando dados padrão.")
            pass # Continua para retornar dados padrão
    
    return default_data

def save_data(data):
    """Salva os dados atuais no arquivo JSON."""
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    st.session_state.data = data

# --- Inicialização ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- Mapeamento para Widgets do Streamlit ---
# Usamos a lista de colunas do JSON para criar os SELECTBOXES
COLUMNS_MAP = {col["id"]: col["title"] for col in st.session_state.data["columns"]}
COLUMN_IDS = list(COLUMNS_MAP.keys())

# --- Layout do Streamlit ---
st.title("Board Kanban Ágil (Streamlit)")
st.markdown("Arraste e solte os cards entre as colunas. Use o botão 'Salvar' para persistir os dados.")

# ⚠️ CORREÇÃO DO ERRO 'TypeError':
# Removemos o argumento 'columns' e passamos os cards para o parâmetro 'items'
# (ou para o primeiro parâmetro posicional, o que é mais comum em componentes)
try:
    updated_cards = kanban_board(
        items=st.session_state.data["cards"],  # Passa apenas os cards, com column_id
        column_titles=COLUMNS_MAP,             # O componente pode precisar de um mapeamento de IDs para Títulos
        key="kanban_board_1",
        # Configurações de estilo (manter estilos pode exigir o uso de kwargs válidos)
        # Vamos manter apenas os essenciais. Se o erro persistir, remova os estilos.
    )

    # Verifica se a chamada retornou algo e se é diferente do estado atual
    if updated_cards is not None and updated_cards != st.session_state.data["cards"]:
        # Se o componente retornar a lista de cards atualizada, salvamos ela
        st.session_state.data["cards"] = updated_cards
        # Não precisa de rerun, pois o Streamlit atualiza após a interação com o componente.

except TypeError as e:
    st.error(f"Erro ao chamar o componente kanban_board. Verifique a documentação para os argumentos corretos. Detalhes: {e}")
    # Se o erro for 'unexpected keyword argument', você deve renomear 'items' ou 'column_titles'.
    # A estrutura atual é uma aposta baseada em componentes populares.
    updated_cards = None # Garante que o fluxo continue

# --- Criação de Novo Card (Com Prioridade/Cor) ---

st.sidebar.header("Novo Card")
with st.sidebar.form("new_card_form", clear_on_submit=True):
    new_title = st.text_input("Título do Card", max_chars=50)
    new_description = st.text_area("Descrição", max_chars=200)
    
    new_priority_name = st.selectbox("Prioridade", options=list(PRIORITY_COLORS.keys()))
    
    new_col_id = st.selectbox(
        "Coluna Inicial",
        options=COLUMN_IDS,
        format_func=lambda x: COLUMNS_MAP[x]
    )
    submitted = st.form_submit_button("Adicionar Card")

    if submitted and new_title:
        new_id = str(uuid.uuid4())
        
        new_card = {
            "id": new_id,
            "title": new_title,
            "description": new_description,
            "column_id": new_col_id,
            "priority": new_priority_name,
            "color": PRIORITY_COLORS[new_priority_name]
        }
        st.session_state.data["cards"].append(new_card)
        st.experimental_rerun() # Recarrega para que o novo card apareça no board

# --- Lógica de Edição e Remoção (Inalterada) ---

st.sidebar.header("Gerenciar Cards")
card_titles = {card["id"]: card["title"] for card in st.session_state.data["cards"]}

if card_titles:
    # Cria uma lista de opções para o selectbox, mas usa o título para mostrar
    options_list = list(card_titles.keys())
    
    # Adiciona uma opção nula para evitar KeyErrors ao remover o último card
    options_list.insert(0, None) 
    
    card_to_edit_id = st.sidebar.selectbox(
        "Selecionar Card para Editar/Remover",
        options=options_list,
        format_func=lambda x: card_titles[x] if x else "--- Selecione um Card ---"
    )

    if card_to_edit_id:
        card_index = next(i for i, card in enumerate(st.session_state.data["cards"]) if card["id"] == card_to_edit_id)
        current_card = st.session_state.data["cards"][card_index]

        st.sidebar.subheader(f"Editar Card: {current_card['title']}")
        with st.sidebar.form("edit_card_form"):
            edited_title = st.text_input("Novo Título", value=current_card["title"])
            edited_description = st.text_area("Nova Descrição", value=current_card["description"])
            
            # Edição de Prioridade
            current_priority = current_card.get("priority", "Nenhuma") 
            edited_priority = st.selectbox("Nova Prioridade", options=list(PRIORITY_COLORS.keys()), index=list(PRIORITY_COLORS.keys()).index(current_priority))
            
            col1, col2 = st.columns([1, 1])
            with col1:
                save_edit_button = st.form_submit_button("Salvar Edição")
            with col2:
                # O delete_button deve ser um widget que aciona uma ação, fora do form para evitar reset do form
                pass 
            
            # Botão de remoção fora do formulário para evitar problemas de reset
            delete_button_key = f"delete_btn_{card_to_edit_id}"
            delete_button = st.button("Remover Card", key=delete_button_key, type="primary")


        if save_edit_button:
            st.session_state.data["cards"][card_index]["title"] = edited_title
            st.session_state.data["cards"][card_index]["description"] = edited_description
            st.session_state.data["cards"][card_index]["priority"] = edited_priority
            st.session_state.data["cards"][card_index]["color"] = PRIORITY_COLORS[edited_priority]
            
            st.success(f"Card '{edited_title}' atualizado!")
            st.experimental_rerun()

        if delete_button:
            st.session_state.data["cards"].pop(card_index)
            st.warning(f"Card '{current_card['title']}' removido!")
            st.experimental_rerun()
else:
    st.sidebar.info("Não há cards para editar.")


# Botão de salvar no JSON
if st.button("💾 Salvar Dados em JSON"):
    save_data(st.session_state.data)
    st.success("Dados salvos em kanban_data.json com sucesso!")

st.caption(f"Dados atuais em `{FILE_PATH}`:")
st.json(st.session_state.data)