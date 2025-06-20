import pandas as pd
import streamlit as st

st.title("🔍 Comparador de Placas entre Vários Arquivos Excel")

uploaded_files = st.file_uploader(
    "📁 Envie 2 ou mais arquivos Excel (.xlsx)",
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
                    # Lê sem cabeçalho, pega a primeira coluna
                    df_sem_header = pd.read_excel(file, header=None, engine='openpyxl')
                    primeira_coluna = df_sem_header.iloc[:, 0]
                    df = pd.DataFrame({
                        'Placa': primeira_coluna.astype(str).str.strip().str.upper()
                    })

                df['_arquivo_'] = file.name
                dfs.append(df[['Placa', '_arquivo_']])
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {e}")

        # Comparar placas entre arquivos
        if len(dfs) >= 2:
            todas = pd.concat(dfs, ignore_index=True)
            # Conta quantos arquivos diferentes cada placa aparece
            placas_por_arquivo = todas.drop_duplicates(subset=['Placa', '_arquivo_'])
            contagem = placas_por_arquivo['Placa'].value_counts()
            placas_em_2_ou_mais = contagem[contagem > 1].index.tolist()

            resultado = todas[todas['Placa'].isin(placas_em_2_ou_mais)]

            if not resultado.empty:
                st.success(f"✅ Encontradas {len(placas_em_2_ou_mais)} placas em comum entre os arquivos!")
                st.dataframe(resultado)

                csv = resultado.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar CSV com Placas em Comum", data=csv, file_name="placas_em_comum.csv", mime='text/csv')
            else:
                st.info("⚠️ Nenhuma placa em comum encontrada entre os arquivos enviados.")
