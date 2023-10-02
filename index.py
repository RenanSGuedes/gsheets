import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
from PIL import Image
import time

business = Image.open('./images/business.jpg')
# Função para atualizar os números dinamicamente
def update_numbers():
    p, n = st.empty(), st.empty()
    
    for i in range(11):
        # Atualize apenas a parte numérica do texto
        number = f"{i * 10}%"
        
        p.progress(int(number.replace('%', "")))
        n.write(f"Progresso: {number}")
        time.sleep(.4)

# Crie uma conexão com a planilha do Google Sheets.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Execute uma consulta SQL na planilha do Google Sheets.
# Use st.cache_data para executar novamente somente quando a consulta mudar ou após 10 minutos.
@st.cache_resource(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
sheet_url_login = st.secrets["private_gsheets_url_login"]

query = f'SELECT * FROM "{sheet_url}"'
query_login = f'SELECT * FROM "{sheet_url_login}"'

rows = run_query(query)
rows_login = run_query(query_login)

# Converter os dados em um DataFrame.
df = pd.DataFrame(rows, columns=["Pessoa de Comercial", "Pessoa CS", "Empresa", "Perfil da Empresa", "Site da Empresa", "Dados de Contratação", "Local de Instalação", "Tipo do Projeto", "Expectativa do Cliente", "Valor do Projeto", "Duração do Projeto", "Data de Instalação da Armadilha", "Logo"])

colX, colY = st.columns([1, 1])

# Variável de controle de login
logged_in = False

placeholder = st.empty()

if not logged_in:

    with placeholder.container():
        colS, colT = st.columns([3, 2])

        colS.title("👋 Bem vindo(a)!")
        colS.subheader("Acesse a plataforma")
        email = colS.text_input(":email: Digite seu e-mail:", placeholder="Digite seu e-mail de acesso")
        pw = colS.text_input(":nine: PIN de acesso:", type="password", placeholder="Digite seu PIN de acesso", value=None)
        colT.image(business)

        if colS.button(":arrow_forward: Login"):
            update_numbers()
    
            if email == rows_login[0].User and int(pw) == int(rows_login[0].Password):
                logged_in = True
            else:
                st.error(":exclamation: Usuário ou senha incorreto(s)")

if logged_in:
    if colX.button("Logout"):
        logged_in = False

if logged_in:
    st.balloons()
    st.success(":white_check_mark: Usuário autenticado")
    # Exiba os dados em contêineres individuais.
    for index, row in df.iterrows():
        with st.expander("Cliente", expanded=True):
            st.subheader(row["Empresa"])

            st.write(f"**Pessoa de comercial:** {row['Pessoa de Comercial']}")
            st.write(f"**Pessoa de CS:** {row['Pessoa CS']}")
            st.markdown("---")

            col1, col2 = st.columns([3, 1])

            col2.image(row["Logo"])
            col1.write("**Perfil da Empresa**")
            col1.write(f"*{row['Perfil da Empresa']}*")
            col1.write(f"**Site:** {row['Site da Empresa']}")
            col1.write(f"**Dados de contratação**")
            col1.write(f"{row['Dados de Contratação']}")

    placeholder.empty()