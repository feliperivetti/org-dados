import streamlit as st
import pandas as pd
import glob
import os
# Importa as constantes do arquivo utils.py
from .utils import COLUNAS_METRICAS

@st.cache_data
def carregar_e_preparar_dados(pasta_dados):
    """
    Carrega, limpa, converte tipos e prepara os dados de 2013 a 2020.
    """
    try:
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        src_dir = os.path.dirname(script_dir)
        project_root = os.path.dirname(src_dir)
        caminho_pasta_dados = os.path.join(project_root, pasta_dados)
        
    except NameError:
        st.info("Executando em modo 'bare'. Procurando 'data' no diretório atual.")
        caminho_pasta_dados = pasta_dados
        
    padrao_arquivos = os.path.join(caminho_pasta_dados, 'team_statistics_brasileirao_*.csv')
    lista_de_arquivos = sorted(glob.glob(padrao_arquivos))
    
    if not lista_de_arquivos:
        st.error(f"Erro: Nenhum arquivo CSV encontrado no padrão '{padrao_arquivos}'.")
        st.error(f"Verifique se sua pasta '{pasta_dados}' está na raiz do projeto, ao lado da pasta 'src'.")
        return None

    # Carrega todos os arquivos
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
    
    # --- [INÍCIO DA CORREÇÃO] ---

    # 1. Verifica se a coluna 'ranking' ainda existe e a renomeia
    if 'ranking' in df_completo.columns and 'colocacao_final' not in df_completo.columns:
        st.info("Detectamos a coluna 'ranking'. Renomeando para 'colocacao_final'.")
        df_completo.rename(columns={'ranking': 'colocacao_final'}, inplace=True)

    # 2. Garante que as colunas de MÉTRICAS (features) sejam numéricas
    for col in COLUNAS_METRICAS:
        if col in df_completo.columns:
            df_completo[col] = pd.to_numeric(df_completo[col], errors='coerce')
        else:
            st.warning(f"Atenção: A coluna de feature '{col}' não foi encontrada.")
    
    # 3. Garante que a coluna ALVO (colocacao_final) seja numérica
    if 'colocacao_final' in df_completo.columns:
        df_completo['colocacao_final'] = pd.to_numeric(df_completo['colocacao_final'], errors='coerce')
    else:
        # Se mesmo após a tentativa de renomear, ela não existir, o erro é fatal
        st.error("ERRO CRÍTICO: A coluna 'colocacao_final' (ou 'ranking') não foi encontrada nos seus dados.")
        st.error("Por favor, verifique os nomes das colunas nos seus arquivos CSV.")
        return None # Para a execução
        
    # --- [FIM DA CORREÇÃO] ---

    # Limpa a coluna 'equipe'
    if 'equipe' in df_completo.columns:
        df_completo['equipe'] = df_completo['equipe'].astype(str).str.replace(
            r'^\d+\.\s*', '', regex=True
        ).str.strip()
    
    # Remove linhas onde métricas OU o alvo são nulos
    colunas_para_dropna = COLUNAS_METRICAS + ['colocacao_final']
    # .dropna() remove linhas onde 'colocacao_final' ou métricas ficaram nulas após coerção
    df_completo.dropna(subset=colunas_para_dropna, inplace=True)
    
    return df_completo