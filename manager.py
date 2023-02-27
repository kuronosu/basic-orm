import sqlite3


class BaseManager:
    CREATE_TABLE_QUERY: str = '''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {PK_NAME} integer PRIMARY KEY AUTOINCREMENT NOT NULL, {FIELDS})'''
    INSERT_QUERY: str = 'INSERT INTO {TABLE_NAME} ({INSERT_PARAMS}) VALUES ({INSERT_VALUES})'
    UPDATE_QUERY: str = 'UPDATE {TABLE_NAME} SET {UPDATE_PARAMS} WHERE {PK_NAME} = ?'
    DELETE_QUERY: str = 'DELETE FROM {TABLE_NAME} WHERE {PK_NAME} = ?'
    LIST_QUERY: str = 'SELECT id, {FIELDS} FROM {TABLE_NAME} {WHERE} {ORDER} {LIMIT} {OFFSET}'
    GET_QUERY: str = 'SELECT id, {FIELDS} FROM {TABLE_NAME} WHERE {PK_NAME} = ?'

    def __init__(self, db_name: str, table_name: str, fields: dict[str, str], pk_name='id', create_table=False, verbose=False):
        if not fields:
            raise ValueError('Fields must be defined')
        self.db_name = db_name
        self.table_name = table_name
        self.pk_name = pk_name
        self.fields = fields
        self.connection: sqlite3.Connection = None  # type: ignore

        self._verbose = verbose

        if create_table:
            self.open()
            self.create_table()

    def __del__(self):
        self.close()

    def open(self):
        if self.connection:
            self.close()
        self.connection = sqlite3.connect(self.db_name)

    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_table(self):
        query = self.CREATE_TABLE_QUERY.format(
            TABLE_NAME=self.table_name,
            PK_NAME=self.pk_name,
            FIELDS=','.join([f'{key} {value}' for key, value in self.fields.items()]))
        if self._verbose:
            print(query)
        self.connection.execute(query)
        self.connection.commit()

    def insert(self, **kwargs) -> int | None:
        if len(kwargs) != len(self.fields):
            raise ValueError('Invalid number of arguments')
        filed_names = self.fields.keys()
        for key in kwargs:
            if key not in filed_names:
                raise ValueError('Invalid field name')

        query = self.INSERT_QUERY.format(
            TABLE_NAME=self.table_name,
            INSERT_PARAMS=','.join(kwargs.keys()),
            INSERT_VALUES=','.join(['?'] * len(kwargs)),
        )
        params = tuple(kwargs.values())
        if self._verbose:
            print(query, params)
        cur = self.connection.execute(query, params)
        self.connection.commit()
        return cur.lastrowid

    def update(self, pk, **kwargs):
        if len(kwargs) == 0:
            raise ValueError('No arguments to update')
        filed_names = self.fields.keys()
        for key in kwargs:
            if key not in filed_names:
                raise ValueError('Invalid field name')

        query = self.UPDATE_QUERY.format(
            TABLE_NAME=self.table_name,
            UPDATE_PARAMS=','.join([f'{key} = ?' for key in kwargs]),
            PK_NAME=self.pk_name)
        params = tuple(kwargs.values()) + (pk,)
        if self._verbose:
            print(query, params)
        self.connection.execute(query, params)
        self.connection.commit()

    def delete(self, pk):
        query = self.DELETE_QUERY.format(
            TABLE_NAME=self.table_name, PK_NAME=self.pk_name)
        params = (pk,)
        if self._verbose:
            print(query, params)
        cur = self.connection.execute(query, params)
        self.connection.commit()
        return cur.rowcount

    def list(self, where=None, order=None, limit=None, offset=None, **kwargs):
        fields = self.fields.keys()
        query = self.LIST_QUERY.format(
            TABLE_NAME=self.table_name,
            FIELDS=','.join(fields),
            WHERE='WHERE' if where else '',
            ORDER='ORDER BY' if order else '',
            LIMIT='LIMIT' if limit else '',
            OFFSET='OFFSET' if offset else '',
        )
        if self._verbose:
            print(query)
        return [[it[0], dict(zip(fields, it[1:]))] for it in self.connection.execute(query).fetchall()]

    def get(self, pk: int):
        fields = self.fields.keys()
        query = self.GET_QUERY.format(
            FIELDS=','.join(fields),
            TABLE_NAME=self.table_name,
            PK_NAME=self.pk_name)
        params = (pk,)
        if self._verbose:
            print(query, params)
        res = self.connection.execute(query, params).fetchone()
        if res is not None:
            return res[0], dict(zip(fields, res[1:]))
