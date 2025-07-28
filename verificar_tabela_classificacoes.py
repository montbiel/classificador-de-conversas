#!/usr/bin/env python3
"""
Verificar estrutura da tabela classificacoes
"""

import asyncio
from database import DatabaseManager

async def verificar_estrutura():
    db = DatabaseManager()
    conn = await db.get_connection()
    
    # Verificar estrutura da tabela
    result = await conn.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'classificacoes' 
        ORDER BY ordinal_position
    """)
    
    print("Estrutura da tabela classificacoes:")
    for row in result:
        print(f"  {row[0]}: {row[1]}")
    
    # Verificar dados atuais
    dados = await conn.fetch("""
        SELECT user_id, classificacao, contexto
        FROM classificacoes
        ORDER BY data_classificacao DESC
        LIMIT 3
    """)
    
    print("\nDados atuais na tabela:")
    for row in dados:
        print(f"  Usuário {row[0]}: '{row[1]}' - {row[2][:50]}...")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verificar_estrutura()) 