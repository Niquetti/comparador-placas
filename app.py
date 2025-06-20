import re
import streamlit as st
import pandas as pd

st.title("Comparador por Placa e Filtro por Modelo")

uploaded_files = st.file_uploader(
    "Envie até 10 arquivos Excel (.xlsx)",
    type=["xlsx"],
    accept_multiple_files=True
)

# Filtros opcais por modelo
st.subheader("Filtrar por modelo de veículo (opcional)")
col1, col2, col3 = st.columns(3)
with col1:
    m1 = st.text_input("Modelo 1", placeholder="Ex: SW4")
with col2:
    m2 = st.text_input("Modelo 2", placeholder="Ex: Hilux")
with col3:
    m3 = st.text_input("Modelo 3", placeholder="Ex: Corolla")

modelos_filtrar = [m.strip() for m in (m1, m2, m3) if m.strip()]

# Regex para placas Mercosul (ABC1D23)
placa_regex = re.compile(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$')

def detecta_plca_col(df: pd.DataFrame) -> str | None:
    """Retorna o nome da coluna que parece conter placas."""
    # 1) se já existe 'Placa'
    for c in df.columns:
        if c.strip().lower() == 'placa':
            return c
    # 2) testa a primeira coluna
    col0 = df.iloc[:, 0].astype(str).str.strip().str.upper()
    pct = (col0.str.match(placa_regex).sum() / max(1, len(col0))) * 100
    if pct >= 80:  # se ≥ 80% batem com regex, assume que é placa
        return df.columns[0]
    return None

dfs = []
if uploaded_files:
    if len(uploaded_files) > 10:
        st.warning("Você só pode enviar até 10 arquivos.")
    else:
        for file in uploaded_files:
            df = None
            # 1ª tentativa: cabeçalho normal
            try:
                df0 = pd.read_excel(file, engine='openpyxl', header=0)
                df0.columns = [c.strip() for c in df0.columns]
                nome_col = detecta_plca_col(df0)
                if nome_col:
                    df = df0
                else:
                    # 2ª tentativa: seu relatório LPR (header na linha 6 do arquivo, index=5)
                    df5 = pd.read_excel(file, engine='openpyxl', header=5)
                    df5.columns = [c.strip() for c in df5.columns]
                    if 'Placa' in df5.columns:
                        nome_col = 'Placa'
                        df = df5
            except Exception as e:
                st.error(f"Erro ao ler {file.name}: {e}")
                continue

            if df is None:
                st.error(f"❌ Não localizei coluna de placa em {file.name}.")
                continue

            # padroniza placa
            df['Placa'] = (
                df[nome_col]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            # filtra por modelo
            if modelos_filtrar and 'Modelo' in df.columns:
                máscara = pd.Series(False, index=df.index)
                for md in modelos_filtrar:
                    máscara |= df['Modelo'].astype(str).str.contains(md, case=False, na=False)
                df = df[máscara]

            df['_arquivo_'] = file.name
            dfs.append(df[['Placa', '_arquivo_']])

        # faz a junção e conta
        if len(dfs) >= 2:
            todas = pd.concat(dfs, ignore_index=True)
            cont = todas['Placa'].value_counts()
            comuns = cont[cont > 1].index.tolist()
            result = todas[todas['Placa'].isin(comuns)]

            if not result.empty:
                st.success(f"✅ {len(comuns)} placa(s) em comum:")
                st.dataframe(result)
                csv = result.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Baixar CSV",
                    data=csv,
                    file_name="placas_em_comum.csv",
                    mime='text/csv'
                )
            else:
                st.info("⚠️ Nenhuma placa em comum encontrada.")
        else:
            st.info("Envie pelo menos 2 arquivos para comparar.")
