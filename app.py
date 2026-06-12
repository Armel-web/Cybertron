import streamlit as st
import time
from src.nlp_engine import CybertronEngine
from src.audio_handler import AudioHandler

# Initialisation du moteur d'IA (mis en cache pour préserver les performances)
@st.cache_resource
def get_engine():
    return CybertronEngine()

engine = get_engine()

# DESIGN MINIMALISTE ET SOMBRE
st.set_page_config(page_title="Cybertron AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    /* Style global */
    .stApp { background-color: #141722; color: #ececf1; }
    
    /* les menus Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Conteneur de messages */
    .chat-bubble-user {
        background-color: #2a2d3d;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #00f0ff;
    }
    .chat-bubble-assistant {
        background-color: #1e2230;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #ff9900;
    }
    </style>
""", unsafe_allow_html=True)


# GESTION DE L'ÉTAT ET DE L'HISTORIQUE DES DISCUSSIONS
if "conversations" not in st.session_state:
    # Structure de données regroupant plusieurs fils de discussion distincts
    st.session_state.conversations = {
        "Discussion Initiale 1": [
            {"role": "user", "content": "J'ai reçu un mail me demandant mes codes."},
            {"role": "assistant", "content": "Alerte : Tentative d'ingénierie sociale détectée (Phishing).", "threat": "🔴 CRITIQUE", "method": "PhraseMatcher"}
        ]
    }
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Discussion Initiale 1"


# BARRE LATÉRALE : HISTORIQUE & CONFIGURATION MODÈLES
with st.sidebar:
    st.title("Cybertron")
    
    # Bouton "Nouvelle Conversation"
    if st.button("➕ Nouvelle discussion", use_container_width=True):
        nouveau_nom = f"Incident Cyber - {time.strftime('%H:%M:%S')}"
        st.session_state.conversations[nouveau_nom] = []
        st.session_state.current_chat = nouveau_nom
        st.rerun()
        
    st.divider()
    
    # Zone sélective des modèles de traitement
    st.subheader("⚙️ Sélection du modèle")
    choix_modele = st.selectbox(
            "Choisissez le moteur d'analyse pour ce fil de discussion :",
        ["cybertron-spacy-md (Aide Polyvalente)", "cybertron-spacy-sm (Aide Rapide)", "Gemini Processor (Aide Avancée)"],
        index=0,
    )
    
    st.divider()
    
    # Affichage de l'historique des discussions avec indication visuelle de la discussion active
    st.subheader("📝 Historique des Discussions")
    for chat_title in list(st.session_state.conversations.keys()):
        # Mise en évidence visuelle de la discussion active
        label = f"{chat_title}" if chat_title != st.session_state.current_chat else f"{chat_title} (Actif)"
        if st.button(label, key=chat_title, use_container_width=True):
            st.session_state.current_chat = chat_title
            st.rerun()


# ZONE CENTRALE : FLUX DE DISCUSSION
st.title(f"Console : {st.session_state.current_chat}")
st.caption(f"Moteur actif : {choix_modele}")
st.divider()

# Affichage des messages du fil de discussion actif
flux_actuel = st.session_state.conversations[st.session_state.current_chat]

for msg in flux_actuel:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><b>Vous :</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-bubble-assistant">
                <b>Cybertron Engine :</b><br>{msg["content"]}<br>
                <small style="color: #64748b;">Niveau : {msg.get('threat', 'Évalué')}</small>
            </div>
        """, unsafe_allow_html=True)

st.divider()


# ZONE DE SAISIE MULTI-MODALE

# Intégration de la fonctionnalité vocale
texte_vocal = AudioHandler.render_voice_input()

# Barre de saisie de texte classique
prompt_texte = st.chat_input("Posez votre question ou décrivez une anomalie système ici...")

# Centralisation de la donnée d'entrée (texte ou vocal) pour traitement
prompt_final = prompt_texte if prompt_texte else texte_vocal

if prompt_final:
    # Sauvegarde immédiate de la saisie utilisateur
    flux_actuel.append({"role": "user", "content": prompt_final})
    
    # Traitement algorithmique par notre package src/
    resultat = engine.predict(prompt_final, choix_modele)
    
    # Enregistrement de la réponse enrichie
    flux_actuel.append({
        "role": "assistant",
        "content": resultat["response"],
        "threat": resultat["threat_level"],
        "method": resultat["method"]
    })
    
    # Rafraîchissement instantané de l'interface
    st.rerun()