from datetime import datetime
import asyncpg
import os
from aiogram import Bot
from openpyxl.workbook import Workbook

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


    async def fetch_data(self, table_name):
        conn = await self.connect()
        query = f"SELECT * FROM {table_name};"
        return await conn.fetch(query)

   async def create_excel(self):
    workbook = Workbook()

    # Заголовки для каждой таблицы
    headers = {
        "zayavki": ["Header1", "Header2", "Header3"],  # Замените заголовки на реальные
        "less18": ["Header4", "Header5", "Header6"],
        "rejects": ["Дата отклика", "Причина отказа"]
    }

    for table_name, header_row in headers.items():
        sheet = workbook.create_sheet(title=table_name)
        sheet.append(header_row)
        data = await self.fetch_data(table_name)
        for row in data:
            # Преобразуйте asyncpg.Record в список значений
            row_values = list(row.values())
            sheet.append(row_values)

    file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    workbook.save(file_name)
    return file_name
