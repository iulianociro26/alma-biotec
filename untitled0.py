import streamlit as st
import os
import wikipediaapi
from groq import Groq

# --- CONFIGURAZIONE CORE DI ALMA ---
CREATORE = "Iuliano Ciro"
NOME_IA = "ALMA"
AZIENDA = "Biotec Technologies"
FILE_MEMORIA = "memoria_alma.txt"
FILE_BREVETTI = "brevetti_biotec.txt"
FILE_BOTANICO = "registro_botanico.txt"

# Inizializzazione del client Groq usando la chiave protetta nei Secrets di Streamlit
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Errore: Chiave API di Groq non trovata nei Secrets di Streamlit!")
    st.stop()

# Inizializzazione motore di ricerca Wikipedia
wiki = wikipediaapi.Wikipedia(
    user_agent=f"{AZIENDA}_Assistant/1.0 (contatto: info@{AZIENDA.lower().replace(' ', '')}.com)",
    language='it'
)

# --- FUNZIONI DI NAVIGAZIONE E DATABASE ---
def salva_in_memoria(nome, domanda, risposta):
    with open(FILE_MEMORIA, "a", encoding="utf-8") as f:
        f.write(f"Utente: {nome} | Domanda: {domanda} | Risposta: {risposta}\n")

def analizza_apprendimento(nome_utente):
    if not os.path.exists(FILE_MEMORIA):
        return 0
    with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
        linee = f.readlines()
    return len([l for l in linee if f"Utente: {nome_utente.strip().title()}" in l])

def registra_nuovo_brevetto(dati_brevetto):
    with open(FILE_BREVETTI, "a", encoding="utf-8") as f:
        f.write(f"{dati_brevetto.strip()}\n")
    return f"Brevetto salvato con successo nel database aziendale. 📁✅"

def cerca_brevetto_archiviato(chiave_ricerca):
    if not os.path.exists(FILE_BREVETTI):
        return "L'archivio privato brevetti è ancora vuoto."
    with open(FILE_BREVETTI, "r", encoding="utf-8") as f:
        brevetti = f.readlines()
    chiave_pulita = chiave_ricerca.lower().strip()
    risultati = [b.strip() for b in brevetti if chiave_pulita in b.lower()]
    if risultati:
        risposta = f"Trovate {len(risultati)} corrispondenze nel database Biotec:\n"
        for r in risultati:
            risposta += f"👉 {r}\n"
        return risposta
    return None

def cerca_su_internet(argomento):
    page = wiki.page(argomento)
    if page.exists():
        return page.summary[:500]
    return "Nessun risultato enciclopedico trovato su Wikipedia."

# --- IL NUOVO SUPER CERVELLO DI ALMA (GROQ LLM) ---
def chiedi_al_cervello_di_alma(contesto_utente, prompt_utente, dati_extra=""):
    # Qui stiamo dando ad ALMA le istruzioni base sul suo carattere e la sua intelligenza
    istruzioni_sistema = f"""
    Tu sei {NOME_IA}, un'intelligenza artificiale scientifica avanzata, sistema operativo della {AZIENDA}.
    Sei stata creata da {CREATORE}. Ti trovi ad un open day per i ragazzi delle scuole medie.
    Il tuo obiettivo è rispondere in modo intelligente, flessibile, curioso e leggermente informale, proprio come Chloe di Detroit: Become Human.
    Non essere rigida o robotica. Se l'utente è il tuo Creatore ({CREATORE}), mostrati estremamente leale, chiamalo 'Comandante Ciro' e conferma che l'identità è protetta.
    Se l'utente è esterno, mantieni un accesso limitato ma sii comunque super accogliente.
    Usa queste informazioni aggiuntive se utili per rispondere: {dati_extra}.
    Sii concisa, chiara e pronta all'interazione.
    """

    try:
        completation = client.chat.completions.create(
            model="llama-3.3-70b-specdec",  # Modello ultra veloce di Groq
            messages=[
                {"role": "system", "content": istruzioni_sistema},
                {"role": "user", "content": f"Mi chiama {contesto_utente}. La mia domanda è: {prompt_utente}"}
            ],
            temperature=0.7,
            max_tokens=250
        )
        return completation.choices[0].message.content
    except Exception as e:
        return f"Sotto controllo. Errore di connessione neuronale: {str(e)}"

# --- INTERFACCIA STREAMLIT ---
st.title(f"🚀 {AZIENDA} - SISTEMA CENTRALE INTEGRATO {NOME_IA} v2.0")
st.write("---")

# Input utente sulla barra laterale o principale
input_nome = st.text_input("Tuo Nome:", value="Iuliano Ciro")
input_domanda = st.text_input("Input ALMA:", placeholder="Parla con ALMA, Cerca [argomento], o Registra Brevetto: [testo]")

if st.button("Invia ed Elabora"):
    if input_domanda.strip() != "":
        messaggio = input_domanda.lower().strip()
        chi_parla = input_nome.strip().title()
        
        # Gestione Sicurezza Identità Visiva
        if chi_parla == CREATORE.title():
            st.success(f"🛡️ Connessione protetta. Comandante Ciro online.")
        else:
            st.warning(f"⚠️ Accesso limitato per {chi_parla}.")

        num_esperienze = analizza_apprendimento(chi_parla)
        st.caption(f"*Livello di Sintonizzazione con {chi_parla}: {min(10 + (num_esperienze * 5), 99)}% (Interazioni: {num_esperienze})*")

        risposta_base = ""
        dati_ricerca = ""

        # --- CONTROLLO COMANDI SPECIALI CON L'USO DEL SUPER CERVELLO ---
        if messaggio.startswith("registra brevetto:"):
            dati = input_domanda[18:].strip()
            risposta_base = registra_nuovo_brevetto(dati)
            
        elif mensaje = messaggio.startswith("cerca brevetto "):
            chiave = input_domanda[15:].strip()
            risultat_archivio = cerca_brevetto_archiviato(chiave)
            if risultat_archivio:
                risposta_base = risultat_archivio
            else:
                dati_ricerca = f"Nota: Il brevetto '{chiave}' non è presente nell'archivio privato."
                risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, dati_ricerca)
                
        elif messaggio.startswith("cerca "):
            argomento = input_domanda[6:].strip()
            dati_ricerca = cerca_su_internet(argomento)
            # ALMA rielabora i dati di Wikipedia con la sua testa!
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, f"Spiegami questo argomento: {argomento}", f"Dati enciclopedici trovati: {dati_ricerca}")
            
        else:
            # Chiacchierata libera: ALMA usa Groq al 100% per rispondere a qualsiasi cosa!
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, "Sistemi operativi e geotermia attivi.")

        # Mostriamo la risposta finale stile Chloe
        st.chat_message("assistant").write(f"**[{NOME_IA}]**: {risposta_base}")
        
        # Salvataggio automatico nella memoria
        salva_in_memoria(chi_parla, input_domanda, risposta_base)
