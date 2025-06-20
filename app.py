import streamlit as st
import pandas as pd

st.title("Comparador por Placa e Filtro por Modelo")

uploaded_files = st.file_uploader(
    "Envie até 10 arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

# Filtros para até 3 modelos
st.subheader("Filtrar por modelo de veículo (opcional)")
col1, col2, col3 = st.columns(3)
with col1:
    modelo1 = st.text_input("Modelo 1", placeholder="Ex: SW4")
with col2:
    modelo2 = st.text_input("Modelo 2", placeholder="Ex: Hilux")
with col3:
    modelo3 = st.text_input("Modelo 3", placeholder="Ex: Corolla")

modelos_filtrar = [m.strip() for m in [modelo1, modelo2, modelo3] if m.strip()]

if uploaded_files:
    if len(uploaded_files) > 10:
        st.warning("Você só pode enviar até 10 arquivos.")
    else:
        dfs = []
        for file in uploaded_files:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                df.columns = [col.strip() for col in df.columns]

                # Verifica se tem coluna 'Placa'
                if "Placa" not in df.columns:
                    st.error(f"❌ Arquivo {file.name} não tem a coluna 'Placa'.")
                    continue

                # Normaliza placa
                df['Placa'] = df['Placa'].astype(str).str.strip().str.upper()

                # Aplica filtro por modelo, se houver e se coluna 'Modelo' existir
                if modelos_filtrar and 'Modelo' in df.columns:
                    filtro_modelo = pd.Series(False, index=df.index)
                    for modelo in modelos_filtrar:
                        filtro_modelo |= df['Modelo'].astype(str).str.contains(modelo, case=False, na=False)
                    df = df[filtro_modelo]

                df["__arquivo__"] = file.name

                # Seleciona só colunas essenciais para comparação
                dfs.append(df[['Placa', '__arquivo__']])
            except Exception as e:
                st.error(f"Erro ao processar {file.name}: {e}")

        if len(dfs) >= 2:
            try:
                todas_placas = pd.concat(dfs)
                contagem = todas_placas['Placa'].value_counts()
                placas_comuns = contagem[contagem > 1].index.tolist()
                resultado = todas_placas[todas_placas['Placa'].isin(placas_comuns)]

                if not resultado.empty:
                    st.success(f"✅ Foram encontradas {len(placas_comuns)} placas em comum!")
                    st.dataframe(resultado)

                    csv = resultado.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Baixar resultado em CSV", data=csv, file_name="placas_em_comum.csv", mime='text/csv')
                else:
                    st.info("⚠️ Nenhuma placa em comum encontrada com os filtros aplicados.")
            except Exception as e:
                st.error(f"Erro na comparação: {e}")
