# AI Resume Assistant

Aplicação de análise de currículos com Inteligência Artificial, desenvolvida em **Python**, utilizando **FastAPI, Streamlit, FAISS, RAG e modelos de linguagem (LLMs)**.

O projeto permite consultar documentos, analisar perfis profissionais e comparar currículos com descrições de vagas, auxiliando na identificação de competências e oportunidades de melhoria.

## Funcionalidades

### Chat com Documento (RAG)

- Upload e processamento de documentos.
- Extração de conteúdo textual.
- Busca semântica utilizando FAISS.
- Geração de respostas com modelos de linguagem.
- Exibição dos trechos recuperados e suas pontuações de similaridade.

**Status:** upload de PDF e consultas RAG testados com sucesso. A recuperação de informações ainda pode ser aprimorada para produzir respostas mais completas.

### Análise de Currículo

- Classificação estimada de senioridade: Júnior, Pleno ou Sênior.
- Identificação de competências e pontos fortes.
- Identificação de informações ausentes ou oportunidades de melhoria.
- Sugestões de desenvolvimento profissional.

A classificação é produzida por IA e não substitui uma avaliação profissional de senioridade.

### Comparação com Vagas

- Comparação entre o texto do currículo e os requisitos de uma vaga.
- Estimativa percentual de compatibilidade.
- Identificação de requisitos obrigatórios não mencionados.
- Identificação de requisitos desejáveis não mencionados.
- Destaque de competências relevantes.
- Geração de resumo da análise.

**Observação:** o percentual de compatibilidade é estimado pelo modelo de linguagem e não representa uma pontuação estatisticamente validada.

## Tecnologias Utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal |
| FastAPI | Desenvolvimento da API REST |
| Streamlit | Interface web |
| FAISS | Indexação e busca vetorial |
| LangChain | Integração com componentes de IA |
| Hugging Face | Geração de embeddings |
| Groq | Acesso ao modelo de linguagem |
| GPT-OSS 120B | Modelo utilizado nos testes de geração de respostas |

## Estrutura do Projeto

```text
ai_resume_assistant/
├── backend/
│   ├── db/
│   ├── routes/
│   ├── services/
│   └── main.py
├── frontend/
│   └── streamlit_app.py
├── requirements.txt
├── README.md
└── .gitignore
```

O projeto também utiliza arquivos de índice vetorial e dados associados ao processamento dos documentos.

## Instalação e Execução

### 1. Clonar o repositório

```bash
git clone https://github.com/jrm0316/ai_resume_assistant.git
cd ai_resume_assistant
```

### 2. Criar o ambiente virtual

No Windows, utilizando Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

As dependências devem estar atualizadas para incluir os pacotes necessários ao backend e ao frontend.

### 4. Configurar a API da Groq

Crie um arquivo `.env` na pasta `backend`, conforme a configuração utilizada na execução local:

```dotenv
GROQ_API_KEY=sua_chave_aqui
```

Nunca publique sua chave de API no repositório.

### 5. Iniciar o backend

```powershell
cd backend
python -m uvicorn main:app --reload --port 8000
```

Documentação interativa da API:

http://127.0.0.1:8000/docs

### 6. Iniciar o frontend

Abra outro terminal na pasta principal do projeto e execute:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend\streamlit_app.py
```

A interface normalmente estará disponível em:

http://localhost:8501

O frontend deve estar configurado para utilizar o endereço `http://127.0.0.1:8000`.

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/upload` | Processamento de documentos |
| POST | `/chat` | Perguntas e respostas com RAG |
| POST | `/analyze` | Análise de currículo |
| POST | `/match` | Comparação de currículo e vaga |
| POST | `/compare` | Comparação de currículo e vaga |

## Testes Realizados

Foram realizados testes manuais utilizando o Swagger UI do FastAPI.

**Resultados:**
- Inicialização do backend: aprovada.
- Upload de PDF: aprovado.
- Chat com RAG: funcional, com oportunidades de melhoria na recuperação.
- Análise de currículo: aprovada no cenário testado.
- Comparação de currículo e vaga: funcional nos dois endpoints.
- Interface Streamlit: inicialização e funcionalidades ainda dependem de validação completa.

## Melhorias Futuras

- Aprimorar a recuperação de contexto no RAG.
- Avaliar e calibrar o percentual de compatibilidade.
- Validar os formatos de upload disponíveis.
- Melhorar o tratamento de erros e a experiência da interface.
- Adicionar testes automatizados.
- Revisar e atualizar as dependências do projeto.
- Preparar a aplicação para implantação.

## Diferenciais do Projeto

- Aplicação prática de RAG em documentos.
- Integração entre API REST, busca vetorial e LLM.
- Separação de responsabilidades entre rotas e serviços.
- Interface web para interação com as funcionalidades de IA.
- Aplicação de inteligência artificial ao contexto de recrutamento e análise profissional.

## Autor

**Juliano Rodrigues Madeira**

GitHub: https://github.com/jrm0316
