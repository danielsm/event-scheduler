import streamlit as st
import sqlite3
from collections import defaultdict
import pandas as pd
import plotly.express as px


# Function to load CSS from a file
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("styles.css")


# Inicializar o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('event_preferences.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS preferences
                 (user_name TEXT, date TEXT, time TEXT, UNIQUE(user_name, date, time))''')
    conn.commit()
    return conn

# Inicializar o banco de dados
conn = init_db()

# Definir as datas e horários do evento
event_schedule = {
    "Quinta-feira 24/04/2025": ["8:00", "9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "Sexta-feira 25/04/2025": ["8:00", "9:00", "10:00", "11:00"],
    "Segunda-feira 28/04/2025": ["8:00", "9:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "Terça-feira 29/04/2025": ["8:00", "9:00", "10:00", "11:00"],
}


# Título do aplicativo
st.title("Agendador de Eventos")

st.markdown("### Marcação Defesa de Doutorado Daniel de Sousa Moraes")

# Campo de entrada para o nome do usuário

user_name = st.text_input("DIGITE SEU NOME:", key="user_name")

# Verificar se o usuário já enviou preferências
user_preferences = []
if user_name:
    user_preferences = conn.execute(
        "SELECT date, time FROM preferences WHERE user_name = ?", (user_name,)
    ).fetchall()

# # Exibir as preferências atuais do usuário
# if user_name and user_preferences:
#     st.write(f"**Preferências atuais de {user_name}:**")
#     for date, time in user_preferences:
#         st.write(f"- {date} às {time}")

# Formulário de entrada do usuário
with st.form("preference_form"):
    st.write("#### Escolha a data e o horário preferidos para o evento:")
    
    # Exibir as datas horizontalmente e os horários verticalmente abaixo de cada data
    cols = st.columns(len(event_schedule))  # Criar colunas para cada data
    selected_times = {}  # Para armazenar os horários selecionados para cada data
    
    for i, (date, times) in enumerate(event_schedule.items()):
        with cols[i]:
            st.write(f"##### {date}")  # Exibir a data como um cabeçalho
            selected_times[date] = []
            for time in times:
                # Pré-selecionar as caixas de seleção se o usuário já votou nesta data e horário
                is_checked = (date, time) in user_preferences
                if st.checkbox(f"{time}", key=f"{date}_{time}", value=is_checked):
                    selected_times[date].append(time)
    
    # Botão de envio
    submitted = st.form_submit_button("Enviar/Atualizar Preferência")
    
    if submitted:
        if user_name:
            # Limpar as preferências anteriores deste usuário
            conn.execute("DELETE FROM preferences WHERE user_name = ?", (user_name,))
            conn.commit()
            
            # Armazenar as preferências do usuário
            for date, times in selected_times.items():
                for time in times:
                    conn.execute("INSERT INTO preferences (user_name, date, time) VALUES (?, ?, ?)",
                                 (user_name, date, time))
            conn.commit()
            st.success(f"Obrigado, {user_name}! Suas preferências foram atualizadas.")
        else:
            st.error("Por favor, insira seu nome.")

# Exibir as preferências atuais
#st.write("### Preferências Atuais")
all_preferences = conn.execute("SELECT user_name, date, time FROM preferences").fetchall()
df = pd.DataFrame(all_preferences, columns=["Usuário", "Data", "Horário"])

# Combinar Data e Horário em uma única coluna para melhor visualização
df["Data_Horário"] = df["Data"] + " " + df["Horário"]

# Criar uma tabela dinâmica para contar os votos por usuário para cada data e horário
pivot_table = df.pivot_table(index="Data_Horário", columns="Usuário", aggfunc="size", fill_value=0)

# Plotar os votos usando Plotly
if not pivot_table.empty:
    st.write("### Visualização dos Votos por Usuário")
    
    # Criar um gráfico de barras interativo com Plotly
    fig = px.bar(
        pivot_table,
        orientation="h",
        labels={"value": "Número de Votos", "index": "Data e Horário"},
        title="Preferências do Evento por Usuário",
        color_discrete_sequence=px.colors.qualitative.Plotly,  # Usar uma paleta de cores elegante
    )
    
    # Personalizar o layout do gráfico
    fig.update_layout(
        xaxis_title="Número de Votos",
        yaxis_title="Data e Horário",
        legend_title="Usuários",
        barmode="stack",  # Barras empilhadas
        hovermode="y unified",  # Exibir informações ao passar o mouse
    )
    
    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Determinar a data e o horário final do evento
# if st.button("Calcular Data e Horário Final do Evento"):
#     max_votes = -1
#     best_date, best_time = None, None
    
#     for date, time, votes in all_preferences:
#         if votes > max_votes:
#             max_votes = votes
#             best_date = date
#             best_time = time
    
#     if best_date and best_time:
#         st.success(f"### Data e Horário Final do Evento: **{best_date} às {best_time}**")
#     else:
#         st.warning("Nenhuma preferência foi enviada ainda.")