# 📄 Comparador de PDFs

Aplicativo web feito com **Streamlit** e **pdfplumber** que permite enviar dois ou mais arquivos PDF, extrair texto e tabelas de cada um, cruzar os dados e mostrar exatamente o que é diferente entre eles. Se não houver diferenças, o app informa isso claramente.

## ✨ Funcionalidades

- Upload de múltiplos arquivos PDF pelo navegador.
- Extração de texto por página com `pdfplumber`.
- Extração e comparação de tabelas célula a célula.
- Diff de texto no estilo `unified_diff` (linhas adicionadas/removidas).
- Comparação automática de todos os pares de arquivos enviados.
- Mensagem clara de "nenhuma diferença encontrada" quando os arquivos são iguais.

## 🚀 Como rodar localmente

```bash
git clone https://github.com/IgorASB/comparador-pdf-streamlit.git
cd comparador-pdf-streamlit
pip install -r requirements.txt
streamlit run app.py
```

O app abre automaticamente no navegador em `http://localhost:8501`.

## 🌐 Como publicar online (Streamlit Community Cloud) — grátis

Para seu amigo poder usar pelo navegador sem instalar nada:

1. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com sua conta GitHub.
2. Clique em **"New app"**.
3. Selecione o repositório `IgorASB/comparador-pdf-streamlit`, a branch `main` e o arquivo principal `app.py`.
4. Clique em **"Deploy"**.
5. Em poucos minutos o Streamlit gera um link público (algo como `https://comparador-pdf-streamlit.streamlit.app`) que você pode compartilhar com quem quiser.

Qualquer atualização enviada (push) para a branch `main` deste repositório atualiza automaticamente o app publicado.

## 📁 Estrutura do projeto

```
comparador-pdf-streamlit/
├── app.py             # código principal do Streamlit
├── requirements.txt   # dependências do projeto
└── README.md          # este arquivo
```

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) — interface web
- [pdfplumber](https://github.com/jsvine/pdfplumber) — extração de texto e tabelas de PDF
- [pandas](https://pandas.pydata.org/) — manipulação e exibição de dados tabulares
