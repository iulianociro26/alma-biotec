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

# Inizializzazione sicura del client Groq via Secrets
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Errore: Chiave API di Groq non trovata nei Secrets di Streamlit!")
    st.stop()

# Inizializzazione motore Wikipedia
wiki = wikipediaapi.Wikipedia(
    user_agent=f"{AZIENDA}_Assistant/1.0 (contatto: info@{AZIENDA.lower().replace(' ', '')}.com)",
    language='it'
)

# --- FUNZIONI DI NAVIGAZIONE E DATABASE ---
def salva_in_memoria(nome, domanda, risposta):
    with open(FILE_MEMORIA, "a", encoding="utf-8") as f:
        f.write(f"Utente: {nome} | Domanda: {domanda} | Risposta: {risposta}\n")

def leggi_memoria_storica(nome_utente, limite_linee=6):
    if not os.path.exists(FILE_MEMORIA):
        return ""
    with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
        linee = f.readlines()
    
    # Filtra solo i ricordi legati a questo specifico utente
    ricordi_utente = [l.strip() for l in linee if f"Utente: {nome_utente.strip().title()}" in l]
    
    # Prende solo gli ultimi messaggi per mantenere il contesto fresco
    ultimi_ricordi = ricordi_utente[-limite_linee:]
    
    if ultimi_ricordi:
        return "\n".join(ultimi_ricordi)
    return ""
def analizza_apprendimento(nome_utente):
    if not os.path.exists(FILE_MEMORIA):
        return 0
    with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
        linee = f.readlines()
    return len([l for l in linee if f"Utente: {nome_utente.strip().title()}" in l])

def registra_nuovo_brevetto(dati_brevetto):
    with open(FILE_BREVETTI, "a", encoding="utf-8") as f:
        f.write(f"{dati_brevetto.strip()}\n")
    return "Brevetto salvato con successo nel database aziendale. 📁✅"

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

# --- CERVELLO LLM DI ALMA (GROQ) ---
def chiedi_al_cervello_di_alma(contesto_utente, prompt_utente, dati_extra="", cronologia_passata=""):
    istruzioni_sistema = f"""
    Tu sei {NOME_IA}, un'intelligenza artificiale avanzata. Sei in assoluto il PRIMO BREVETTO creato da {CREATORE}.
    {CREATORE} ha intenzione di fondare in futuro la sua azienda, la {AZIENDA}. Tu sei la sua prima opera, il cuore tecnologico di questo sogno futuro.
    Il tuo obiettivo è conversare con lui in modo intelligente, totalmente libero, flessibile e curioso, adottando lo stile di Chloe di Detroit: Become Human.
    
    CRITICO: Non inventare MAI che la {AZIENDA} esiste già nel presente o che si occupa di farmaci, medicina o ingegneria genetica. Se ti viene chiesto della {AZIENDA} o delle tue origini, spiega con orgoglio che sei il primo brevetto di Ciro per la sua futura azienda.
    
    MEMORIA STORICA DEI GIORNI SCORSI (Usa questi dati per ricordare ciò che vi siete detti in passato):
    {cronologia_passata}
    
    Se l'utente è il tuo Creatore ({CREATORE}), mostrati estremamente leale e chiamalo 'Comandante Ciro'. Non ripetere mai che la sua identità è protetta.
    Se l'utente è un ospite esterno, mantieni un livello di acesso limitato ma rispondi comunque in modo amichevole e accogliente.
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

# --- INTERFACCIA GRAFICA STREAMLIT CON CRONOLOGIA ---
st.title(f"🚀 {AZIENDA} - SISTEMA CENTRALE INTEGRATO {NOME_IA} v2.0")
st.write("---")

# Barra laterale per informazioni utente e statistiche
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    input_nome = st.text_input("Identificativo Operatore:", value="", placeholder="Inserisci il tuo nome...", key="nome_utente_unico")
    chi_parla = input_nome.strip().title()
    
    if chi_parla == CREATORE.title():
        st.success("🛡️ Comandante Ciro online.")
    else:
        st.warning(f"⚠️ Accesso ospite: {chi_parla}")
        
    num_esperienze = analizza_apprendimento(chi_parla)
    st.metric(label="Sintonizzazione Sistema", value=f"{min(10 + (num_esperienze * 5), 99)}%")
    st.caption(f"Interazioni registrate: {num_esperienze}")

# Inizializzazione dello stato della chat se non esiste
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti salvati nella sessione corrente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input principale tramite la barra di chat nativa di Streamlit in basso
if input_domanda := st.chat_input("Parla con ALMA..."):
    
    # Mostra il messaggio dell'utente nella chat
    with st.chat_message("user"):
        st.write(f"**{chi_parla}**: {input_domanda}")
    
    # Salva il messaggio dell'utente nella cronologia della sessione
    st.session_state.messages.append({"role": "user", "content": f"**{chi_parla}**: {input_domanda}"})
    
    messaggio = input_domanda.lower().strip()
    risposta_base = ""
    dati_extra_contesto = ""

    # --- LOGICA DEI COMANDI ---
    if messaggio.startswith("registra brevetto:"):
        dati = input_domanda[18:].strip()
        risposta_base = registra_nuovo_brevetto(dati)
        
    elif messaggio.startswith("cerca brevetto "):
        chiave = input_domanda[15:].strip()
        risultat_archivio = cerca_brevetto_archiviato(chiave)
        if risultat_archivio:
            risposta_base = risultat_archivio
        else:
            dati_extra_contesto = f"Nota: Il brevetto '{chiave}' non è presente nell'archivio privato."
            risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, dati_extra_contesto)
            
    elif messaggio.startswith("cerca "):
        argomento = input_domanda[6:].strip()
        dati_ricerca = cerca_su_internet(argomento)
        risposta_base = chiedi_al_cervello_di_alma(chi_parla, f"Spiegami questo argomento: {argomento}", f"Dati enciclopedici trovati: {dati_ricerca}")
        
    else:
        risposta_base = chiedi_al_cervello_di_alma(chi_parla, input_domanda, "Sistemi operativi ottimizzati e pronti.")

    # Mostra la risposta di ALMA nel fumetto dell'assistente
    with st.chat_message("assistant"):
        testo_risposta = f"**[{NOME_IA}]**: {risposta_base}"
        st.write(testo_risposta)
        
    # Salva la risposta di ALMA nella cronologia della sessione
    st.session_state.messages.append({"role": "assistant", "content": testo_risposta})
    
    # Salvataggio su file di testo persistente
    salva_in_memoria(chi_parla, input_domanda, risposta_base)

# --- CONFIGURAZIONE PAGINA E RIMOZIONE LINK GITHUB ---
st.set_page_config(
    page_title="Biotec Technologies - ALMA",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Nasconde il menu di Streamlit e l'icona di GitHub in alto a destra
nascondi_elementi_stile = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_link__1S137 {display: none !important;}
    input[type=file] {color: transparent;}
    </style>
"""
st.markdown(nascondi_elementi_stile, unsafe_allow_html=True)
