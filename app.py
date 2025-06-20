import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador de Arquivos", layout="wide")
st.title("📊 Comparador de Arquivos Excel por Modelo de Veículo")

# Upload múltiplo de arquivos (até 10)
uploaded_files = st.file_uploader(
    "📁 Envie até 10 arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

# Filtros por modelo (até 3 modelos)
st.subheader("🚗 Filtrar por modelo de veículo (opcional)")
col1, col2, col3 = st.columns(3)
with col1:
    modelo1 = st.text_input("Modelo 1", placeholder="Ex: SW4")
with col2:
    modelo2 = st.text_input("Modelo 2", placeholder="Ex: Hilux")
with col3:
    modelo3 = st.text_input("Modelo 3", placeholder="Ex: Corolla")

# Coletar modelos preenchidos
modelos_filtrar = [m for m in [modelo1, modelo2, modelo3] if m]

if uploaded_files:
    if len(uploaded_files) > 10:
        st.warning("Você só pode enviar até 10 arquivos.")
    else:
        dfs = []
        nomes = []

        for file in uploaded_files:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                df["__arquivo__"] = file.name  # Marcar origem
                dfs.append(df)
                nomes.append(file.name)
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {e}")

        if len(dfs) >= 2:
            st.subheader("🔍 Comparação de registros em comum")

            # Aplicar filtro por modelos, se houver
            if modelos_filtrar:
                dfs_filtrados = []
                for df in dfs:
                    filtro_geral = pd.Series([False] * len(df))
                    for modelo in modelos_filtrar:
                        filtro = df.apply(lambda row: row.astype(str).str.contains(modelo, case=False).any(), axis=1)
                        filtro_geral = filtro_geral | filtro
                    df_filtrado = df[filtro_geral]
                    dfs_filtrados.append(df_filtrado)
                dfs = dfs_filtrados

            try:
                comum = dfs[0]
                for df in dfs[1:]:
                    comum = pd.merge(comum, df, how='inner')

                if not comum.empty:
                    st.success("✅ Registros em comum encontrados!")
                    st.dataframe(comum)

                    csv = comum.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="comparacao_filtrada.csv", mime='text/csv')
                else:
                    st.info("⚠️ Nenhum registro em comum encontrado com os filtros aplicados.")
            except Exception as e:
                st.error(f"Erro na comparação: {e}")
