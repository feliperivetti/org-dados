import streamlit as st

def render_sidebar(df):
    """Cria e exibe a barra lateral (sidebar)"""
    st.sidebar.header("Opções de Visualização")
    if st.sidebar.checkbox("Mostrar dados brutos (DataFrame)"):
        st.sidebar.subheader("Dados Completos (2014-2020)")
        st.sidebar.dataframe(df)

    st.sidebar.markdown("---")
    try:
        st.sidebar.info(f"""
        **Dados Carregados:**
        * **{len(df)}** registros (linhas)
        * **{len(df['equipe'].unique())}** equipes únicas
        * **{df['Ano'].min()} a {df['Ano'].max()}** (período)
        """)
    except Exception as e:
        st.sidebar.error(f"Erro ao exibir informações: {e}")