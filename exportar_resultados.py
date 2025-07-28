#!/usr/bin/env python3
"""
Script para exportar resultados das classificações para CSV
"""

import asyncio
import pandas as pd
from database import DatabaseManager

async def export_results():
    db = DatabaseManager()
    conn = await db.get_connection()
    
    # Buscar todas as classificações
    results = await conn.fetch("""
        SELECT user_id, classificacao, confianca, contexto, 
               data_classificacao, tokens_utilizados, tempo_processamento_ms
        FROM classificacoes
        ORDER BY data_classificacao DESC
    """)
    
    # Converter para DataFrame
    df = pd.DataFrame(results, columns=[
        'user_id', 'classificacao', 'confianca', 'contexto',
        'data_classificacao', 'tokens_utilizados', 'tempo_processamento_ms'
    ])
    
    # Salvar em CSV
    df.to_csv('classificacoes_completas.csv', index=False)
    print(f"✅ Exportadas {len(df)} classificações para classificacoes_completas.csv")
    
    # Mostrar resumo
    if len(df) > 0:
        print("\n📊 Resumo das classificações:")
        print(f"  Total de classificações: {len(df)}")
        print(f"  Classificações com sucesso: {len(df[df['classificacao'] != 'Erro na classificação'])}")
        print(f"  Classificações com erro: {len(df[df['classificacao'] == 'Erro na classificação'])}")
        
        # Distribuição das classificações
        print("\n📋 Distribuição das classificações:")
        dist = df['classificacao'].value_counts()
        for classificacao, count in dist.items():
            print(f"  {classificacao}: {count}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(export_results()) 