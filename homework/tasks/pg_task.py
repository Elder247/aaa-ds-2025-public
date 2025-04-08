from dataclasses import dataclass

import asyncpg


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:
        """
        Создайте таблицу items со следующими колонками:
         item_id (int) - обязательное поле, значения должны быть уникальными
         user_id (int) - обязательное поле
         title (str) - обязательное поле
         description (str) - обязательное поле
        """
        # In production environment we will use migration tool
        # like https://github.com/pressly/goose
        await self._pool.execute('''
            CREATE TABLE items(
                item_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            );
        ''')

    async def save_items(self, items: list[ItemEntry]) -> None:
        """
        Напишите код для вставки записей в таблицу items одним запросом, цикл
        использовать нельзя.
        """
        # Don't use str-formatting, query args should be escaped to avoid
        # sql injections https://habr.com/ru/articles/148151/.
        command = '''
            INSERT INTO items (item_id, user_id, title, description)
            VALUES ($1, $2, $3, $4)
        '''
        values = [ 
            (item.item_id, item.user_id, item.title, item.description)
            for item in items
        ]
        await self._pool.executemany(command=command, args=values)

    async def find_similar_items(
        self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:
        """
        Напишите код для поиска записей, имеющих указанные user_id, title и description.
        """
        query = '''
            SELECT item_id, user_id, title, description
            FROM items
            WHERE TRUE
                AND user_id = $1
                AND title = $2
                AND description = $3
        '''
        found_items = await self._pool.fetch(query, user_id, title, description)
        return [ItemEntry(**item) for item in found_items]
