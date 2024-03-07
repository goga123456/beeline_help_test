import asyncpg
import os

class Database:
    def __init__(self):
        self.db_url = os.environ['DATABASE_URL']

    async def connect(self):
        return await asyncpg.connect(dsn=self.db_url)
    

    async def zayavka(self, response_date, surname, name, number, birthday, address, education, rus, uzb, eng, exp):
        conn = await self.connect()
        try:
            await conn.execute(
                'INSERT INTO zayavki (response_date, surname, name, number, birthday, address, education, rus, uzb, eng, exp) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);',
                response_date, surname, name, number, birthday, address, education, rus, uzb, eng, exp)
        finally:
            await conn.close()

    async def less18(self, response_date, surname, name, number, birthday):
        conn = await self.connect()
        try:
            await conn.execute(
                'INSERT INTO less18 (response_date, surname, name, number, birthday) VALUES ($1, $2, $3, $4, $5);',
                response_date, surname, name, number, birthday)
        finally:
            await conn.close()
    
    async def reject(self, response_date, cause):
        conn = await self.connect()
        try:
            await conn.execute(
                'INSERT INTO rejects (response_date, cause) VALUES ($1, $2);',
                response_date, cause)
        finally:
            await conn.close()
