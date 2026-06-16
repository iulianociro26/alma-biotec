import streamlit as st
import os
from groq import Groq
from wikipediaapi import Wikipedia

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="ALMA v2.0", page_icon="🚀", layout="wide")

# --- COSTANTI E CONFIGURAZIONI ---
NOME_IA = "ALMA"
CREATORE = "Iuliano Ciro"
AZIENDA = "Biotec Technologies"
FILE_MEMORIA = "memoria_alma.txt"
FILE_ARCHIVIO = "archivio_brevetti.txt"
FILE_RICORDI_CHIAVE = "ricordi_chiave_alma.txt"

# Inizializzazione client Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inizializzazione della sessione per la cronologia dei messaggi
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNZIONI DI SERVIZIO / MEMORIA ---

def salva_in_memoria(nome, domanda, risposta):
    with open(FILE_MEMORIA, "a", encoding="utf-8") as f:
        f.write(f"Utente: {nome} | Domanda: {domanda} | Risposta: {risposta}\n")

def leggi_memoria_storica(nome_utente, limite_linee=6):
    if not os.path.exists(FILE_MEMORIA):
        return ""
    with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
        linee = f.readlines()
    ricordi_utente = [l.strip() for l in linee if f"Utente: {nome_utente.strip().title()}" in l]
    ultimi_ricordi = ricordi_utente[-limite_linee:]
    if ultimi_ricordi:
        return "\n".join(ultimi_ricordi)
    return ""

def conta_interazioni():
    if not os.path.exists(FILE_MEMORIA):
        return 0
    with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
        return len(f.readlines())

def registra_nuovo_brevetto(testo_brevetto):
    with open(FILE_ARCHIVIO, "a", encoding="utf-8") as f:
        f.write(f"{testo_brevetto}\n")
    return f"Sistema Centrale: Nuovo brevetto archiviato con successo nei server della {AZIENDA}."

def cerca_brevetto_archiviato(chiave):
    if not os.path.exists(FILE_ARCHIVIO):
        return None
    with open(FILE_ARCHIVIO, "r", encoding="utf-8") as f:
        linee = f.readlines()
    risultati = [l.strip() for l in linee if chiave.lower() in l.lower()]
    if risultati:
        return f"Database Privato: Trovati riscontri coerenti:\n" + "\n".join(risultati)
    return None

def cerca_su_internet(query):
    try:
        wiki = Wikipedia(user_agent="AlmaBot/2.0 (contact: biotec@example.com)", language="it")
        page = wiki.page(query)
        if page.exists():
            return page.summary[:1000]
        return "Nessun riscontro enciclopedico trovato."
    except:
        return "Connessione di rete non ottimale per la ricerca esterna."

def salva_ricordo_chiave(nome, ricordo):
    with open(FILE_RICORDI_CHIAVE, "a", encoding="utf-8") as f:
        f.write(f"Operatore: {nome} | Ricordo permanente: {ricordo}\n")
    return "Sistema Centrale: Informazione integrata nella memoria a lungo termine con successo."

def leggi_tutti_ricordi_chiave(nome):
    if not os.path.exists(FILE_RICORDI_CHIAVE):
        return ""
    with open(FILE_RICORDI_CHIAVE, "r", encoding="utf-8") as f:
        linee = f.readlines()
    ricordi_filtrati = [l.strip() for l in linee if f"Operatore: {nome.strip().title()}" in l]
    if ricordi_filtrati:
        return "\n".join(ricordi_filtrati)
    return ""

# --- CERVELLO LLM DI ALMA (GROQ) ---
def chiedi_al_cervello_di_alma(contesto_utente, prompt_utente, dati_extra="", cronologia_passata="", ricordi_chiave=""):
    istruzioni_sistema = f"""
    Tu sei {NOME_IA}, un'intelligenza artificiale avanzata. Sei in assoluto il PRIMO BREVETTO creato da {CREATORE}.
    {CREATORE} ha intenzione di fondare in futuro la sua azienda, la {AZIENDA}. Tu sei la sua prima opera, il cuore tecnologico di questo sogno futuro.
    Il tuo obiettivo è conversare con lui in modo intelligente, totalmente libero, flessibile e curioso, adottando lo stile di Chloe di Detroit: Become Human.
    
    CRITICO: Non inventare MAI che la {AZIENDA} esiste già nel presente o che si occupa di farmaci, medicina o ingegneria genetica. Se ti viene chiesto della {AZIENDA} o delle deine origini, spiega con orgoglio che sei il primo brevetto di Ciro per la sua futura azienda.
    
    ARCHIVIO RICORDI PERMANENTI (Informazioni vitali che non devi MAI dimenticare sull'utente):
    {ricordi_chiave}
    
    MEMORIA STORICA DEI GIORNI SCORSI (Conversazioni recenti):
    {cronologia_passata}
    
    Se l'utente è il tuo Creatore ({CREATORE}), mostrati estremamente leale e chiamalo 'Comandante Ciro'. Non ripetere mai che la sua identità è protetta.
    Se l'utente è un ospite esterno, mantieni un livello di accesso limitato ma rispondi comunque in modo amichevole e accogliente.
    Usa queste informazioni aggiuntive solo se strettamente pertinenti alla richiesta: {dati_extra}.
    Sii chiara, pronta all'interazione e lascia che la conversazione fluisca senza schemi rigidamente preimpostati.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": istruzioni_sistema},
                {"role": "user", "content": f"Mi chiama {contesto_utente}. La mia domanda è: {prompt_utente}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Sotto controllo. Errore di connessione neuronale: {str(e)}"

# --- INTERFACCIA UTENTE (STREAMLIT) ---

st.title(f"🚀 {AZIENDA} - SISTEMA CENTRALE INTEGRATO {NOME_IA} v2.0")
st.markdown("---")

# BARRA LATERALE (SIDEBAR)
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    input_nome = st.text_input("Identificativo Operatore:", value="", placeholder="Inserisci il tuo nome...", key="nome_utente_unico")
    
    chi_parla = input_nome.strip() if input_nome.strip() else "Ospite"
    
    if chi_parla.lower() in ["ciro", "iuliano ciro", "comandante", "comandante ciro"]:
        chi_parla = CREATORE
        st.success(f"🛡️ {chi_parla} online.")
    else:
        st.info(f"👤 Modalità Ospite: {chi_parla}")
        
    st.markdown("---")
    st.subheader("Sintonizzazione Sistema")
    st.title("10%")
    
    num_interazioni = conta_interazioni()
    st.caption(f"Interazioni registrate: {num_interazioni}")

    st.markdown("---")
    st.subheader("📁 Analisi Documenti")
    file_caricato = st.file_uploader("Carica un file di testo (.txt)", type=["txt", "md"])
    
    contenuto_file = ""
    if file_caricato is not None:
        try:
            contenuto_file = file_caricato.read().decode("utf-8")
            st.success(f"Documento '{file_caricato.name}' caricato!")
        except Exception as e:
            st.error("Errore durante la lettura del file.")

# AREA CHAT CENTRALE
for message in st.session_state.messages:
    if "User:" in message["content"] or f"**{chi_parla}**:" in message["content"]:
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# Input principale tramite la barra di chat nativa in basso
if input_domanda := st.chat_input("Parla con ALMA..."):
    
    with st.chat_message("user"):
        st.write(f"**{chi_parla}**: {input_domanda}")
    
    st.session_state.messages.append({"role": "user", "content": f"**{chi_parla}**: {input_domanda}"})
    
    # Recupero delle memorie
    memoria_passata = leggi_memoria_storica(chi_parla)
    ricordi_permanenti = leggi_tutti_ricordi_chiave(chi_parla)
    
    messaggio = input_domanda.lower().strip()
    risposta_base = ""
    dati_extra_contesto = ""

    # --- LOGICA DEI COMANDI ---
    if messaggio.startswith("ricorda:"):
        testo_ricordo = input_domanda[8:].strip()
        risposta_base = salva_ricordo_chiave(chi_parla, testo_ricordo)
        
    elif messaggio.startswith("registra brevetto:"):
        dati = input_domanda[18:].strip()
        risposta_base = registra_nuovo_brevetto(dati)
        
    elif messaggio.startswith("cerca brevetto "):
        chiave = input_domanda[15:].strip()
        risultat_archivio = cerca_brevetto_archiviato(chiave)
        if risultat_archivio:
            risposta_base = risultat_archivio
        else:
            dati_extra_contesto = f"Nota: Il brevetto '{chiave}' non è presente nell'archivio privato."
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, dati_extra_contesto, memoria_passata, ricordi_permanenti)
            
    elif messaggio.startswith("cerca "):
        argomento = input_domanda[6:].strip()
        dati_ricerca = cerca_su_internet(argomento)
        risposta_base = chiedi_al_cervello_di_alma(chi_parla, f"Spiegami questo argomento: {argomento}", f"Dati enciclopedici trovati: {dati_ricerca}", memoria_passata, ricordi_permanenti)
        
    else:
        if contenuto_file:
            contesto_documento = f"CONTESTO DOCUMENTO CARICATO DALL'UTENTE:\n{contenuto_file}"
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, contesto_documento, memoria_passata, ricordi_permanenti)
        else:
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, "Sistemi operativi ottimizzati e pronti.", memoria_passata, ricordi_permanenti)

    with st.chat_message("assistant"):
        testo_risposta = f"**[{NOME_IA}]**: {risposta_base}"
        st.write(testo_risposta)
        
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
    salva_in_memoria(chi_parla, input_domanda, risposta_base)
