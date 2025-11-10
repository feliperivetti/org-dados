import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .utils import COLUNAS_METRICAS, formatar_nome

@st.cache_resource
def train_model(df):
    """
    Treina um modelo para prever a 'colocacao_final'.
    """
    features = COLUNAS_METRICAS
    
    # --- [ALTERADO] ---
    target = 'colocacao_final' # Alvo da previsão atualizado
    # --- [FIM DA ALTERAÇÃO] ---
    
    if target not in df.columns:
        st.error(f"A coluna alvo '{target}' não foi encontrada para treinar o modelo.")
        return None, None

    X = df[features]
    y = df[target]
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return model, features

def render_tab_previsao(df, model, features):
    """
    Renderiza a aba de previsão interativa com sliders.
    """
    # --- [ALTERADO] ---
    st.header("🔮 Simulador de Colocação Final")
    st.markdown("Use os sliders abaixo para simular as estatísticas de um time e prever sua colocação final.")
    st.warning("Aviso: Esta é uma previsão estatística baseada em dados de 2014-2020 e não garante resultados reais.", icon="⚠️")
    
    col1, col2 = st.columns(2)
    
    input_data = {}
    
    try:
        stats = df[features].describe().loc[['min', 'max', '50%']]
    except KeyError:
        st.error("Erro ao calcular estatísticas. Verifique as colunas do seu DataFrame.")
        return

    # Sliders na Coluna 1
    with col1:
        input_data['gols'] = st.slider(
            formatar_nome('gols'), 
            int(stats.loc['min', 'gols']), 
            int(stats.loc['max', 'gols']), 
            int(stats.loc['50%', 'gols'])
        )
        input_data['posse_de_bola'] = st.slider(
            formatar_nome('posse_de_bola'), 
            int(stats.loc['min', 'posse_de_bola']), 
            int(stats.loc['max', 'posse_de_bola']), 
            int(stats.loc['50%', 'posse_de_bola'])
        )
        input_data['passes_certos'] = st.slider(
            formatar_nome('passes_certos'), 
            int(stats.loc['min', 'passes_certos']), 
            int(stats.loc['max', 'passes_certos']), 
            int(stats.loc['50%', 'passes_certos'])
        )

    # Sliders na Coluna 2
    with col2:
        input_data['disputa_aerea'] = st.slider(
            formatar_nome('disputa_aerea'), 
            int(stats.loc['min', 'disputa_aerea']), 
            int(stats.loc['max', 'disputa_aerea']), 
            int(stats.loc['50%', 'disputa_aerea'])
        )
        input_data['cartao_amarelo'] = st.slider(
            formatar_nome('cartao_amarelo'), 
            int(stats.loc['min', 'cartao_amarelo']), 
            int(stats.loc['max', 'cartao_amarelo']), 
            int(stats.loc['50%', 'cartao_amarelo'])
        )
        input_data['cartao_vermelho'] = st.slider(
            formatar_nome('cartao_vermelho'), 
            int(stats.loc['min', 'cartao_vermelho']), 
            int(stats.loc['max', 'cartao_vermelho']), 
            int(stats.loc['50%', 'cartao_vermelho'])
        )
    
    # Botão para executar a predição
    if st.button("Prever Colocação", type="primary"): # Texto do botão atualizado
        
        if model is None:
            st.error("O modelo não foi treinado. Verifique os dados.")
            return
            
        data_predict = pd.DataFrame([input_data])[features] 
        prediction = model.predict(data_predict)
        
        st.metric("Colocação Prevista", f"{prediction[0]:.0f}º") # Texto do KPI atualizado

    st.markdown("---")
    st.subheader("Importância das Métricas para a Previsão")
    st.markdown("O que o modelo mais valoriza para definir a colocação final (baseado nos dados de 2014-2020)?")
    # --- [FIM DA ALTERAÇÃO] ---
    
    if model is not None:
        importances = pd.DataFrame({
            'Métrica': [formatar_nome(f) for f in features],
            'Importância': model.feature_importances_
        }).set_index('Métrica')
        
        st.bar_chart(importances.sort_values(by='Importância', ascending=False))
    else:
        st.warning("O modelo de previsão não está disponível.")