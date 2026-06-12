import os
import json
import time
import spacy
from spacy.language import Language
from spacy.matcher import PhraseMatcher

# Déclaration des extensions natives spaCy
if not spacy.tokens.Doc.has_extension("threat_level"):
    spacy.tokens.Doc.set_extension("threat_level", default="Faible")
if not spacy.tokens.Doc.has_extension("suspicious_tokens"):
    spacy.tokens.Doc.set_extension("suspicious_tokens", default=[])

@Language.component("cyber_threat_analyzer")
def cyber_threat_analyzer(doc):
    alert_words = ["password", "virus", "hacked", "phishing", "urgent", "banque", "cliquez", "ransomware", "mfa"]
    detected = [token.text for token in doc if token.text.lower() in alert_words]
    doc._.suspicious_tokens = list(set(detected))
    
    if len(detected) > 3:
        doc._.threat_level = "🔴 CRITIQUE"
    elif len(detected) > 0:
        doc._.threat_level = "🟠 ÉLEVÉ"
    else:
        doc._.threat_level = "🟢 MINIME"
    return doc

class CybertronEngine:
    def __init__(self):
        self.responses = {}
        self.intent_docs = {}
        self.matcher = None
        self.current_model_name = None
        self.nlp = None
        self.load_intents()

    def load_intents(self):
        with open("intents.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def configure_pipeline(self, model_name):
        """ Gère la commutation dynamique des modèles (Style Gemini) """
        if self.current_model_name == model_name and self.nlp is not None:
            return
        
        self.current_model_name = model_name
        
        # Option 1 & 2 : Modèles locaux spaCy issus de ton cours
        if model_name in ["cybertron-spacy-md (Sémantique)", "cybertron-spacy-sm (Rapide)"]:
            spacy_code = "fr_core_news_md" if "md" in model_name else "fr_core_news_sm"
            try:
                self.nlp = spacy.load(spacy_code)
            except OSError:
                # Fallback automatique si le modèle n'est pas installé
                self.nlp = spacy.load("fr_core_news_sm")
                
            if "cyber_threat_analyzer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("cyber_threat_analyzer", last=True)
                
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            
            for intent in self.data["intents"]:
                tag = intent["tag"]
                self.responses[tag] = intent["responses"]
                patterns = [self.nlp(p.lower()) for p in intent["patterns"]]
                self.matcher.add(tag, patterns)
                self.intent_docs[tag] = patterns

    def predict(self, text, model_name):
        """ Traite le texte selon le modèle sélectionné """
        # Simulation d'un modèle LLM Cloud type Gemini Pro Cyber
        if model_name == "Gemini Pro (Simulation LLM)":
            time.sleep(0.8) # Simulation de latence API
            return {
                "response": f" [Analyse générative avancée] Votre requête : '{text}' présente des caractéristiques suspectes. Analyse contextuelle globale en cours...",
                "threat_level": "🟠 ÉVALUATION IA GENERATIVE",
                "tokens": ["Analyse contextuelle globale"],
                "method": "Gemini Pro Generative API (Stub)"
            }
            
        # Modèles Spacy (Cours avancé)
        self.configure_pipeline(model_name)
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        if matches:
            tag = self.nlp.vocab.strings[matches[0][0]]
            return {
                "response": self.responses[tag][0],
                "threat_level": doc._.threat_level,
                "tokens": doc._.suspicious_tokens,
                "method": "Rule-based Matching (PhraseMatcher)"
            }
            
        # Repli sémantique si le modèle md est actif
        if "md" in model_name:
            best_score = 0.0
            best_tag = None
            for tag, docs in self.intent_docs.items():
                for d in docs:
                    score = doc.similarity(d)
                    if score > best_score:
                        best_score = score
                        best_tag = tag
            if best_score > 0.62:
                return {
                    "response": self.responses[best_tag][0],
                    "threat_level": doc._.threat_level,
                    "tokens": doc._.suspicious_tokens,
                    "method": f"Similarité Vectorielle ({round(best_score*100, 1)}%)"
                }

        return {
            "response": "Désolé, mes signatures actuelles ne me permettent pas de catégoriser cet incident avec certitude.",
            "threat_level": "⚪ INCONNU",
            "tokens": doc._.suspicious_tokens,
            "method": "Seuil de confiance insuffisant"
        }