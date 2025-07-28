#!/usr/bin/env python3
"""
Verificar classificações no banco de dados
"""

import asyncio
from database import DatabaseManager

async def verificar_classificacoes():
    db = DatabaseManager()
    conn = await db.get_connection()
    
    # Verificar total de classificações
    total = await conn.fetchval('SELECT COUNT(*) FROM classificacoes')
    print(f'📊 Total de classificações no banco: {total}')
    
    if total > 0:
        # Verificar últimas classificações
        ultimas = await conn.fetch("""
            SELECT user_id, classificacao, confianca, data_classificacao
            FROM classificacoes
            ORDER BY data_classificacao DESC
            LIMIT 5
        """)
        
        print("\n📋 Últimas classificações:")
        for row in ultimas:
            print(f"  Usuário {row[0]}: {row[1]} (confiança: {row[2]}) - {row[3]}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verificar_classificacoes()) 