import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador de Placas", layout="centered")
st.title("🔍 Comparador de Placas entre dois arquivos Excel")

st.markdown("Envie dois arquivos Excel com uma coluna de placas para comparar quais **aparecem nos dois locais**.")

file1 = st.file_uploader("Arquivo Excel 1", type=["xlsx"])
file2 = st.file_uploader("Arquivo Excel 2", type=["xlsx"])

if file1 and file2:
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)

        colunas1 = df1.columns.tolist()
        colunas2 = df2.columns.tolist()

        coluna_placa1 = st.selectbox("Selecione a coluna de placas do Arquivo 1", colunas1)
        coluna_placa2 = st.selectbox("Selecione a coluna de placas do Arquivo 2", colunas2)

        placas1 = df1[coluna_placa1].astype(str).str.strip().str.upper()
        placas2 = df2[coluna_placa2].astype(str).str.strip().str.upper()

        placas_comuns = placas1[placas1.isin(placas2)].drop_duplicates()

        st.success(f"Placas encontradas nos dois arquivos: {len(placas_comuns)}")
        st.dataframe(placas_comuns)

        if not placas_comuns.empty:
            resultado = pd.DataFrame(placas_comuns, columns=["Placas em Comum"])
            excel_data = resultado.to_excel(index=False, engine='openpyxl')

            st.download_button(
                label="📥 Baixar resultado em Excel",
                data=excel_data,
                file_name="placas_em_comum.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao processar os arquivos: {e}")