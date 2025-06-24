#client = genai.Client(api_key="AIzaSyCHHSeMS0VsSGwO5RoWsb9ALVwomz65ODs")
import streamlit as st
import random
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Inicializa el cliente de Gemini
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


# Estilo personalizado global
st.markdown("""
    <style>
        .chat-container {
            max-height: 600px;  /* Altura fija, puedes ajustar */
            overflow-y: auto;
            padding: 10px;
            border-radius: 12px;
            background-color: #fafafa;
            margin-bottom: 15px;
        }
        .refran-card {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            margin-top: 20px;
            margin-bottom: 30px;
        }
        .chat-bubble-user {
            background-color: #f0f2f6;
            color: #333;
            padding: 10px 10px;
            border-radius: 18px;
            margin: 8px 0;
            max-width: 80%;
            float: right;
            clear: both;
        }
        .chat-bubble-gemini {
            background-color: #f0f2f6;
            color: #333;
            padding: 20px 20px;
            border-radius: 18px;
            margin: 8px 0;
            max-width: 80%;
            float: left;
            clear: both;
        }
        
        .chat-input-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            border: 1px solid #ddd;
        }

        /* Input expandible, con estilo */
        .chat-input-container input {
            flex-grow: 1;
            font-style: italic;
            padding: 10px 15px;
            border-radius: 10px;
            border: 1px solid #ccc;
            background-color: #fff;
            font-size: 16px;
            height: 42px; /* altura igual al botón */
            box-sizing: border-box;
        }

        /* Botón con estilo y tamaño igual altura input */
        .chat-input-container button {
            color: white;
            border: none;
            padding: 0 20px;
            height: 42px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s ease;
        }

        .chat-input-container button:hover {
            background-color: #367be3;
        }
            
        /* Style the label */
        [data-baseweb="select"] > label {
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 8px;
        }
        
        [data-baseweb="select"] input {
            color:orange;
            border-radius: 10px;
            padding: 10px 8px;
        }

        /* DropDown filter */
        [data-baseweb="select"] {
            border-radius: 10px;
        }

        /* Cajitas filtros & botón reset*/
        [data-baseweb="select"] [role="button"] {
            background-color: #2c3e50; 
            font-color:#2c3e50;
            border-radius: 10px ;
            padding: 2px 8px ;
            font-weight: 00 ;
        }

        /* Style the placeholder text */
        [data-baseweb="select"] input::placeholder {
            font-style: italic;
            color: #a3b1c2;
        }
    </style>
""", unsafe_allow_html=True)

# CARGA DEL CSV
@st.cache_data
def cargar_refranes(ruta_csv):
    df = pd.read_csv(ruta_csv, delimiter=";")
    return df

df_refranes = cargar_refranes(r"C:\Users\teresa.mattil\OneDrive - Accenture\Desktop\refranero_español.csv")

# FILTRO DE CATEGORÍAS
categorias_unicas = sorted(df_refranes["Categoría"].dropna().unique().tolist())

if "filtro_categorias" not in st.session_state:
    st.session_state.filtro_categorias = categorias_unicas

st.multiselect(
    "Filtra por categoría:",
    options=categorias_unicas,
    default=st.session_state.filtro_categorias,
    key="filtro_categorias"
)

# Filtrar según selección
df_filtrado = df_refranes[df_refranes["Categoría"].isin(st.session_state.filtro_categorias)]

# Elegir refrán al inicio
if "refran_seleccionado" not in st.session_state or "chat" not in st.session_state:
    if not df_filtrado.empty:
        st.session_state.refran_seleccionado = random.choice(df_filtrado["refran"].dropna().tolist())

# MOSTRAR REFRÁN CON ESTILO
st.markdown(f"""
    <div class="refran-card">
        <h2 style='text-align: center;'>Refrán del Día</h2>
        <p style='text-align: center; font-size: 20px; font-style: italic; color: #333;'>“{st.session_state.refran_seleccionado}”</p>
    </div>
""", unsafe_allow_html=True)

# CREAR GEMINI SOLO UNA VEZ
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash")

# Botón explicación
if st.button("🧠 Generar explicación"):
    prompt = f"Genera una explicación breve del refrán: \"{st.session_state.refran_seleccionado}\", y dame 1 ejemplo de uso en una frase normal"
    response = st.session_state.chat.send_message(prompt)
    st.session_state.historial = [("Gemini", response.text)]

# MOSTRAR HISTORIAL
if "historial" in st.session_state:
    chat_html = "<div class='chat-container'>"

    for rol, mensaje in st.session_state.historial:
        if rol == "Usuario":
            chat_html += f"<div class='chat-bubble-user'>{mensaje}</div>"
        elif rol == "Gemini":
            chat_html += f"<div class='chat-bubble-gemini'>{mensaje}</div>"

    chat_html += "</div>"

    st.markdown(chat_html, unsafe_allow_html=True)


    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([7,1])
        with col1:
            user_input = st.text_input("", placeholder="Escribe algo...", key="input_chat", label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Enviar")

    if submitted and user_input:
        st.session_state.historial.append(("Usuario", user_input))
        st.session_state.historial.append(("Gemini", "⏳ Pensando..."))
        st.rerun()

    if st.session_state.historial and st.session_state.historial[-1] == ("Gemini", "⏳ Pensando..."):
        last_user_msg = None
        for rol, msg in reversed(st.session_state.historial[:-1]):
            if rol == "Usuario":
                last_user_msg = msg
                break

        if last_user_msg:
            respuesta = st.session_state.chat.send_message(last_user_msg)
            st.session_state.historial[-1] = ("Gemini", respuesta.text)
            st.rerun()

# BOTÓN NUEVO REFRÁN
if st.button("🔄 Nuevo refrán"):
    df_filtrado = df_refranes[df_refranes["Categoría"].isin(st.session_state.filtro_categorias)]

    if not df_filtrado.empty:
        st.session_state.refran_seleccionado = random.choice(df_filtrado["refran"].dropna().tolist())
        st.session_state.chat = client.chats.create(model="gemini-2.5-flash")
        st.session_state.pop("historial", None)
        st.rerun()
    else:
        st.warning("⚠️ No hay refranes disponibles con las categorías seleccionadas.")
