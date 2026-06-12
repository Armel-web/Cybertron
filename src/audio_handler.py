import streamlit as st
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

class AudioHandler:
    @staticmethod
    def render_voice_input():
        """ Affiche l'interface d'enregistrement vocale native """
        st.markdown("### 🎙️ Entrée Vocale (Optionnelle)")
        # Utilisation du composant natif moderne de Streamlit pour la capture audio
        audio_file = st.audio_input("Cliquez sur le micro pour décrire l'incident à la voix")
        
        if audio_file is not None:
            if not SPEECH_AVAILABLE:
                st.warning("La bibliothèque `speech_recognition` n'est pas installée dans ton venv. Installe-la via `pip install SpeechRecognition`.")
                return None
                
            try:
                r = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio_data = r.record(source)
                    # Transcription gratuite via l'API de reconnaissance Google intégrée
                    text = r.recognize_google(audio_data, language="fr-FR")
                    st.success(f" Transcrit avec succès : \"{text}\"")
                    return text
            except Exception as e:
                st.error("Impossible de décoder l'audio. Parlez plus distinctement.")
                return None
        return None