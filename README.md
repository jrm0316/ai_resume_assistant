AI Resume Assistant

Um sistema completo de análise de currículos com IA, utilizando RAG (Retrieval-Augmented Generation), FastAPI e Streamlit.

O projeto permite:
- 📄 Fazer perguntas sobre documentos (RAG)
- 📊 Analisar currículos automaticamente
- ⚔️ Comparar candidatos com vagas

---

## 🚀 Funcionalidades

### 📄 Chat com Documento (RAG)
- Upload de arquivos `.txt`
- Busca semântica com FAISS
- Respostas baseadas no conteúdo do documento
- Exibição de fontes com score de relevância

---

### 📊 Analisar Currículo
- Classificação de nível (Júnior, Pleno, Sênior)
- Identificação de:
  - Pontos fortes
  - Pontos fracos
  - Sugestões de melhoria

---

### ⚔️ Comparar com Vaga
- Calcula o **match (%)** entre currículo e vaga
- Divide em:
  - Requisitos obrigatórios faltantes
  - Requisitos desejáveis
- Destaca pontos fortes
- Gera resumo automático

---

## 🧠 Tecnologias Utilizadas
- **Python**
- **FastAPI** → Backend (API REST)
- **Streamlit** → Interface web
- **FAISS** → Busca vetorial
- **LLMs (IA)** → Análise e geração de respostas

---
## 📁 Estrutura do Projeto

ai-resume-assistant/
│

├── backend/

│ ├── routes/

│ ├── services/

│ ├── main.py

│

├── frontend/

│ └── streamlit_app.py

│
├── index.faiss

├── textos.pkl

├── requirements.txt

├── .env

└── .gitignore

---

## ⚙️ Como rodar o projeto

1️⃣ Clonar repositório
```bash
git clone https://github.com/jrm0316/ai_resume_assistant.git
cd ai_resume_assistant

2️⃣ Backend
cd backend

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r ../requirements.txt

uvicorn main:app --reload --port 9000

3️⃣ Frontend (Streamlit)
Em outro terminal:

cd frontend
streamlit run streamlit_app.py

🌐 Acessos
Backend: http://127.0.0.1:9000/docs
Frontend: aberto automaticamente pelo Streamlit

📌 Exemplos de uso
  * Chat com Documento

Pergunta:
  * O que é FastAPI?

Resposta:
  * FastAPI é usado para criar APIs rápidas.

Análise de Currículo
Entrada:
 * Desenvolvedor Python com experiência em APIs REST usando FastAPI

Saída:
  * Nível: Pleno
  * Pontos fortes e sugestões automáticas

Comparação com Vaga
Entrada:
  * Currículo: Python + FastAPI
  * Vaga: Python, FastAPI, Docker

Saída:
  * Match: 60%
  * Faltando: Docker

🔥 Diferenciais do Projeto
  * Uso de RAG na prática
  * Integração completa Backend + IA + Frontend
  * Estrutura modular (routes + services)
  * Aplicação real para recrutamento

### Autor
  * Desenvolvido por Juliano Rodrigues Madeira
