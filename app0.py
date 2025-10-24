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

# Classes CSS personalizadas
st.markdown("""
<style>
    .kanban-column {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        min-height: 600px;
    }
    .task-card {
        background-color: white;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .task-high {
        border-left-color: #ff4b4b !important;
    }
    .task-medium {
        border-left-color: #ffa500 !important;
    }
    .task-low {
        border-left-color: #00cc66 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚗 Kanban Turis Tráfego")
st.markdown("---")

# Sidebar para adicionar novas tarefas
with st.sidebar:
    st.header("➕ Nova Tarefa")
    
    with st.form("new_task_form"):
        title = st.text_input("Título da Tarefa*")
        description = st.text_area("Descrição")
        priority = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
        assignee = st.text_input("Responsável")
        due_date = st.date_input("Data de Vencimento")
        column = st.selectbox("Coluna", ["Backlog", "A Fazer", "Em Progresso", "Revisão", "Concluído"])
        
        submitted = st.form_submit_button("Criar Tarefa")
        
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
                st.success("Tarefa criada com sucesso!")
                st.rerun()
            else:
                st.error("Título é obrigatório!")

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

# Função para editar tarefa
def edit_task(task_id, current_column):
    data = load_data()
    task = next(
        (t for t in data["columns"][current_column]["tasks"] 
         if t["id"] == task_id), None
    )
    
    if task:
        with st.form(f"edit_task_{task_id}"):
            st.subheader("Editar Tarefa")
            
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
                if st.form_submit_button("💾 Salvar"):
                    task.update({
                        "title": new_title,
                        "description": new_description,
                        "priority": new_priority,
                        "assignee": new_assignee,
                        "due_date": new_due_date.isoformat()
                    })
                    save_data(data)
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
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

# Layout do Kanban
data = load_data()
columns = st.columns(len(data["columns"]))

for idx, (column_key, column_data) in enumerate(data["columns"].items()):
    with columns[idx]:
        # Header da coluna
        st.subheader(f"{column_data['name']} ({len(column_data['tasks'])})")
        
        # Container da coluna
        with st.container():
            st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
            
            for task in column_data["tasks"]:
                # Card da tarefa
                priority_class = {
                    "Alta": "task-high",
                    "Média": "task-medium", 
                    "Baixa": "task-low"
                }.get(task.get("priority", "Média"), "task-medium")
                
                st.markdown(f'<div class="task-card {priority_class}">', unsafe_allow_html=True)
                
                # Informações da tarefa
                st.write(f"**{task['title']}**")
                
                if task.get("description"):
                    st.write(f"📝 {task['description'][:50]}..." 
                           if len(task.get("description", "")) > 50 
                           else f"📝 {task['description']}")
                
                if task.get("assignee"):
                    st.write(f"👤 {task['assignee']}")
                
                if task.get("due_date"):
                    due_date = datetime.fromisoformat(task["due_date"]).strftime("%d/%m/%Y")
                    st.write(f"📅 {due_date}")
                
                st.write(f"🔸 {task.get('priority', 'Média')}")
                
                # Botões de ação
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("✏️", key=f"edit_{task['id']}", help="Editar"):
                        st.session_state[f"editing_{task['id']}"] = True
                
                with col2:
                    if st.button("🗑️", key=f"delete_{task['id']}", help="Excluir"):
                        delete_task(task["id"], column_key)
                
                with col3:
                    # Botão de mover para direita
                    if column_key != "done":
                        next_columns = list(data["columns"].keys())
                        current_index = next_columns.index(column_key)
                        if current_index < len(next_columns) - 1:
                            next_column = next_columns[current_index + 1]
                            if st.button("→", key=f"move_{task['id']}", help=f"Mover para {data['columns'][next_column]['name']}"):
                                move_task(task["id"], column_key, next_column)
                
                # Modal de edição
                if st.session_state.get(f"editing_{task['id']}", False):
                    edit_task(task["id"], column_key)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Estatísticas
st.markdown("---")
st.subheader("📊 Estatísticas")

total_tasks = sum(len(col["tasks"]) for col in data["columns"].values())
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Tarefas", total_tasks)

with col2:
    completed = len(data["columns"]["done"]["tasks"])
    st.metric("Concluídas", completed)

with col3:
    in_progress = len(data["columns"]["in_progress"]["tasks"])
    st.metric("Em Progresso", in_progress)

with col4:
    backlog = len(data["columns"]["backlog"]["tasks"])
    st.metric("Backlog", backlog)

# Botão para exportar dados
if st.sidebar.button("📤 Exportar Dados JSON"):
    with open(DATA_FILE, "r") as f:
        st.sidebar.download_button(
            label="Baixar JSON",
            data=f.read(),
            file_name="kanban_turis_trafego.json",
            mime="application/json"
        )

# Botão para limpar todos os dados
if st.sidebar.button("🗑️ Limpar Todos os Dados"):
    if st.sidebar.confirm("Tem certeza? Esta ação não pode ser desfeita."):
        init_data()
        st.rerun()