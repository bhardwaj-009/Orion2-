
import streamlit as st
import pandas as pd
import datetime as dt
from fpdf import FPDF
import io
from streamlit_option_menu import option_menu

st.set_page_config(page_title="CarService ORION", layout="wide")

# Logo
st.image("orion_logo.png", width=180)
st.title("CarService ORION - Sistema Completo")

# Menu moderno
with st.sidebar:
    menu = option_menu(
        "Menu",
        ["Login", "Inserimento", "Dashboard", "Report"],
        icons=["person", "pencil-square", "bar-chart", "file-earmark-pdf"],
        menu_icon="cast", default_index=2
    )

# Inizializzazione dati
if "dati" not in st.session_state:
    st.session_state.dati = []

# Login (semplificato)
if menu == "Login":
    st.subheader("Login Utente")
    username = st.text_input("Nome utente")
    password = st.text_input("Password", type="password")
    utenti = {"admin": "admin123", "operaio1": "pwd1"}
    if st.button("Login"):
        if utenti.get(username) == password:
            st.success("Accesso effettuato con successo")
        else:
            st.error("Credenziali errate")

# Inserimento giornaliero
elif menu == "Inserimento":
    st.subheader("Inserimento Giornata di Lavoro")
    with st.form("form"):
        nome = st.selectbox("Nome Operaio", ["Marco", "Saeed", "Qasim", "Najib", "Hikmat", "Musa", "Khalil", "Ashraf", "Sumit", "Khalid"])
        targa = st.text_input("Targa Macchina")
        data = st.date_input("Data", dt.date.today())
        ora_inizio = st.time_input("Ora Inizio")
        ora_fine = st.time_input("Ora Fine")
        pausa_inizio = st.time_input("Inizio Pausa")
        pausa_fine = st.time_input("Fine Pausa")
        km_inizio = st.number_input("Km Inizio", min_value=0)
        km_fine = st.number_input("Km Fine", min_value=0)
        guadagno = st.number_input("Guadagno (€)", min_value=0.0)
        invia = st.form_submit_button("Salva")
        if invia:
            ore = (dt.datetime.combine(dt.date.today(), ora_fine) - dt.datetime.combine(dt.date.today(), ora_inizio)).seconds / 3600
            pausa = (dt.datetime.combine(dt.date.today(), pausa_fine) - dt.datetime.combine(dt.date.today(), pausa_inizio)).seconds / 3600
            ore_lavorate = max(0, round(ore - pausa, 2))
            km = max(0, km_fine - km_inizio)
            st.session_state.dati.append({
                "Data": data,
                "Nome": nome,
                "Targa": targa,
                "Ore Lavorate": ore_lavorate,
                "Km": km,
                "Guadagno": guadagno
            })
            st.success("Giornata salvata!")

# Dashboard
elif menu == "Dashboard":
    st.subheader("Dashboard")
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        contratti = {
            "Marco": 160, "Saeed": 160, "Qasim": 100, "Najib": 160, "Hikmat": 160,
            "Musa": 160, "Khalil": 160, "Ashraf": 40, "Sumit": 160, "Khalid": 40
        }
        totali = df.groupby("Nome").agg({
            "Ore Lavorate": "sum",
            "Km": "sum",
            "Guadagno": "sum"
        }).reset_index()
        totali["Target"] = totali["Nome"].map(contratti)
        totali["Stato"] = totali.apply(lambda x: "✅ OK" if abs(x["Ore Lavorate"] - x["Target"]) < 1 else ("🔺 Sopra" if x["Ore Lavorate"] > x["Target"] else "🔻 Sotto"), axis=1)
        st.dataframe(totali)

        st.bar_chart(totali.set_index("Nome")[["Ore Lavorate", "Target"]])
    else:
        st.warning("Nessun dato disponibile.")

# Report
elif menu == "Report":
    st.subheader("Report PDF e CSV")
    if st.session_state.dati:
        df = pd.DataFrame(st.session_state.dati)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Scarica CSV", data=csv, file_name="report_orion.csv", mime="text/csv")

        def crea_pdf(df):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Report CarService ORION", ln=True, align="C")
            pdf.ln(10)
            for i, row in df.iterrows():
                pdf.cell(0, 8, f"{row['Data']} - {row['Nome']}: {row['Ore Lavorate']}h, {row['Km']}km, €{row['Guadagno']:.2f}", ln=True)
            buffer = io.BytesIO()
            pdf.output(buffer)
            return buffer.getvalue()

        pdf_bytes = crea_pdf(df)
        st.download_button("⬇️ Scarica PDF", data=pdf_bytes, file_name="report_orion.pdf", mime="application/pdf")
    else:
        st.info("Nessun dato disponibile.")
