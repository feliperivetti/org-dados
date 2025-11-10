import streamlit as st
import pandas as pd
import glob
import os
# Importa as constantes do arquivo utils.py (que está no mesmo diretório)
from .utils import COLUNAS_METRICAS

@st.cache_data
def carregar_e_preparar_dados(pasta_dados):
    """
    Carrega, limpa, converte tipos e prepara os dados de 2014 a 2020.
    """
    try:
        # Pega o caminho do script (ex: /.../src/components/data_loader.py)
        script_path = os.path.abspath(__file__)
        # Pega o diretório do script (ex: /.../src/components)
        script_dir = os.path.dirname(script_path)
        # Sobe um nível para o diretório 'src' (ex: /.../src)
        src_dir = os.path.dirname(script_dir)
        # Sobe mais um nível para a raiz do projeto (ex: /...)
        project_root = os.path.dirname(src_dir)
        # Constrói o caminho para a pasta 'data' (ex: /.../data)
        caminho_pasta_dados = os.path.join(project_root, pasta_dados)
        
    except NameError:
        # Fallback para ambientes onde __file__ não está definido
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
    
    # Garante que todas as colunas de métricas sejam numéricas
    for col in COLUNAS_METRICAS:
        if col in df_completo.columns:
            df_completo[col] = pd.to_numeric(df_completo[col], errors='coerce')
        else:
            st.warning(f"Atenção: A coluna esperada '{col}' não foi encontrada.")
    
    # Limpa a coluna 'equipe'
    if 'equipe' in df_completo.columns:
        df_completo['equipe'] = df_completo['equipe'].astype(str).str.replace(
            r'^\d+\.\s*', '', regex=True
        ).str.strip()
    
    # Remove linhas onde métricas essenciais são nulas
    df_completo.dropna(subset=COLUNAS_METRICAS, inplace=True)
    
    return df_completo