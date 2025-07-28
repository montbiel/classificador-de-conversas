#!/usr/bin/env python3
"""
Teste de dados de usuário específico
"""

import asyncio
from database import DatabaseManager

async def test_user_data():
    db = DatabaseManager()
    conn = await db.get_connection()
    
    # Testar usuário 56
    result = await conn.fetch('SELECT COUNT(*) FROM chat_history WHERE customer_id = 56')
    print(f'Mensagens para usuário 56: {result[0][0]}')
    
    # Verificar estrutura da tabela
    columns = await conn.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'chat_history' 
        ORDER BY ordinal_position
    """)
    
    print("\nEstrutura da tabela chat_history:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(test_user_data()) 