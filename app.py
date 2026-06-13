import streamlit as st
import time
from src.nlp_engine import CybertronEngine
from src.audio_handler import AudioHandler

# Initialisation du moteur d'IA et chargement des ressources (modèles, intents, etc.) avec mise en cache pour performance
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
    
    /* Les menus Streamlit */
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


# GESTION DE L'ÉTAT ET DE L'HISTORIQUE (Vide au premier lancement)
if "conversations" not in st.session_state:
    st.session_state.conversations = {}  # Aucun fil de discussion par défaut

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None  # Aucun chat actif au départ


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
        "Choisissez le moteur d'analyse :",
        ["cybertron-spacy-md (Analyse Sémantique)", "cybertron-spacy-sm (Analyse Rapide)", "Gemini Pro (Simulation LLM Advanced)"],
        index=0,
    )
    
    st.divider()
    
    # Affichage de l'historique des discussions avec possibilité de suppression
    st.subheader("📝 Historique des Discussions")
    liste_chats = list(st.session_state.conversations.keys())
    
    if not liste_chats:
        st.caption("Aucun historique disponible.")
    else:
        for chat_title in liste_chats:
            # Alignement horizontal pour le titre et le bouton de suppression
            col_chat, col_del = st.columns([0.85, 0.15])
            
            with col_chat:
                label = f"💬 {chat_title}" if chat_title != st.session_state.current_chat else f"{chat_title}"
                if st.button(label, key=f"btn_{chat_title}", use_container_width=True):
                    st.session_state.current_chat = chat_title
                    st.rerun()
            
            with col_del:
                if st.button("🗑️", key=f"del_{chat_title}", use_container_width=True, help="Supprimer cette discussion"):
                    del st.session_state.conversations[chat_title]
                    # Si le chat supprimé était actif, basculer vers un autre ou revenir à l'accueil
                    if st.session_state.current_chat == chat_title:
                        restants = list(st.session_state.conversations.keys())
                        st.session_state.current_chat = restants[0] if restants else None
                    st.rerun()


# ZONE CENTRALE : ACCUEIL OU FLUX DE DISCUSSION
if st.session_state.current_chat is None:
    # Écran d'accueil épuré avec message de bienvenue et instructions
    st.markdown("""
        <div style="text-align: center; margin-top: 120px; padding: 20px;">
            <h1 style="font-size: 3.2rem; font-weight: 700; margin-bottom: 10px; color: #ececf1;">Cybertron</h1>
            <p style="color: #8e8ea0; font-size: 1.3rem; max-width: 600px; margin: 0 auto;">
                Sécurité opérationnelle par IA. Posez une question ou décrivez une anomalie système pour démarrer l'analyse continue.
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Mode actif : Affichage du fil de discussion en cours
    st.title(f"Console : {st.session_state.current_chat}")
    st.caption(f"Moteur actif : {choix_modele}")
    st.divider()

    flux_actuel = st.session_state.conversations[st.session_state.current_chat]

    for msg in flux_actuel:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>Vous :</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-bubble-assistant">
                    <b>Cybertron Engine :</b><br>{msg["content"]}<br>
                    <small style="color: #64748b;">Niveau : {msg.get('threat', 'Évalué')} | Via : {msg.get('method', 'NLP Pipeline')}</small>
                </div>
            """, unsafe_allow_html=True)


# ZONE DE SAISIE MULTI-MODALE
st.divider()

texte_vocal = AudioHandler.render_voice_input()
prompt_texte = st.chat_input("Posez votre question ou décrivez une anomalie système ici...")
prompt_final = prompt_texte if prompt_texte else texte_vocal

if prompt_final:
    # Création automatique à la volée si l'utilisateur envoie un message depuis l'écran d'accueil
    if st.session_state.current_chat is None:
        nouveau_nom = f"Incident Cyber - {time.strftime('%H:%M:%S')}"
        st.session_state.conversations[nouveau_nom] = []
        st.session_state.current_chat = nouveau_nom
        
    flux_actuel = st.session_state.conversations[st.session_state.current_chat]
    flux_actuel.append({"role": "user", "content": prompt_final})
    
    # Traitement
    resultat = engine.predict(prompt_final, choix_modele)
    
    flux_actuel.append({
        "role": "assistant",
        "content": resultat["response"],
        "threat": resultat["threat_level"],
        "method": resultat["method"]
    })
    
    st.rerun()