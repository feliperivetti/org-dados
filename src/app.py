import streamlit as st
import seaborn as sns

# Importações dos componentes
from components.data_loader import carregar_e_preparar_dados
from components.sidebar import render_sidebar
from components.tabs import (
    render_tab_tendencias, 
    render_tab_correlacoes, 
    render_tab_analise_time
)
from components.prediction import (
    train_model, 
    render_tab_previsao
)
from components.utils import COLUNAS_METRICAS, PASTA_DADOS

# Configurações da Página
st.set_page_config(layout="wide", page_title="Análise Brasileirão")
sns.set_theme(style="whitegrid", palette="muted")

def main():
    """Função principal que executa o aplicativo Streamlit."""
    st.title("📊 Análise de Dados do Brasileirão (2013-2020)")
    st.markdown("Use as abas abaixo para explorar diferentes visões dos dados.")
    
    # Carrega os dados usando o componente
    df = carregar_e_preparar_dados(PASTA_DADOS)
    
    if df is None:
        st.error("Carregamento de dados falhou. O aplicativo não pode continuar.")
        st.stop()
        
    # Cálculos globais
    try:
        df_medias_ano = df.groupby('Ano')[COLUNAS_METRICAS].mean()
        anos_completos = range(df['Ano'].min(), df['Ano'].max() + 1)
    except Exception as e:
        st.error(f"Erro ao calcular médias ou anos: {e}")
        st.stop()
        
    # Renderiza a barra lateral usando o componente
    render_sidebar(df)

    # --- [NOVO] Treina o modelo (só executa na 1ª vez, depois usa o cache) ---
    model, features = train_model(df)
    # --- [FIM NOVO] ---

    # --- [ALTERADO] Adiciona a 'tab4' ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Análise de Tendências", 
        "🔗 Correlações", 
        "⚽ Análise por Time",
        "🔮 Simulador (Previsão)"  # Nova aba
    ])
    # --- [FIM ALTERADO] ---

    # Renderiza o conteúdo de cada aba
    with tab1:
        render_tab_tendencias(df)
    
    with tab2:
        render_tab_correlacoes(df)
    
    with tab3:
        render_tab_analise_time(df, df_medias_ano, anos_completos)
        
    with tab4:
        render_tab_previsao(df, model, features)

# Ponto de Entrada do Script
if __name__ == "__main__":
    main()