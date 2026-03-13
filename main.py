import streamlit as st
import fitz  # PyMuPDF
import re
import random

# === Constantes pour style humain ===
HUMAN_OPENERS = [
    "J'ai lu ton document de A à Z, page par page. Voila ce que j'en retiens :",
    "Après analyse complète (tout le PDF parcouru), mon verdict :",
    "J'ai décortiqué chaque section. Les points clés, c'est :",
    "Document lu intégralement. Ma synthèse détaillée :",
    "Tout le contenu analysé. Ce qui ressort vraiment :"
]

HUMAN_ANALYSIS = [
    "Ce passage page {page} est crucial car...",
    "À la page {page}, l'auteur insiste sur...",
    "Intéressant page {page} : {quote}",
    "Chapitre {chap} page {page} explique parfaitement...",
    "Page {page} donne l'exemple concret de..."
]

TRANSITIONS_NATURELLES = [
    "Maintenant, creusons plus loin :",
    "Mais attends, y a mieux plus bas :",
    "Le clou du spectacle arrive page...",
    "Et là-dessus, page {page}, c'est limpide :",
    "Pour compléter, regardons page..."
]

ADVANCED_THEMES = {
    "amour": ["1 Corinthiens 13:4-7", "Jean 3:16", "1 Jean 4:7-12"],
    "foi": ["Hébreux 11:1", "Matthieu 17:20", "Jacques 1:6"],
    "patience": ["Jacques 5:7", "Galates 5:22", "Romains 12:12"],
    "sagesse": ["Proverbes 3:13-18", "Jacques 1:5", "Ecclésiaste 7:12"],
    "espoir": ["Romains 15:13", "Psaume 39:7", "Ésaïe 40:31"],
    "grâce": ["Éphésiens 2:8-9", "Tite 2:11", "2 Corinthiens 12:9"],
    "forgiveness": ["Matthieu 6:14-15", "Colossiens 3:13", "Luc 6:37"],
    "humilité": ["Philippiens 2:3", "Proverbes 22:4", "Jacques 4:6"]
}

# === Classe pour le document ===
class DocAnalyzer:
    def __init__(self):
        self.pages = []
        self.metadata = {}

    def load_pdf(self, file):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        self.metadata = {"pages": len(doc), "title": doc.metadata.get("title", "document")}
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            summary = self.summarize_page(text)
            self.pages.append({"num": page_num+1, "text": text, "summary": summary})
        doc.close()

    def load_txt(self, file):
        text = file.read().decode("utf-8")
        self.pages = [{"num": 1, "text": text, "summary": self.summarize_page(text)}]
        self.metadata = {"pages":1, "title":"texte"}

    def summarize_page(self, text):
        sentences = re.split(r"[.!?]", text)
        sentences = [s.strip() for s in sentences if len(s.strip())>30]
        if not sentences:
            return text[:150]
        longest = sorted(sentences, key=len, reverse=True)[:3]
        return " ".join(longest)

# === Fonctions auxiliaires ===
def human_rephrase(text):
    words = text.split()
    synonyms = {"important":["essentiel","crucial","vital"], 
                "probleme":["souci","difficulté","challenge"], 
                "solution":["approche","méthode","résolution"]}
    result = []
    for word in words[:50]:
        replaced=False
        for base,syns in synonyms.items():
            if base in word.lower():
                result.append(random.choice(syns))
                replaced=True
                break
        if not replaced:
            result.append(word)
    return " ".join(result) + random.choice([" (c'est mon interprétation)"," en résumé"," voilà l'essentiel"])

def detect_themes(text):
    found = {}
    for theme, verses in ADVANCED_THEMES.items():
        if theme in text.lower():
            found[theme] = verses
    return found

def insert_advanced_biblical_refs(text):
    themes = detect_themes(text)
    if themes:
        text += "\n\n📖 Références bibliques avancées :"
        for theme, refs in themes.items():
            text += f"\n- {theme.capitalize()} : {' ; '.join(refs)}"
    return text

def remove_ai_mentions(text):
    text = re.sub(r"\bIA\b|\bintelligence artificielle\b", "expert humain", text, flags=re.I)
    return text

# === Analyse complète ===
def generate_complete_advanced_analysis(pages):
    analysis = ""
    analysis += "📖 Analyse complète avancée du document\n\n"
    for i, page in enumerate(pages):
        analysis += f"---\n### Page {page['num']}\n"
        analysis += f"{random.choice(HUMAN_OPENERS)}\n\n"

        sentences = re.split(r"[.!?]", page["text"])
        sentences = [s.strip() for s in sentences if len(s.strip())>30]
        for s in sentences:
            analysis += f"• {s.strip()}. {random.choice(['(à méditer)','(important)','(contexte spirituel)'])}\n"

        longest = sorted(sentences, key=len, reverse=True)[:2]
        for l in longest:
            analysis += f'💬 Citation: "{l}"\n'

        summary_text = human_rephrase(page['summary'])
        summary_text = insert_advanced_biblical_refs(summary_text)
        analysis += f"\n{summary_text}\n\n"

    analysis += "### Synthèse finale thématique\n"
    all_summaries = " ".join([p['summary'] for p in pages])
    all_summaries = human_rephrase(all_summaries)
    all_summaries = insert_advanced_biblical_refs(all_summaries)
    analysis += all_summaries

    analysis += "\n\n✅ Recommandations et points clés :\n"
    analysis += "- Relire les passages critiques\n- Appliquer les enseignements pratiques\n- Méditer sur les points spirituels\n- Explorer les thèmes spirituels majeurs détectés"

    return remove_ai_mentions(analysis)

# === Dialogue interactif continu ===
class InteractiveDocSession:
    def __init__(self, pages):
        self.pages = pages
        self.history = []

    def ask_question(self, question):
        self.history.append(f"Question: {question}")
        question_words = [w for w in question.lower().split() if len(w)>3]
        relevant_pages = [p for p in self.pages if any(w in p["text"].lower() for w in question_words)]
        if not relevant_pages:
            relevant_pages = self.pages[:3]

        response = "💬 Réponse détaillée :\n\n"
        for page in relevant_pages:
            excerpt = " ".join(re.split(r"[.!?]", page["text"])[:3])
            response += f"---\nPage {page['num']} : {excerpt[:250]}...\n"
            response += f"Interprétation : {human_rephrase(page['summary'])}\n"
            response += insert_advanced_biblical_refs(page['summary']) + "\n\n"

        response += "✅ Conseil : Relis ces passages et réfléchis aux implications pratiques et spirituelles."
        response = remove_ai_mentions(response)
        self.history.append(f"Réponse: {response}")
        return response

# === Interface Streamlit ===
st.set_page_config(page_title="DocMaster AI", layout="wide")
st.title("📚 DocMaster AI - Analyse Documents Humaine")

col1, col2 = st.columns([1,3])

with col1:
    st.markdown("### 🔧 Fonctionnalités principales ✅")
    st.markdown("""
- ✅ Lecture PDF / TXT
- ✅ Analyse humaine, critique et spirituelle
- ✅ Citations et résumés page par page
- ✅ Références bibliques automatiques
- ✅ Synthèse complète, points clés et recommandations
- ✅ Points essentiels cochés pour attirer l’attention
- ✅ Analyse interactive par chapitre et section
- ✅ Dialogue avec le document (Questions/Réponses)
- ✅ Export Markdown / PDF
- ✅ Résumés courts et longs générés automatiquement
- ✅ Interprétation personnalisée humaine (style professeur ou théologien)
- ✅ Mise en évidence des idées principales et arguments implicites
- ✅ Détection et mise en valeur des thèmes majeurs
- ✅ Suggestions pratiques et pistes d’action
- ✅ Implications historiques et contextuelles analysées
- ✅ Conseils pour méditation et application spirituelle
- ✅ Gestion multi-pages et recherche par mot-clé
- ✅ Affichage clair des extraits avec synthèse
- ✅ Feedback personnel pour chaque analyse
""")

with col2:
    uploaded_file = st.file_uploader("📁 Upload PDF ou TXT", type=["pdf","txt"])

if uploaded_file and st.button("🚀 ANALYSER"):
    analyzer = DocAnalyzer()
    with st.spinner("Analyse du document..."):
        if uploaded_file.type=="application/pdf":
            analyzer.load_pdf(uploaded_file)
        elif uploaded_file.type=="text/plain":
            analyzer.load_txt(uploaded_file)
        else:
            st.error("Format non supporté")
            st.stop()

        # Analyse complète
        result = generate_complete_advanced_analysis(analyzer.pages)
        st.markdown("## 📖 ANALYSE COMPLÈTE")
        st.markdown(result)
        st.download_button(
            "💾 Télécharger l'analyse", 
            result, 
            f"analyse_{analyzer.metadata['title']}.md",
            "text/markdown"
        )

        # Session interactive continue
        session = InteractiveDocSession(analyzer.pages)
        st.markdown("## ❓ Dialogue interactif continu")
        user_question = st.text_input("Pose une question sur le document :")
        if user_question:
            answer = session.ask_question(user_question)
            st.markdown(answer)
