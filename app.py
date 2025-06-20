import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador por Placa", layout="wide")
st.title("📊 Comparador de Arquivos Excel por Placa e Modelo")

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

modelos_filtrar = [m for m in [modelo1, modelo2, modelo3] if m]

if uploaded_files:
    if len(uploaded_files) > 10:
        st.warning("Você só pode enviar até 10 arquivos.")
    else:
        dfs = []
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, engine='openpyxl')

                # Normaliza nome da coluna
                df.columns = [col.strip().lower() for col in df.columns]

                # Procura coluna de placa
                placa_col = next((col for col in df.columns if 'placa' in col), None)
                if not placa_col:
                    st.error(f"❌ Arquivo {file.name} não tem coluna de placa.")
                    continue

                df['placa'] = df[placa_col].astype(str).str.strip().str.upper()
                df["__arquivo__"] = file.name

                # Aplica filtros de modelo, se houver
                if modelos_filtrar:
                    filtro = pd.Series([False] * len(df))
                    for modelo in modelos_filtrar:
                        for col in df.columns:
                            filtro |= df[col].astype(str).str.contains(modelo, case=False, na=False)
                    df = df[filtro]

                dfs.append(df[['placa', '__arquivo__']])  # Só a placa e nome do arquivo
            except Exception as e:
                st.error(f"Erro ao processar {file.name}: {e}")

        if len(dfs) >= 2:
            try:
                # Junta todas as placas em um único dataframe
                todas_placas = pd.concat(dfs)

                # Conta quantas vezes cada placa aparece
                duplicadas = todas_placas['placa'].value_counts()
                placas_comuns = duplicadas[duplicadas > 1].index.tolist()

                resultado = todas_placas[todas_placas['placa'].isin(placas_comuns)]

                if not resultado.empty:
                    st.success(f"✅ Foram encontradas {len(placas_comuns)} placas em comum!")
                    st.dataframe(resultado)

                    # Baixar CSV
                    csv = resultado.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="placas_em_comum.csv", mime='text/csv')
                else:
                    st.info("⚠️ Nenhuma placa em comum foi encontrada.")
            except Exception as e:
                st.error(f"Erro na comparação: {e}")
