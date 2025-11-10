import pandas as pd

# Constantes globais
COLUNAS_METRICAS = [
    'gols', 'cartao_amarelo', 'cartao_vermelho', 
    'posse_de_bola', 'passes_certos', 'disputa_aerea'
]
PASTA_DADOS = 'data'

def formatar_nome(nome_coluna):
    """Transforma 'posse_de_bola' em 'Posse de Bola'"""
    if pd.isna(nome_coluna):
        return ""
    return nome_coluna.replace('_', ' ').title()