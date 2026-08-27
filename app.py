"""
Comparador de PDFs - Streamlit + pdfplumber
--------------------------------------------
Permite que o usuário envie dois (ou mais) arquivos PDF, extrai o texto e as
tabelas de cada um usando pdfplumber, cruza os dados e mostra as diferenças
encontradas. Caso não haja diferenças, informa que nada foi encontrado.
"""

import difflib
import itertools

import pandas as pd
import pdfplumber
import streamlit as st

st.set_page_config(page_title="Comparador de PDFs", layout="wide")
st.title("📄 Comparador de PDFs")
st.write(
    "Envie dois ou mais arquivos PDF. O sistema vai extrair o **texto** e as "
    "**tabelas** de cada um e mostrar o que é diferente entre eles."
)


def extrair_dados_pdf(arquivo):
    dados = {"texto_paginas": [], "tabelas": []}
    with pdfplumber.open(arquivo) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text() or ""
            dados["texto_paginas"].append(texto)
            tabelas_pagina = pagina.extract_tables()
            for j, tabela in enumerate(tabelas_pagina, start=1):
                tabela_normalizada = [
                    [(cel if cel is not None else "").strip() for cel in linha]
                    for linha in tabela
                ]
                dados["tabelas"].append(
                    {"pagina": i, "indice": j, "linhas": tabela_normalizada}
                )
    dados["texto_completo"] = "\n".join(dados["texto_paginas"])
    return dados


def comparar_textos(texto_a, texto_b, nome_a, nome_b):
    linhas_a = texto_a.splitlines()
    linhas_b = texto_b.splitlines()
    diff = list(
        difflib.unified_diff(
            linhas_a, linhas_b, fromfile=nome_a, tofile=nome_b, lineterm=""
        )
    )
    mudancas = [
        l for l in diff if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))
    ]
    return diff, mudancas


def comparar_tabelas(tabelas_a, tabelas_b):
    relatorios = []
    total_pares = max(len(tabelas_a), len(tabelas_b))
    for idx in range(total_pares):
        tab_a = tabelas_a[idx] if idx < len(tabelas_a) else None
        tab_b = tabelas_b[idx] if idx < len(tabelas_b) else None
        if tab_a is None:
            relatorios.append({
                "titulo": f"Tabela {idx + 1}: existe apenas no segundo arquivo (página {tab_b['pagina']})",
                "diferencas": None, "so_existe_em": "b",
            })
            continue
        if tab_b is None:
            relatorios.append({
                "titulo": f"Tabela {idx + 1}: existe apenas no primeiro arquivo (página {tab_a['pagina']})",
                "diferencas": None, "so_existe_em": "a",
            })
            continue
        linhas_a = tab_a["linhas"]
        linhas_b = tab_b["linhas"]
        max_linhas = max(len(linhas_a), len(linhas_b))
        diffs_celulas = []
        for r in range(max_linhas):
            linha_a = linhas_a[r] if r < len(linhas_a) else []
            linha_b = linhas_b[r] if r < len(linhas_b) else []
            max_cols = max(len(linha_a), len(linha_b))
            for c in range(max_cols):
                val_a = linha_a[c] if c < len(linha_a) else ""
                val_b = linha_b[c] if c < len(linha_b) else ""
                if val_a != val_b:
                    diffs_celulas.append({
                        "linha": r + 1, "coluna": c + 1,
                        "valor_arquivo_1": val_a, "valor_arquivo_2": val_b,
                    })
        relatorios.append({
            "titulo": f"Tabela {idx + 1} (pág. {tab_a['pagina']} / pág. {tab_b['pagina']})",
            "diferencas": diffs_celulas, "so_existe_em": None,
        })
    return relatorios


arquivos = st.file_uploader(
    "Envie os arquivos PDF para comparar (selecione 2 ou mais)",
    type=["pdf"], accept_multiple_files=True,
)

if arquivos and len(arquivos) < 2:
    st.warning("Envie pelo menos **2 arquivos PDF** para que a comparação seja feita.")

if arquivos and len(arquivos) >= 2:
    with st.spinner("Extraindo dados dos PDFs..."):
        dados_extraidos = {}
        for arq in arquivos:
            dados_extraidos[arq.name] = extrair_dados_pdf(arq)

    nomes = list(dados_extraidos.keys())
    st.success(f"{len(nomes)} arquivo(s) processado(s) com sucesso.")
    pares = list(itertools.combinations(nomes, 2))

    for nome_a, nome_b in pares:
        st.markdown("---")
        st.subheader(f"🔍 Comparando: `{nome_a}` × `{nome_b}`")
        dados_a = dados_extraidos[nome_a]
        dados_b = dados_extraidos[nome_b]
        houve_diferenca = False

        diff_texto, mudancas_texto = comparar_textos(
            dados_a["texto_completo"], dados_b["texto_completo"], nome_a, nome_b
        )
        with st.expander("📝 Diferenças de texto", expanded=bool(mudancas_texto)):
            if mudancas_texto:
                houve_diferenca = True
                st.code("\n".join(diff_texto), language="diff")
            else:
                st.info("Nenhuma diferença de texto encontrada entre os dois arquivos.")

        relatorios_tabelas = comparar_tabelas(dados_a["tabelas"], dados_b["tabelas"])
        with st.expander("📊 Diferenças de tabelas", expanded=True):
            if not relatorios_tabelas:
                st.info("Nenhuma tabela foi encontrada em nenhum dos arquivos.")
            else:
                algo_diferente_em_tabela = False
                for rel in relatorios_tabelas:
                    if rel["so_existe_em"] is not None:
                        algo_diferente_em_tabela = True
                        houve_diferenca = True
                        st.warning(rel["titulo"])
                        continue
                    if rel["diferencas"]:
                        algo_diferente_em_tabela = True
                        houve_diferenca = True
                        st.markdown(f"**{rel['titulo']}** — {len(rel['diferencas'])} diferença(s):")
                        df_dif = pd.DataFrame(rel["diferencas"])
                        st.dataframe(df_dif, use_container_width=True)
                    else:
                        st.markdown(f"**{rel['titulo']}** — sem diferenças.")
                if not algo_diferente_em_tabela:
                    st.info("Nenhuma diferença encontrada nas tabelas.")

        if not houve_diferenca:
            st.success(f"✅ Nenhuma diferença encontrada entre `{nome_a}` e `{nome_b}`.")
        else:
            st.error(f"⚠️ Foram encontradas diferenças entre `{nome_a}` e `{nome_b}`.")
