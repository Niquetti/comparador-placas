import pandas as pd
import streamlit as st

st.set_page_config(page_title="Comparador de Placas", layout="wide")
st.title("🚔 Comparador de Placas")

uploaded_files = st.file_uploader(
    "📁 Envie 2 ou mais arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

dfs = []

def buscar_coincidencias_apos_placa(placa_suspeita, todas, placas_em_mais_de_um):
    placa_suspeita = placa_suspeita.strip().upper()
    resultados = []

    for arquivo in todas['_arquivo_'].unique():
        df_arq = todas[todas['_arquivo_'] == arquivo].reset_index(drop=True)
        indices_placa = df_arq.index[df_arq['Placa'] == placa_suspeita].tolist()

        if not indices_placa:
            continue  # Placa digitada não está nesse arquivo

        for idx in indices_placa:
            placas_apos = df_arq.loc[idx+1:, 'Placa'].tolist()
            coincidencias = [p for p in placas_apos if p in placas_em_mais_de_um and p != placa_suspeita]
            coincidencias_unicas = list(dict.fromkeys(coincidencias))

            if coincidencias_unicas:
                resultados.append({
                    'Arquivo': arquivo,
                    'Índice da placa': idx,
                    'Placas coincidentes após': coincidencias_unicas
                })

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
                    df = pd.read_excel(file, header=None, engine='openpyxl')
                    primeira_coluna = df.iloc[:, 0]
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
            placas_em_mais_de_um = contagem[contagem > 1].index.tolist()

            st.markdown("### 🔁 Placas que aparecem em mais de um arquivo:")
            if placas_em_mais_de_um:
                st.write(placas_em_mais_de_um)
            else:
                st.info("Nenhuma placa aparece em mais de um arquivo.")

            st.markdown("### 🔎 Buscar coincidências após uma placa específica")
            placa_input = st.text_input("Digite a placa suspeita (ex: ABC1D23)")

            if placa_input:
                # Verifica se placa existe em algum arquivo
                placas_todas = todas['Placa'].unique().tolist()
                if placa_input.strip().upper() not in placas_todas:
                    st.warning(f"A placa {placa_input.upper()} não foi encontrada em nenhum arquivo.")
                    st.info("Confira a lista de placas que aparecem em mais de um arquivo acima.")
                else:
                    resultado = buscar_coincidencias_apos_placa(placa_input, todas, placas_em_mais_de_um)
                    if resultado:
                        st.success(f"✅ Coincidências encontradas após {placa_input.upper()}:")
                        for r in resultado:
                            st.write(f"📂 Arquivo: *{r['Arquivo']}, após índice *{r['Índice da placa']}**")
                            st.write(r['Placas coincidentes após'])
                            st.markdown("---")
                    else:
                        st.warning(f"Nenhuma coincidência encontrada após *{placa_input.upper()}*.")

# Rodapé com assinatura
st.markdown("<hr style='margin-top: 50px;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px;'>Desenvolvido por <strong>Niquetti</strong> 🚔</p>", unsafe_allow_html=True)
def buscar_coincidencias_apos_placa(placa_suspeita, todas, placas_em_mais_de_um):
    placa_suspeita = placa_suspeita.strip().upper()
    resultados = []

    for arquivo in todas['_arquivo_'].unique():
        df_arq = todas[todas['_arquivo_'] == arquivo].reset_index(drop=True)
        indices_placa = df_arq.index[df_arq['Placa'] == placa_suspeita].tolist()

        if not indices_placa:
            continue

        for idx in indices_placa:
            placas_apos = df_arq.loc[idx+1:, 'Placa'].tolist()
            coincidencias = [p for p in placas_apos if p in placas_em_mais_de_um and p != placa_suspeita]
            coincidencias_unicas = list(dict.fromkeys(coincidencias))

            if coincidencias_unicas:
                resultados.append({
                    'Arquivo': arquivo,
                    'Índice da placa': idx,
                    'Placas coincidentes após': coincidencias_unicas
                })

    return resultados


# Dentro do if placa_input:
if placa_input:
    placa_normalizada = placa_input.strip().upper()
    placas_todas = todas['Placa'].unique().tolist()

    if placa_normalizada not in placas_todas:
        st.warning(f"A placa *{placa_normalizada}* não foi encontrada em nenhum arquivo.")
        st.info("Confira a lista de placas que aparecem em mais de um arquivo acima.")
    else:
        resultado = buscar_coincidencias_apos_placa(placa_input, todas, placas_em_mais_de_um)
        if resultado:
            st.success(f"✅ Coincidências encontradas após {placa_normalizada}:")
            for r in resultado:
                st.write(f"📂 Arquivo: *{r['Arquivo']}, após índice *{r['Índice da placa']}**")
                st.write(r['Placas coincidentes após'])
                st.markdown("---")
        else:
            st.warning(f"❌ Nenhuma coincidência encontrada após a placa *{placa_normalizada}*.")
