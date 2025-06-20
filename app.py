import pandas as pd
import streamlit as st

st.title("🔍 Comparador de Placas entre Vários Arquivos Excel")

uploaded_files = st.file_uploader(
    "📁 Envie 2 ou mais arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

dfs = []

def placas_depois_de(placa, df):
    """
    Recebe uma placa (str) e dataframe concatenado com colunas ['Placa', '_arquivo_'].
    Para cada ocorrência da placa, retorna as placas que aparecem depois no mesmo arquivo (sequência).
    """
    placa = placa.strip().upper()
    resultados = {}

    # Vamos iterar por arquivo para manter a ordem da sequência
    arquivos = df['_arquivo_'].unique()
    for arq in arquivos:
        df_arquivo = df[df['_arquivo_'] == arq].reset_index(drop=True)
        indices = df_arquivo.index[df_arquivo['Placa'] == placa].tolist()
        if not indices:
            continue
        for idx in indices:
            # Placas depois da posição idx (exclusivo)
            placas_apos = df_arquivo.loc[idx+1:, 'Placa'].unique().tolist()
            if placas_apos:
                chave = f"{arq} (após índice {idx})"
                resultados[chave] = placas_apos

    return resultados

if uploaded_files:
    if len(uploaded_files) < 2:
        st.warning("⚠️ Envie pelo menos 2 arquivos para comparar.")
    else:
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                df.columns = [str(c).strip().lower() for c in df.columns]

                if 'placa' in df.columns:
                    df['Placa'] = df['placa'].astype(str).str.strip().str.upper()
                else:
                    df_sem_header = pd.read_excel(file, header=None, engine='openpyxl')
                    primeira_coluna = df_sem_header.iloc[:, 0]
                    df = pd.DataFrame({
                        'Placa': primeira_coluna.astype(str).str.strip().str.upper()
                    })

                df['_arquivo_'] = file.name
                dfs.append(df[['Placa', '_arquivo_']])
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {e}")

        if len(dfs) >= 2:
            todas = pd.concat(dfs, ignore_index=True)

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

            # NOVO: campo para digitar placa e mostrar as placas que aparecem depois dela
            st.markdown("---")
            placa_input = st.text_input("🔎 Digite a placa para buscar as placas que passaram depois dela")

            if placa_input:
                resultados_placas_apos = placas_depois_de(placa_input, todas)
                if resultados_placas_apos:
                    st.write(f"Placas que apareceram depois da placa *{placa_input.upper()}* nos arquivos:")
                    for k, placas_apos in resultados_placas_apos.items():
                        st.write(f"*{k}:* {placas_apos}")
                else:
                    st.warning(f"Nenhuma ocorrência da placa {placa_input.upper()} encontrada nos arquivos.")
