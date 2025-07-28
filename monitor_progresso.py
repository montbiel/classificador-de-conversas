#!/usr/bin/env python3
"""
Script para verificar progresso das classificações
"""

import asyncio
from database import DatabaseManager

async def check_progress():
    db = DatabaseManager()
    
    # Total de clientes no CSV
    customers = await db.get_customers_from_csv()
    total_customers = len(customers)
    
    # Total de classificações
    conn = await db.get_connection()
    total_classifications = await conn.fetchval("SELECT COUNT(*) FROM classificacoes")
    await conn.close()
    
    # Progresso
    progress = (total_classifications / total_customers) * 100 if total_customers > 0 else 0
    
    print(f"📊 PROGRESSO DO CLASSIFICADOR")
    print(f"Total de clientes: {total_customers}")
    print(f"Classificações realizadas: {total_classifications}")
    print(f"Progresso: {progress:.1f}%")
    
    if progress < 100:
        remaining = total_customers - total_classifications
        print(f"Restam: {remaining} clientes para classificar")
    else:
        print("✅ Todos os clientes foram classificados!")
    
    # Mostrar últimas classificações
    if total_classifications > 0:
        conn = await db.get_connection()
        ultimas = await conn.fetch("""
            SELECT user_id, classificacao, data_classificacao
            FROM classificacoes
            ORDER BY data_classificacao DESC
            LIMIT 5
        """)
        await conn.close()
        
        print(f"\n📋 Últimas 5 classificações:")
        for row in ultimas:
            print(f"  Usuário {row[0]}: {row[1]} - {row[2]}")

if __name__ == "__main__":
    asyncio.run(check_progress()) 