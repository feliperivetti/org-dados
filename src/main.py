import streamlit as st
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker 

# --- Configurações da Página e Estilo ---
st.set_page_config(layout="wide", page_title="Análise Brasileirão")
sns.set_theme(style="whitegrid", palette="muted")

# --- Carregamento de Dados (com Cache) ---

@st.cache_data
def carregar_e_preparar_dados():
    """
    Carrega os dados da pasta 'data' que está no diretório raiz,
    um nível acima da pasta 'src' onde este script está.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        pasta_dados = os.path.join(project_root, 'data')
    except NameError:
        st.info("Executando em modo 'bare'. Procurando 'data' no diretório atual.")
        pasta_dados = 'data'
        
    padrao_arquivos = os.path.join(pasta_dados, 'team_statistics_brasileirao_*.csv')
    lista_de_arquivos = sorted(glob.glob(padrao_arquivos))
    
    if not lista_de_arquivos:
        st.error(f"Erro: Nenhum arquivo CSV encontrado no padrão '{padrao_arquivos}'.")
        st.error(f"Verifique se sua pasta 'data' está na raiz do projeto, ao lado da pasta 'src'.")
        return None

    lista_dataframes = []
    for arquivo_csv in lista_de_arquivos:
        try:
            df_ano = pd.read_csv(arquivo_csv)
            nome_base = os.path.basename(arquivo_csv)
            ano_str = nome_base.split('_')[-1].replace('.csv', '')
            df_ano['Ano'] = int(ano_str)
            lista_dataframes.append(df_ano)
        except Exception as e:
            st.warning(f"Erro ao ler o arquivo {arquivo_csv}: {e}")
            
    if not lista_dataframes:
        st.error("Nenhum dado foi carregado com sucesso.")
        return None
        
    df_completo = pd.concat(lista_dataframes, ignore_index=True)
    return df_completo

# --- Função para "embelezar" nomes de colunas ---
def formatar_nome(nome_coluna):
    """Transforma 'posse_de_bola' em 'Posse de Bola'"""
    if pd.isna(nome_coluna):
        return ""
    return nome_coluna.replace('_', ' ').title()

# --- Início da Interface Principal ---

st.title("📊 Análise de Dados do Brasileirão (2014-2020)")
st.markdown("Use as abas abaixo para explorar diferentes visões dos dados.")

df = carregar_e_preparar_dados()

if df is None:
    st.stop()

# --- Sidebar (Menu Lateral) ---
st.sidebar.header("Opções de Visualização")
if st.sidebar.checkbox("Mostrar dados brutos (DataFrame)"):
    st.sidebar.subheader("Dados Completos (2014-2020)")
    st.sidebar.dataframe(df)

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Dados Carregados:**
* **{len(df)}** registros (linhas)
* **{len(df['equipe'].unique())}** equipes únicas
* **{df['Ano'].min()} a {df['Ano'].max()}** (período)
""")

# --- Lista de Colunas e Dados Globais ---
colunas_metricas = [
    'gols', 'cartao_amarelo', 'cartao_vermelho', 
    'posse_de_bola', 'passes_certos', 'disputa_aerea'
]
# Calcula as médias da liga UMA VEZ para usar depois
df_medias_ano = df.groupby('Ano')[colunas_metricas].mean()
# Define o range completo de anos dos dados
anos_completos = range(df['Ano'].min(), df['Ano'].max() + 1)


# --- Criação das Abas ---
tab1, tab2, tab3 = st.tabs([
    "📈 Análise de Tendências", 
    "🔗 Correlações (O que leva ao Sucesso?)", 
    "⚽ Análise por Time"
])


# --- Conteúdo da Aba 1: Tendências ---
with tab1:
    st.header("Tendências Temporais (Evolução 2014-2020)")
    st.markdown("Como as médias do campeonato mudaram ao longo dos anos?")

    metricas_tendencia = st.multiselect(
        "Selecione as métricas para ver a tendência (média por ano):",
        options=colunas_metricas,
        default=['gols', 'posse_de_bola', 'cartao_amarelo'],
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

# --- Conteúdo da Aba 2: Correlações ---
with tab2:
    st.header("Matriz de Correlação")
    st.markdown("Qual métrica tem maior impacto no **ranking** final? (Quanto mais perto de 1.0 ou -1.0, mais forte a relação)")

    colunas_numericas = df.select_dtypes(include='number').drop(columns='Ano', errors='ignore')
    corr_matrix = colunas_numericas.corr()
    
    fig_corr = plt.figure(figsize=(14, 10))
    sns.heatmap(
        corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', linewidths=0.5
    )
    plt.title('Matriz de Correlação entre Métricas (2014-2020)', fontsize=18)
    st.pyplot(fig_corr)
    
    st.markdown("""
    **Como ler este gráfico:**
    * **Correlação com `ranking`:**
        * **Valor Negativo Forte (ex: -0.8):** EXCELENTE. Quanto **MAIS** da métrica, **MENOR** o `ranking` (melhor a posição).
        * **Valor Positivo Forte (ex: +0.6):** PÉSSIMO. Quanto **MAIS** da métrica, **MAIOR** o `ranking` (pior a posição).
    """)

    st.markdown("---")
    st.header("Análise de Dispersão (Métrica vs. Ranking)")
    st.markdown("Veja visualmente a relação entre uma métrica e a posição final no campeonato.")

    metrica_x = st.selectbox(
        "Selecione a métrica (Eixo X) para comparar com o Ranking (Eixo Y):",
        options=colunas_metricas,
        index=0, 
        format_func=formatar_nome,
        key='selectbox_dispersao' # Chave única
    )

    if metrica_x:
        titulo_x = formatar_nome(metrica_x)
        fig_scatter = plt.figure(figsize=(10, 6))
        ax = fig_scatter.add_subplot(111)
        sns.regplot(
            data=df, x=metrica_x, y='ranking', ax=ax,
            line_kws={'color': 'red', 'linestyle': '--', 'lw': 2}, 
            scatter_kws={'alpha': 0.3} 
        )
        ax.invert_yaxis() # Inverte o eixo Y (Ranking 1 no topo)
        ax.set_title(f'Relação entre {titulo_x} e Ranking Final', fontsize=16)
        ax.set_xlabel(titulo_x)
        ax.set_ylabel("Ranking Final (1 = Campeão)")
        st.pyplot(fig_scatter)


# --- [INÍCIO DA LÓGICA CORRIGIDA] ---
# --- Conteúdo da Aba 3: Análise por Time ---
with tab3:
    st.header("Análise Individual por Time")
    st.markdown("Selecione um time para ver sua performance ao longo dos anos (2014-2020).")

    lista_times = sorted(df['equipe'].unique())
    time_selecionado = st.selectbox(
        "Selecione um time:",
        options=lista_times,
        index=lista_times.index("Flamengo") if "Flamengo" in lista_times else 0
    )

    if time_selecionado:
        # Filtra o DataFrame original para o time selecionado
        df_time_original = df[df['equipe'] == time_selecionado].copy()
        
        if df_time_original.empty:
            st.warning(f"Não há dados para o time '{time_selecionado}' no período.")
        else:
            st.subheader(f"Desempenho: {time_selecionado}")
            
            # KPIs (calculados apenas sobre os anos em que o time jogou)
            media_ranking = df_time_original['ranking'].mean()
            melhor_ranking = df_time_original['ranking'].min()
            
            col1_kpi, col2_kpi = st.columns(2)
            col1_kpi.metric("Melhor Posição (no período)", f"{int(melhor_ranking)}º")
            col2_kpi.metric("Média de Posição (quando jogou)", f"{media_ranking:.1f}º")
            
            st.markdown("---")

            # --- CORREÇÃO 1: Gráfico de Ranking ---
            
            # Prepara os dados do time com o index completo (anos faltantes terão NaN)
            df_time_reindexado = df_time_original.set_index('Ano').reindex(anos_completos).reset_index()
            # O reindex pode bagunçar o nome da equipe, vamos garantir
            df_time_reindexado['equipe'] = time_selecionado 

            st.subheader("Evolução do Ranking Ano a Ano")
            
            fig_rank_time = plt.figure(figsize=(10, 5))
            ax_rank = fig_rank_time.add_subplot(111)
            
            # Plota usando o DataFrame re-indexado.
            # O lineplot naturalmente criará "buracos" onde os dados são NaN
            sns.lineplot(data=df_time_reindexado, x='Ano', y='ranking', marker='o', lw=3, ax=ax_rank)
            
            ax_rank.set_title(f"Posição Final de {time_selecionado} por Ano")
            ax_rank.set_ylabel("Ranking (1 = Campeão)")
            ax_rank.set_xlabel("Ano")
            
            # Define o eixo X para mostrar o período COMPLETO
            ax_rank.set_xlim(left=anos_completos.start - 0.5, right=anos_completos.stop - 1 + 0.5) 
            ax_rank.set_ylim(bottom=20.5, top=0.5) 
            ax_rank.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) # Anos inteiros
            ax_rank.yaxis.set_major_locator(ticker.MultipleLocator(2)) # Marcas de 2 em 2
            st.pyplot(fig_rank_time)
            
            st.markdown("---")

            # --- CORREÇÃO 2: Gráfico de Comparação ---
            st.subheader("Comparação com a Média do Campeonato")
            
            metrica_comp = st.selectbox(
                "Selecione a métrica para comparar:",
                options=colunas_metricas,
                format_func=formatar_nome,
                key='selectbox_time' # Chave única
            )
            
            if metrica_comp:
                # Pega os dados do time, já com index de 'Ano'
                df_time_metrica = df_time_original.set_index('Ano')[metrica_comp]
                
                # Pega as médias da liga (já calculada para todos os anos)
                df_media_metrica = df_medias_ano[metrica_comp]
                
                # Cria o DataFrame de comparação
                df_comparacao = pd.DataFrame({
                    f'{time_selecionado}': df_time_metrica,
                    'Média da Liga': df_media_metrica
                })

                # Re-indexa o DataFrame final para o período completo
                # A Média da Liga ficará completa, e o time terá buracos (NaN)
                df_comparacao_reindexada = df_comparacao.reindex(anos_completos)

                # O st.line_chart plota o DataFrame 'df_comparacao_reindexada' inteiro
                # Ele também criará "buracos" para os valores NaN
                st.line_chart(df_comparacao_reindexada, use_container_width=True)
                
                st.markdown(f"""
                **Análise ({formatar_nome(metrica_comp)}):**
                O gráfico acima mostra se o **{time_selecionado}** esteve acima 
                ou abaixo da média de todos os times do campeonato em cada ano. 
                **Buracos na linha do time** indicam anos em que ele não estava na Série A.
                """)
