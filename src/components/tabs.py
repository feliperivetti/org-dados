import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
# Importa as constantes e helpers do utils.py
from .utils import COLUNAS_METRICAS, formatar_nome

def render_tab_tendencias(df):
    """Cria e exibe o conteúdo da Aba 1"""
    st.header("Tendências Temporais (Evolução 2013-2020)")
    st.markdown("Como as médias do campeonato mudaram ao longo dos anos?")

    metricas_tendencia = st.multiselect(
        "Selecione as métricas para ver a tendência (média por ano):",
        options=COLUNAS_METRICAS,
        default=['gols', 'posse_de_bola', 'disputa_aerea'],
        format_func=formatar_nome
    )

    if metricas_tendencia:
        df_trends = df.groupby('Ano')[metricas_tendencia].mean().reset_index()
        cols = st.columns(len(metricas_tendencia))
        
        for i, metrica in enumerate(metricas_tendencia):
            with cols[i]:
                titulo_grafico = formatar_nome(metrica)
                st.subheader(f"Média de {titulo_grafico}")
                
                fig_trend = plt.figure(figsize=(10, 6))
                sns.lineplot(data=df_trends, x='Ano', y=metrica, marker='o', lw=3)
                plt.title(f'Evolução da Média de {titulo_grafico}', fontsize=16)
                plt.xlabel('Ano')
                plt.ylabel(f'Média de {titulo_grafico}')
                plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                st.pyplot(fig_trend)

def render_tab_correlacoes(df):
    """Cria e exibe o conteúdo da Aba 2"""
    st.header("Matriz de Correlação")
    st.markdown("Qual métrica tem maior impacto na **colocação final**?")

    colunas_numericas = df.select_dtypes(include='number').drop(columns='Ano', errors='ignore')
    
    # --- [ALTERADO] ---
    # Procura pela nova coluna 'colocacao_final'
    if 'colocacao_final' not in colunas_numericas.columns:
        st.error("Coluna 'colocacao_final' não encontrada. Não é possível gerar correlação.")
        st.error("Verifique se o nome da coluna no seu CSV está correto.")
        return
    # --- [FIM DA ALTERAÇÃO] ---

    corr_matrix = colunas_numericas.corr()
    
    fig_corr = plt.figure(figsize=(14, 10))
    sns.heatmap(
        corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', linewidths=0.5
    )
    plt.title('Matriz de Correlação entre Métricas (2013-2020)', fontsize=18)
    st.pyplot(fig_corr)
    
    st.markdown("""
    **Como ler este gráfico:**
    * **Correlação com `colocacao_final`:**
        * **Valor Negativo Forte (ex: -0.8):** EXCELENTE. (Mais métrica, melhor colocação)
        * **Valor Positivo Forte (ex: +0.6):** PÉSSIMO. (Mais métrica, pior colocação)
    """)

    st.markdown("---")
    # --- [ALTERADO] ---
    st.header("Análise de Dispersão (Métrica vs. Colocação Final)")
    st.markdown("Veja visualmente a relação entre uma métrica e a posição final.")

    metrica_x = st.selectbox(
        "Selecione a métrica (Eixo X) para comparar com a Colocação Final (Eixo Y):",
        options=COLUNAS_METRICAS,
        index=0, 
        format_func=formatar_nome,
        key='selectbox_dispersao'
    )

    if metrica_x:
        titulo_x = formatar_nome(metrica_x)
        fig_scatter = plt.figure(figsize=(10, 6))
        ax = fig_scatter.add_subplot(111)
        sns.regplot(
            data=df, x=metrica_x, y='colocacao_final', ax=ax, # Usa 'colocacao_final'
            line_kws={'color': 'red', 'linestyle': '--', 'lw': 2}, 
            scatter_kws={'alpha': 0.3} 
        )
        ax.invert_yaxis() 
        ax.set_title(f'Relação entre {titulo_x} e Colocação Final', fontsize=16)
        ax.set_xlabel(titulo_x)
        ax.set_ylabel("Colocação Final (1 = Campeão)") # Label atualizado
        st.pyplot(fig_scatter)
    # --- [FIM DA ALTERAÇÃO] ---


def render_tab_analise_time(df, df_medias_ano, anos_completos):
    """Cria e exibe o conteúdo da Aba 3"""
    st.header("Análise Individual por Time")
    st.markdown("Selecione um time para ver sua performance ao longo dos anos (2013-2020).")

    lista_times = sorted(df['equipe'].unique())
    time_selecionado = st.selectbox(
        "Selecione um time:",
        options=lista_times,
        index=lista_times.index("Flamengo") if "Flamengo" in lista_times else 0
    )

    if not time_selecionado:
        st.warning("Por favor, selecione um time.")
        return

    df_time_original = df[df['equipe'] == time_selecionado].copy()
    
    if df_time_original.empty:
        st.warning(f"Não há dados para o time '{time_selecionado}' no período.")
        return

    st.subheader(f"Desempenho: {time_selecionado}")
    
    # --- [ALTERADO] ---
    # KPIs usam a nova coluna 'colocacao_final'
    media_colocacao = df_time_original['colocacao_final'].mean()
    melhor_colocacao = df_time_original['colocacao_final'].min()
    
    col1_kpi, col2_kpi = st.columns(2)
    col1_kpi.metric("Melhor Colocação (no período)", f"{int(melhor_colocacao)}º")
    col2_kpi.metric("Média de Colocação (quando jogou)", f"{media_colocacao:.1f}º")
    
    st.markdown("---")

    # Gráfico 1: Evolução da Colocação
    # (LÓGICA DOS "BURACOS" JÁ ESTÁ AQUI - `reindex`)
    df_time_reindexado = df_time_original.set_index('Ano').reindex(anos_completos).reset_index()
    df_time_reindexado['equipe'] = time_selecionado 

    st.subheader("Evolução da Colocação Ano a Ano")
    
    fig_rank_time = plt.figure(figsize=(10, 5))
    ax_rank = fig_rank_time.add_subplot(111)
    
    # Usa 'colocacao_final' no eixo Y
    sns.lineplot(data=df_time_reindexado, x='Ano', y='colocacao_final', marker='o', lw=3, ax=ax_rank)
    
    ax_rank.set_title(f"Colocação Final de {time_selecionado} por Ano")
    ax_rank.set_ylabel("Colocação Final (1 = Campeão)") # Label atualizado
    ax_rank.set_xlabel("Ano")
    # --- [FIM DA ALTERAÇÃO] ---
    
    # Lógica de eixos (mantida)
    ax_rank.set_xlim(left=anos_completos.start - 0.5, right=anos_completos.stop - 1 + 0.5) 
    ax_rank.set_ylim(bottom=20.5, top=0.5) 
    ax_rank.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) 
    ax_rank.yaxis.set_major_locator(ticker.MultipleLocator(2)) 
    st.pyplot(fig_rank_time)
    
    st.markdown("---")

    # Gráfico 2: Comparação com a Média da Liga (sem alteração de lógica, só de texto)
    st.subheader("Comparação com a Média do Campeonato")
    
    metrica_comp = st.selectbox(
        "Selecione a métrica para comparar:",
        options=COLUNAS_METRICAS,
        format_func=formatar_nome,
        key='selectbox_time'
    )
    
    if metrica_comp:
        df_time_metrica = df_time_original.set_index('Ano')[metrica_comp]
        df_media_metrica = df_medias_ano[metrica_comp]
        
        df_comparacao = pd.DataFrame({
            f'{time_selecionado}': df_time_metrica,
            'Média da Liga': df_media_metrica
        })
        df_comparacao_reindexada = df_comparacao.reindex(anos_completos)

        st.line_chart(df_comparacao_reindexada, width='stretch')
        
        st.markdown(f"""
        **Análise ({formatar_nome(metrica_comp)}):**
        Buracos na linha do time indicam anos em que ele não estava na Série A.
        """)