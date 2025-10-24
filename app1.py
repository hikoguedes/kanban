import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Kanban Turis Tráfego",
    page_icon="🚗",
    layout="wide"
)

# Arquivo JSON para armazenar os dados
DATA_FILE = "kanban_data.json"

# Inicializar dados
def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "columns": {
                "backlog": {"name": "Backlog", "tasks": []},
                "to_do": {"name": "A Fazer", "tasks": []},
                "in_progress": {"name": "Em Progresso", "tasks": []},
                "review": {"name": "Revisão", "tasks": []},
                "done": {"name": "Concluído", "tasks": []}
            },
            "last_id": 0
        }
        save_data(default_data)
    return load_data()

# Carregar dados do JSON
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return init_data()

# Salvar dados no JSON
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Gerar ID único
def generate_id(data):
    data["last_id"] += 1
    return data["last_id"]

# CSS personalizado
st.markdown("""
<style>
    .kanban-container {
        display: flex;
        gap: 15px;
        padding: 10px 0;
        overflow-x: auto;
        min-height: 650px;
    }
    .kanban-column {
        background: white;
        border-radius: 10px;
        padding: 15px;
        min-width: 280px;
        min-height: 600px;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .column-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1em;
    }
    .task-card {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border-left: 5px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .task-high {
        border-left-color: #ff4b4b;
    }
    .task-medium {
        border-left-color: #ffa500;
    }
    .task-low {
        border-left-color: #00cc66;
    }
    .task-info {
        margin: 8px 0;
        font-size: 0.85em;
        color: #555;
    }
    .task-title {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 8px;
        color: #333;
    }
    .empty-column {
        text-align: center;
        color: #666;
        padding: 40px 20px;
        font-style: italic;
    }
    .action-buttons {
        display: flex;
        gap: 8px;
        margin-top: 10px;
    }
    .move-buttons {
        display: flex;
        gap: 5px;
        margin-top: 10px;
        border-top: 1px solid #f0f0f0;
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚗 Kanban Turis Tráfego")
st.markdown("---")

# Sidebar para adicionar novas tarefas
with st.sidebar:
    st.header("➕ Nova Tarefa")
    
    with st.form("new_task_form", clear_on_submit=True):
        title = st.text_input("Título da Tarefa*")
        description = st.text_area("Descrição")
        priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        assignee = st.text_input("Responsável")
        due_date = st.date_input("Data de Vencimento")
        column = st.selectbox("Coluna", ["Backlog", "A Fazer", "Em Progresso", "Revisão", "Concluído"])
        
        submitted = st.form_submit_button("🎯 Criar Tarefa")
        
        if submitted:
            if title:
                data = load_data()
                new_task = {
                    "id": generate_id(data),
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "assignee": assignee,
                    "due_date": due_date.isoformat() if due_date else None,
                    "created_at": datetime.now().isoformat(),
                    "column": column.lower().replace(" ", "_")
                }
                
                column_key = {
                    "Backlog": "backlog",
                    "A Fazer": "to_do", 
                    "Em Progresso": "in_progress",
                    "Revisão": "review",
                    "Concluído": "done"
                }[column]
                
                data["columns"][column_key]["tasks"].append(new_task)
                save_data(data)
                st.success("✅ Tarefa criada com sucesso!")
                st.rerun()
            else:
                st.error("❌ Título é obrigatório!")

# Função para mover tarefa entre colunas
def move_task(task_id, from_column, to_column):
    data = load_data()
    
    # Encontrar e remover a tarefa da coluna original
    task_to_move = None
    for task in data["columns"][from_column]["tasks"]:
        if task["id"] == task_id:
            task_to_move = task
            break
    
    if task_to_move:
        data["columns"][from_column]["tasks"] = [
            task for task in data["columns"][from_column]["tasks"] 
            if task["id"] != task_id
        ]
        
        # Adicionar à nova coluna
        task_to_move["column"] = to_column
        data["columns"][to_column]["tasks"].append(task_to_move)
        save_data(data)
        st.rerun()

# Função para excluir tarefa
def delete_task(task_id, column_key):
    data = load_data()
    data["columns"][column_key]["tasks"] = [
        task for task in data["columns"][column_key]["tasks"] 
        if task["id"] != task_id
    ]
    save_data(data)
    st.rerun()

# Função para editar tarefa
def edit_task(task_id, current_column):
    data = load_data()
    task = next(
        (t for t in data["columns"][current_column]["tasks"] 
         if t["id"] == task_id), None
    )
    
    if task:
        with st.form(f"edit_task_{task_id}"):
            st.subheader("✏️ Editar Tarefa")
            
            new_title = st.text_input("Título", value=task["title"])
            new_description = st.text_area("Descrição", value=task.get("description", ""))
            new_priority = st.selectbox(
                "Prioridade", 
                ["Alta", "Média", "Baixa"],
                index=["Alta", "Média", "Baixa"].index(task.get("priority", "Média"))
            )
            new_assignee = st.text_input("Responsável", value=task.get("assignee", ""))
            
            due_date = task.get("due_date")
            new_due_date = st.date_input(
                "Data de Vencimento",
                value=datetime.fromisoformat(due_date) if due_date else datetime.now()
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Salvar Alterações"):
                    task.update({
                        "title": new_title,
                        "description": new_description,
                        "priority": new_priority,
                        "assignee": new_assignee,
                        "due_date": new_due_date.isoformat()
                    })
                    save_data(data)
                    st.session_state[f"editing_{task['id']}"] = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state[f"editing_{task['id']}"] = False
                    st.rerun()

# Função para renderizar card da tarefa
def render_task_card(task, column_key, column_index, all_columns):
    priority_class = {
        "Alta": "task-high",
        "Média": "task-medium", 
        "Baixa": "task-low"
    }.get(task.get("priority", "Média"), "task-medium")
    
    # Card container
    with st.container():
        # Título e informações
        st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
        
        # Título
        st.markdown(f'<div class="task-title">{task["title"]}</div>', unsafe_allow_html=True)
        
        # Descrição
        if task.get("description"):
            desc = task['description']
            if len(desc) > 60:
                desc = desc[:60] + "..."
            st.markdown(f'<div class="task-info">📝 {desc}</div>', unsafe_allow_html=True)
        
        # Responsável
        if task.get("assignee"):
            st.markdown(f'<div class="task-info">👤 {task["assignee"]}</div>', unsafe_allow_html=True)
        
        # Data de vencimento
        if task.get("due_date"):
            due_date = datetime.fromisoformat(task["due_date"]).strftime("%d/%m/%Y")
            st.markdown(f'<div class="task-info">📅 {due_date}</div>', unsafe_allow_html=True)
        
        # Prioridade
        st.markdown(f'<div class="task-info">🔸 {task.get("priority", "Média")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️", key=f"edit_{task['id']}", help="Editar", use_container_width=True):
                st.session_state[f"editing_{task['id']}"] = True
        with col2:
            if st.button("🗑️", key=f"delete_{task['id']}", help="Excluir", use_container_width=True):
                delete_task(task["id"], column_key)
        
        # Botões de movimento
        column_keys = list(all_columns.keys())
        col_left, col_right = st.columns(2)
        
        with col_left:
            if column_index > 0:
                prev_column = column_keys[column_index - 1]
                if st.button("←", key=f"left_{task['id']}", 
                           help=f"Mover para {all_columns[prev_column]['name']}",
                           use_container_width=True):
                    move_task(task["id"], column_key, prev_column)
        
        with col_right:
            if column_index < len(column_keys) - 1:
                next_column = column_keys[column_index + 1]
                if st.button("→", key=f"right_{task['id']}", 
                           help=f"Mover para {all_columns[next_column]['name']}",
                           use_container_width=True):
                    move_task(task["id"], column_key, next_column)
        
        # Modal de edição
        if st.session_state.get(f"editing_{task['id']}", False):
            edit_task(task["id"], column_key)

# Renderizar o Kanban
def render_kanban():
    data = load_data()
    
    # Criar colunas
    columns = st.columns(len(data["columns"]))
    
    for idx, (column_key, column_data) in enumerate(data["columns"].items()):
        with columns[idx]:
            # Header da coluna
            st.markdown(
                f'<div class="column-header">{column_data["name"]} ({len(column_data["tasks"])})</div>', 
                unsafe_allow_html=True
            )
            
            # Área de tasks da coluna
            if column_data["tasks"]:
                for task in column_data["tasks"]:
                    # Verificar se está editando
                    if not st.session_state.get(f"editing_{task['id']}", False):
                        render_task_card(task, column_key, idx, data["columns"])
                    else:
                        edit_task(task["id"], column_key)
            else:
                st.markdown(
                    '<div class="empty-column">📭 Nenhuma tarefa</div>', 
                    unsafe_allow_html=True
                )

# Renderizar a aplicação
render_kanban()

# Estatísticas
st.markdown("---")
st.subheader("📊 Estatísticas do Projeto")

data = load_data()
total_tasks = sum(len(col["tasks"]) for col in data["columns"].values())
completed = len(data["columns"]["done"]["tasks"])
in_progress = len(data["columns"]["in_progress"]["tasks"]) + len(data["columns"]["review"]["tasks"])
backlog = len(data["columns"]["backlog"]["tasks"]) + len(data["columns"]["to_do"]["tasks"])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Tarefas", total_tasks)

with col2:
    st.metric("Concluídas", completed)

with col3:
    st.metric("Em Andamento", in_progress)

with col4:
    st.metric("Pendentes", backlog)

with col5:
    progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
    st.metric("Progresso Geral", f"{progress:.1f}%")

# Exportação e limpeza de dados
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configurações")

if st.sidebar.button("📤 Exportar Dados JSON", use_container_width=True):
    with open(DATA_FILE, "r") as f:
        st.sidebar.download_button(
            label="📥 Baixar Arquivo JSON",
            data=f.read(),
            file_name="kanban_turis_trafego.json",
            mime="application/json",
            use_container_width=True
        )

if st.sidebar.button("🔄 Reiniciar Board", use_container_width=True):
    if st.sidebar.confirm("Tem certeza? Todos os dados serão perdidos."):
        init_data()
        st.rerun()

# Instruções
with st.expander("ℹ️ Como usar o Kanban"):
    st.markdown("""
    **🎯 Como mover tarefas:**
    
    **Método 1 - Botões de Movimento:**
    - Use os botões **← →** abaixo de cada card para mover entre colunas
    - **←** Move para coluna anterior  
    - **→** Move para próxima coluna
    
    **📊 Fluxo do Kanban:**
    ```
    Backlog → A Fazer → Em Progresso → Revisão → Concluído
    ```
    
    **🏷️ Sistema de Prioridades:**
    - 🔴 **Vermelho**: Alta prioridade (urgente)
    - 🟡 **Laranja**: Média prioridade (importante)  
    - 🟢 **Verde**: Baixa prioridade (normal)
    
    **✏️ Editar Tarefas:**
    - Clique no botão **✏️** no card
    - Faça as alterações necessárias
    - Clique em **💾 Salvar Alterações**
    
    **🗑️ Excluir Tarefas:**
    - Clique no botão **🗑️** no card
    - A tarefa será removida imediatamente
    
    **➕ Criar Nova Tarefa:**
    - Use o formulário na barra lateral
    - Preencha pelo menos o título
    - Selecione a coluna inicial
    """)

# Inicializar session state para edição
for key in st.session_state.keys():
    if key.startswith('editing_'):
        st.session_state[key] = False