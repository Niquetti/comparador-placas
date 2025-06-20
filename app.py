import pandas as pd
import streamlit as st

st.title("🔍 Comparador de Placas entre Múltiplos Arquivos Excel")

uploaded_files = st.file_uploader(
    "📁 Envie dois ou mais arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

dfs = []

if uploaded_files:
    if len(uploaded_files) < 2:
        st.warning("⚠️ Envie pelo menos 2 arquivos para comparar.")
    else:
        for file in uploaded_files:
            try:
                # Tenta ler com cabeçalho
                df = pd.read_excel(file, engine='openpyxl')
                df.columns = [str(c).strip().lower() for c in df.columns]

                if 'placa' in df.columns:
                    df['Placa'] = df['placa'].astype(str).str.strip().str.upper()
                else:
                    # Se não tem coluna 'placa', tenta sem cabeçalho (header=None)
                    df = pd.read_excel(file, header=None, engine='openpyxl')
                    df.columns = ['Placa']
                    df['Placa'] = df['Placa'].astype(str).str.strip().str.upper()

                df['_arquivo_'] = file.name
                dfs.append(df[['Placa', '_arquivo_']])
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {e}")

        if len(dfs) >= 2:
            todas = pd.concat(dfs, ignore_index=True)
            contagem = todas['Placa'].value_counts()
            placas_comuns = contagem[contagem > 1].index.tolist()
            resultado = todas[todas['Placa'].isin(placas_comuns)]

            if not resultado.empty:
                st.success(f"✅ Foram encontradas {len(placas_comuns)} placas em comum!")
                st.dataframe(resultado)

                csv = resultado.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV", data=csv, file_name="placas_em_comum.csv", mime='text/csv')
            else:
                st.info("⚠️ Nenhuma placa em comum encontrada.")
