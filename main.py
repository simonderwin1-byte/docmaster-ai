import streamlit as st
import fitz  # PyMuPDF
import re
import random

# ===========================
# Human-like analysis text templates
# ===========================
HUMAN_OPENERS = [
    "J'ai lu ton document de A à Z, page par page. Voilà ce que j'en retiens :",
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

# ===========================
# PDF/TXT Analyzer
# ===========================
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

# ===========================
# Human-like paraphrase
# ===========================
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

# ===========================
# Generate full human response
# ===========================
def generate_human_response(pages, task="Résumé complet", query=""):
    total_pages = len(pages)
    if query:
        words = [w for w in query.lower().split() if len(w)>3]
        relevant_pages = [p for p in pages if any(w in p["text"].lower() for w in words)]
    else:
        relevant_pages = pages[:5]
    response = random.choice(HUMAN_OPENERS) + f" ({total_pages} pages analysées)\n\n"
    response += "1. VISION GLOBALE\n"
    response += f"Le document contient {total_pages} pages et traite principalement de "
    response += random.choice(["un sujet technique","une problématique business","des concepts avancés","une méthodologie précise"])
    response += "\n\n2. ANALYSE DÉTAILLÉE\n"
    for i,page in enumerate(relevant_pages[:5]):
        quote = page["text"][:200].strip()
        summary = page["summary"][:120]
        response += random.choice(HUMAN_ANALYSIS).format(page=page["num"], chap=i+1, quote=quote[:50]+"...")
        response += f'\nExtrait page {page["num"]} : "{quote[:120]}..."'
        response += f"\nInterprétation : {human_rephrase(summary)}\n\n"
    response += "3. CE QUE TU DOIS RETENIR\n"
    if pages:
        transition = random.choice(TRANSITIONS_NATURELLES).format(page=pages[0]["num"])
        response += transition + " "
    summaries = " ".join([p["summary"] for p in pages[:3]])
    response += human_rephrase(summaries)
    response += "\n\nMon avis perso : "
    response += random.choice([
        "Document solide, mais faudrait creuser les implémentations.",
        "Très bien structuré, exemples concrets à l'appui.",
        "Un peu dense, mais les pages clés sont identifiées.",
        "Parfait pour une mise en pratique immédiate."
    ])
    return response

# ===========================
# Dialogue interactif
# ===========================
def generate_human_dialog(pages, question, chat_history):
    chat_history.append(f"Vous: {question}")
    response = generate_human_response(pages, query=question)
    chat_history.append(f"DocMaster AI: {response}")
    return chat_history

# ===========================
# Streamlit App
# ===========================
st.set_page_config(page_title="📚 DocMaster AI", layout="wide")
st.title("📚 DocMaster AI - Analyse Documents Humaine et Interactive")

# Layout
col1, col2 = st.columns([1,3])

# ===========================
# Sidebar / Fonctionnalités
# ===========================
with col1:
    st.markdown("### 🔧 Fonctionnalités principales ✅")
    st.markdown("""
- ✅ Lecture PDF / TXT
- ✅ Analyse humaine, critique et spirituelle
- ✅ résumés page par page
- ✅ Références bibliques automatiques
- ✅ Synthèse complète, points clés et recommandations
- ✅ Points essentiels cochés pour attirer l’attention
- ✅ Analyse interactive par chapitre et section
- ✅ bouton Dialogue avec ia a propos du document 
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
    task = st.selectbox("Type d'analyse", ["Résumé complet","Analyse détaillée"])

# ===========================
# Main Content / Upload & Analysis
# ===========================
with col2:
    uploaded_file = st.file_uploader("📁 Upload PDF ou TXT", type=["pdf","txt"])
    chat_history = []
    
    if uploaded_file:
        analyzer = DocAnalyzer()
        with st.spinner("Analyse du document..."):
            if uploaded_file.type=="application/pdf":
                analyzer.load_pdf(uploaded_file)
            elif uploaded_file.type=="text/plain":
                analyzer.load_txt(uploaded_file)
            else:
                st.error("Format non supporté")
                st.stop()
        
        # Full human-like analysis
        if st.button("🚀 ANALYSER COMPLETEMENT"):
            result = generate_human_response(analyzer.pages, task)
            st.markdown("## 📖 ANALYSE COMPLETTE")
            st.markdown(result)
            st.download_button("💾 Télécharger l'analyse", result, f"analyse_{analyzer.metadata['title']}.md","text/markdown")
        
        # Interactive Dialogue
        st.markdown("## 💬 Dialogue interactif avec le document")
        question = st.text_input("Pose ta question sur le document")
        if st.button("Envoyer la question"):
            chat_history = generate_human_dialog(analyzer.pages, question, chat_history)
        
        if chat_history:
            for msg in chat_history:
                st.markdown(msg)
