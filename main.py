import streamlit as st

st.title("Analyseur de PDF")

st.write("Bienvenue dans ton application Streamlit.")

uploaded_file = st.file_uploader("Télécharger un fichier PDF", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF téléchargé avec succès !")
