import logging


class DB:
    import sqlite3 as __sqlite__
    from os import path as __os_path__
    from os import listdir as __list_dir__

    def __init__(self, database=":memory:") -> None:
        self.uri_db = database
        self.db = self.__sqlite__.connect(database)
        self.cursor = self.db.cursor()
        with open(self.__os_path__.join('.', 'sql', 'create_tables.sql'), 'r') as update:
            sql = update.read()
            self.cursor.executescript(sql)
        self.db.commit()

    def select(self, table: str, fields=['*'], where={1: 1}, many=-1):
        fields = ', '.join(fields)
        wheres = self.__convert_where__(where)
        sql = "SELECT {fields} FROM {table} WHERE {where}"
        sql = sql.format(table=table, fields=', '.join(
            fields), where=wheres)
        logging.debug("%s", sql)
        data = self.cursor.execute(sql)
        self.db.commit()
        lista = data.fetchall()
        if len(lista) < 0:
            return None
        elif len(lista) == 1 or many == 1:
            return lista[0]
        elif many == -1:
            return lista
        return lista[:many]

    def update(self, table: str, camps: dict, where: dict = {1: 1}):
        values = self.__convert_set__(camps)
        wheres = self.__convert_where__(where)
        sql = "UPDATE '{}' SET {} WHERE {}"
        sql = sql.format(table, values, wheres)
        logging.debug("%s", sql)
        row_id = self.cursor.execute(sql).lastrowid
        self.db.commit()
        return row_id

    def insert(self, table: str, file: dict):
        values = self.__convert_insert__(file)
        sql = "INSERT INTO '{}' ({}) VALUES ({})"
        sql = sql.format(table, ', '.join(file), values)
        logging.debug("%s", sql)
        row_id = self.cursor.execute(sql).lastrowid
        self.db.commit()
        return row_id

    def __convert_where__(self, where: dict, cat='AND'):
        """Convert JSON to WHERE structure"""
        wheres = []
        for i in where:
            k = where[i]
            if isinstance(k, str):
                k = f"\"{k}\""
            wheres.append(f"{i}={k}")
        return f" {cat} ".replace('  ', ' ').join(wheres)

    def __convert_set__(self, camps: dict):
        """Convert JSON to SET structure"""
        values = []
        for i in camps:
            k = camps[i]
            if isinstance(k, str):
                k = f"\"{k}\""
            values.append(f"{i}={k}")
        return ', '.join(values)

    def __convert_insert__(self, camps):
        values = []
        for i in camps:
            k = camps[i]
            if isinstance(k, str):
                k = f"\"{k}\""
            camps.append(str(k))
        return ', '.join(values)
