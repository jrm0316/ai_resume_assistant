import streamlit as st
import requests

API_URL = "http://127.0.0.1:9000"

st.set_page_config(page_title="AI Resume Assistant", layout="wide")

st.title("🤖 AI Resume Assistant")

# =========================
# SIDEBAR
# =========================
st.sidebar.title("Menu")

option = st.sidebar.radio(
    "Escolha uma opção:",
    ["Chat com Documento", "Analisar Currículo", "Comparar com Vaga"]
)

# =========================
# 1. CHAT (RAG)
# =========================
if option == "Chat com Documento":
    st.header("📄 Chat com Documento (RAG)")

    if "doc_loaded" not in st.session_state:
        st.session_state.doc_loaded = False

    uploaded_file = st.file_uploader("Upload do arquivo (.txt)", type=["txt"])

    if uploaded_files:
        if st.button("Processar documento"):
            with st.spinner("Processando..."):
                res = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, "text/plain")}
                )

                if res.status_code == 200:
                    st.success("Documento processado!")
                    st.session_state.doc_loaded = True
                else:
                    st.error(f"Erro: {res.text}")

    if st.session_state.doc_loaded:
        question = st.text_input("Faça uma pergunta:", key="chat_question")

        if st.button("Perguntar"):
            res = requests.post(
                f"{API_URL}/chat",
                json={"question": question}
            )

            data = res.json()

            st.subheader("Resposta:")
            st.write(data["answer"])

            st.subheader("Fontes:")
            for src in data["sources"]:
                st.write(f"📌 {src['content']}")
                st.write(f"Score: {round(src['score'], 2)}")
                st.write("---")
    else:
        st.warning("⚠️ Faça upload e processe o documento primeiro.")


# =========================
# 2. ANALYZE
# =========================
elif option == "Analisar Currículo":
    st.header("📊 Analisar Currículo")

    text = st.text_area("Cole seu currículo aqui:", key="cv_interview")

    if st.button("Analisar"):
        res = requests.post(
            f"{API_URL}/analyze",
            json={"text": text}
        )

        data = res.json()

        if "erro" in data:
            st.error(data["erro"])
            st.write(data.get("raw", ""))
        else:
            st.success(f"Nível: {data['nivel']}")

            st.subheader("Pontos Fortes")
            for item in data["pontos_fortes"]:
                st.write(f"✅ {item}")

            st.subheader("Pontos Fracos")
            for item in data["pontos_fracos"]:
                st.write(f"❌ {item}")

            st.subheader("Sugestões")
            for item in data["sugestoes"]:
                st.write(f"💡 {item}")


# =========================
# 3. COMPARE
# =========================
elif option == "Comparar com Vaga":
    st.header("⚔️ Comparar com Vaga")

    resume = st.text_area("Currículo", key="cv_match")
    job = st.text_area("Descrição da vaga", key="job_match")

    if st.button("Comparar"):
        res = requests.post(
            f"{API_URL}/compare",
            json={
                "resume": resume,
                "job": job
            }
        )

        data = res.json()

        if "erro" in data:
            st.error(data["erro"])
            st.write(data.get("raw", ""))
        else:
            st.metric("Match", f"{data['match']}%")

            st.subheader("Faltando (Obrigatório)")
            for item in data.get("faltando_obrigatorio", []):
                st.write(f"🔴 {item}")

            st.subheader("Faltando (Desejável)")
            for item in data.get("faltando_desejavel", []):
                st.write(f"🟡 {item}")

            st.subheader("Pontos Fortes")
            for item in data["pontos_fortes"]:
                st.write(f"🟢 {item}")

            st.subheader("Resumo")
            st.write(data["resumo"])