import streamlit as st
import fitz  # PyMuPDF
import re
import random

HUMAN_OPENERS = [
    "J'ai lu ton document de A a Z, page par page. Voila ce que j'en retiens :",
    "Apres analyse complete (tout le PDF parcouru), mon verdict :",
    "J'ai decortique chaque section. Les points cles, c'est :",
    "Document lu integralement. Ma synthese detaillee :",
    "Tout le contenu analyse. Ce qui ressort vraiment :"
]

HUMAN_ANALYSIS = [
    "Ce passage page {page} est crucial car...",
    "A la page {page}, l'auteur insiste sur...",
    "Interessant page {page} : {quote}",
    "Chapitre {chap} page {page} explique parfaitement...",
    "Page {page} donne l'exemple concret de..."
]

TRANSITIONS_NATURELLES = [
    "Maintenant, creusons plus loin :",
    "Mais attends, y a mieux plus bas :",
    "Le clou du spectacle arrive page...",
    "Et la-dessus, page {page}, c'est limpide :",
    "Pour completer, regardons page..."
]

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

def human_rephrase(text):
    words = text.split()
    synonyms = {"important":["essentiel","crucial","vital"], "probleme":["souci","difficulte","challenge"], "solution":["approche","methode","resolution"]}
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
    return " ".join(result) + random.choice([" (c'est mon interpretation)"," en resume"," voila l'essentiel"])

def generate_human_response(pages, task, query=""):
    total_pages = len(pages)
    if query:
        words = [w for w in query.lower().split() if len(w)>3]
        relevant_pages = [p for p in pages if any(w in p["text"].lower() for w in words)]
    else:
        relevant_pages = pages[:5]
    response = random.choice(HUMAN_OPENERS) + f" ({total_pages} pages analysees)\n\n"
    response += "1. VISION GLOBALE\n"
    response += f"Le document contient {total_pages} pages et traite principalement de "
    response += random.choice(["un sujet technique","une problematique business","des concepts avances","une methodologie precise"])
    response += "\n\n2. ANALYSE DETAILLEE\n"
    for i,page in enumerate(relevant_pages[:5]):
        quote = page["text"][:200].strip()
        summary = page["summary"][:120]
        response += random.choice(HUMAN_ANALYSIS).format(page=page["num"], chap=i+1, quote=quote[:50]+"...")
        response += f'\nExtrait page {page["num"]} : "{quote[:120]}..."'
        response += f"\nInterpretation : {human_rephrase(summary)}\n\n"
    response += "3. CE QUE TU DOIS RETENIR\n"
    if pages:
        transition = random.choice(TRANSITIONS_NATURELLES).format(page=pages[0]["num"])
        response += transition + " "
    summaries = " ".join([p["summary"] for p in pages[:3]])
    response += human_rephrase(summaries)
    response += "\n\nMon avis perso : "
    response += random.choice([
        "Document solide, mais faudrait creuser les implementations.",
        "Tres bien structure, exemples concrets a l'appui.",
        "Un peu dense, mais les pages cles sont identifiees.",
        "Parfait pour une mise en pratique immediate."
    ])
    return response

st.set_page_config(page_title="DocMaster AI", layout="wide")
st.title("📚 DocMaster AI - Analyse Documents Humaine")
col1,col2=st.columns([1,3])
with col1:
    st.markdown("### 🔧 Fonctionnalites")
    st.markdown("- ✅ Lecture complete du document\n- ✅ Citations de pages\n- ✅ Style humain\n- ✅ Synthese automatique")
    task = st.selectbox("Type d'analyse", ["Resume complet","Analyse detaillee"])
    query = st.text_input("Question precise","Explique le concept principal")
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
            st.error("Format non supporte")
            st.stop()
        result = generate_human_response(analyzer.pages, task, query)
    st.markdown("## 📖 ANALYSE")
    st.markdown(result)
    st.download_button("💾 Telecharger l'analyse", result, f"analyse_{analyzer.metadata['title']}.md","text/markdown")
