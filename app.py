import time
import json
import numpy as np
import streamlit as st
import fitz  # PyMuPDF

# Packages fondamentaux de Data Science exigés pour le projet
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# Configuration de l'interface en mode Large
st.set_page_config(page_title="Cybertron - IA Cybersécurité", page_icon="🛡️", layout="wide")

# Outil pour styliser l'interface avec du CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #ffffff; }
    .metric-box {
        background-color: #1e222b;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00bcff;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ENTRAÎNEMENT DU RÉSEAU DE NEURONES
@st.cache_resource
def entrainer_cybertron():
    with open("intents.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    inputs = []
    outputs = []
    classes = []
    responses = {}
    
    for intent in data["intents"]:
        tag = intent["tag"]
        classes.append(tag)
        responses[tag] = intent["responses"]
        for pattern in intent["patterns"]:
            inputs.append(pattern.lower())
            outputs.append(tag)
            
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(inputs).toarray()
    y = np.array([classes.index(t) for t in outputs])
    
    model = Sequential([
        Dense(128, input_shape=(X.shape[1],), activation='relu'),
        Dropout(0.3),                                             
        Dense(64, activation='relu'),                             
        Dense(len(classes), activation='softmax')                 
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(X, y, epochs=150, verbose=0)
    
    return vectorizer, model, classes, responses

# Lancement de l'IA Cybertron (chargement de l'entraînement en cache pour rapidité)
vectorizer, model, classes, responses = entrainer_cybertron()

# MÉMOIRE DE LA DISCUSSION
if "messages" not in st.session_state:
    st.session_state.messages = []

# BARRE LATÉRALE : DASHBOARD DE SÉCURITÉ
with st.sidebar:
    st.markdown("### 🖥️ Moniteur Système")
    st.markdown("- **CPU** : 15%")
    st.markdown("- **RAM** : 45%")

    st.divider()
    st.subheader("📁 Analyse de fichiers / Logs")
    uploaded_pdf = st.file_uploader("Déposer un e-mail ou log suspect", type=['pdf'])
    
    if uploaded_pdf:
        with st.spinner("Analyse lexicale..."):
            with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
                text_pdf = "".join([page.get_text().lower() for page in doc])
            
            alert_words = ["password", "virus", "hacked", "phishing", "urgent", "banque", "cliquez"]
            stats = {word: text_pdf.count(word) for word in alert_words}
            
        st.success("Analyse effectuée")
        cols = st.columns(2)
        for i, (word, count) in enumerate(stats.items()):
            target_col = cols[0] if i % 2 == 0 else cols[1]
            if count > 0:
                target_col.markdown(f"🔴 **{word}** : `{count}`")
            else:
                target_col.markdown(f"⚪ {word} : `0`")

    st.divider()
    if st.button("🗑️ Réinitialiser la console"):
        st.session_state.messages = []
        st.rerun()

# BARRE PRINCIPALE
st.title("Cybertron - Analyse de Menaces par IA")
st.markdown("##### *Terminal d'analyse de menaces par Intelligence Artificielle et Deep Learning.*")

# Affichage de l'historique du chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée utilisateur
if prompt := st.chat_input(" Décrivez l'incident ou collez le texte suspect ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        start_time = time.time()
        
        # Prétraitement du texte et prédiction de la classe d'incident
        input_vector = vectorizer.transform([prompt.lower()]).toarray()
        prediction = model.predict(input_vector, verbose=0)
        idx_predit = np.argmax(prediction)
        score_confiance = prediction[0][idx_predit]
        tag_predit = classes[idx_predit]
        
        duration = round(time.time() - start_time, 4)
        
        # Construction de la réponse intelligente avec mise en forme avancée
        if score_confiance > 0.30:
            reponse_texte = responses[tag_predit][0]
            
            # Définition dynamique de la sévérité visuelle
            if tag_predit in ["ransomware", "fuite_donnees"]:
                severity_color = "🔴 CRITIQUE"
                box_style = "border: 2px solid #ff4b4b; background-color: #2b1b1b; padding: 20px; border-radius: 10px;"
            elif tag_predit in ["phishing", "malware"]:
                severity_color = "🟠 ÉLEVÉ"
                box_style = "border: 2px solid #ffa500; background-color: #2b251b; padding: 20px; border-radius: 10px;"
            else:
                severity_color = "🟡 MODÉRÉ"
                box_style = "border: 2px solid #00bcff; background-color: #1b262b; padding: 20px; border-radius: 10px;"
            
            # Affichage de la carte de réponse personnalisée (HTML)
            container_html = f"""
            <div style="{box_style}">
                <h3 style='margin-top:0px;'>Niveau de menace : {severity_color}</h3>
                <p><b>Type d'incident détecté :</b> Classification automatique en <code>{tag_predit.upper()}</code></p>
                <hr style='border-color: rgba(255,255,255,0.1);'>
                <p style='font-size: 16px; line-height: 1.6;'>{reponse_texte}</p>
            </div>
            """
            st.markdown(container_html, unsafe_allow_html=True)
            
            # Ajout interactif d'un Playbook de remédiation
            st.markdown("#### 📋 Procédure de Réaction Immédiate :")
            if tag_predit == "phishing":
                st.checkbox("Ne cliquer sur aucun lien hypertexte du message.", value=False, key="p1")
                st.checkbox("Ne saisir aucune coordonnée bancaire ou mot de passe.", value=False, key="p2")
                st.checkbox("Transférer le message à la cellule de sécurité ou le signaler (Pharos).", value=False, key="p3")
            elif tag_predit == "ransomware":
                st.checkbox("DÉCONNECTER IMMÉDIATEMENT la machine du réseau (Wi-Fi et Câble).", value=False, key="r1")
                st.checkbox("Ne pas éteindre l'ordinateur (pour préserver les clés de chiffrement en mémoire RAM).", value=False, key="r2")
                st.checkbox("Alerter immédiatement le responsable informatique.", value=False, key="r3")
            else:
                st.checkbox("Changer les identifiants compromis par un mot de passe fort.", value=False, key="g1")
                st.checkbox("Activer l'authentification multifacteur (2FA).", value=False, key="g2")
                
        else:
            st.warning("⚠️ Niveau de confiance insuffisant pour catégoriser automatiquement la menace. Par sécurité, traitez cet incident comme suspect et demandez une levée de doute à un expert.")
        
        # Affichage de la jauge de confiance du modèle
        st.write("")
        st.markdown(f"**Indice de confiance du réseau de neurones :** `{round(float(score_confiance)*100, 1)}%`")
        st.progress(float(score_confiance))
        
        # Métriques techniques
        st.caption(f"⚡ Inférence Réseau : `{duration}s` | Classes analysées : `6` | Framework : `TensorFlow Keras`")
        
        # Ajout de la réponse à l'historique de la discussion
        st.session_state.messages.append({"role": "assistant", "content": f"Menace {tag_predit.upper()} identifiée avec une confiance de {round(float(score_confiance)*100, 2)}%."})