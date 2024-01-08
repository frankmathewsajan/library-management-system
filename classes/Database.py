import sqlite3

database_structure = {
    "users": {
        "username": "TEXT UNIQUE",
        "password": "BLOB",
        "auth": "BOOLEAN",
        'checked_out': 'INT DEFAULT 0',
        'purchased': 'INT DEFAULT 0',
        'balance': 'INT DEFAULT 0',
    },
    "searches": {"username": "TEXT", "search": "TEXT UNIQUE"},
    "books": {"uid": "TEXT", "type": "TEXT", "username": "TEXT"},
    "config": {"id": "TEXT UNIQUE",'value':'TEXT'},
    "library": {
        "title": "TEXT",
        "image_data": "BLOB",
        "author": "TEXT",
        "publisher": "TEXT",
        "description": "TEXT",
        "imageLinks": "TEXT",
        "price": "NUMERIC",
        "uid": "TEXT",
        "pgno": "INTEGER",
        "type": "TEXT",
        "saleability": "BOOLEAN",
        "search": "TEXT",
    },
}


class Database:
    def drop() -> None:
        import os
        file_path = './databases/sqlite.db'
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'{file_path} has been deleted.')
        else:
            print(f'No such file: {file_path}')      


    def init() -> None:

        conn, cursor = Database.connect()
        create_table_queries = []
        for table_name, columns in database_structure.items():
            columns_query = ", ".join(
                [f"{column} {data_type}" for column, data_type in columns.items()]
            )
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_query});"
            create_table_queries.append(create_query)
        for query in create_table_queries:
            cursor.execute(query)

        Database.save(conn, cursor)
        Database.insert('config',{
            'id':'resume',
            'value':False
        })
        print("Database created successfully!")

    def connect() -> tuple:
        """
        Create connection to database
        returns connection & cursor
        """
        sqliteConnection = sqlite3.connect("./databases/sqlite.db")
        cursor = sqliteConnection.cursor()
        return (sqliteConnection, cursor)

    def save(sqliteConnection: sqlite3.Connection, cursor: sqlite3.Cursor) -> bool:
        """
        Commit & Close Connection
        """
        cursor.close()
        sqliteConnection.commit()

    def join_and_get(columns:list, table_a: str, table_b: str, on: str, conditions: list) -> list:
        """
        Connects table1 and table2 on the specified condition and 
        returns results based on additional conditions.
        Write condition on a. or b.
        """

        query = f"""
            SELECT {', '.join(columns)}
            FROM {table_a} a
            INNER JOIN {table_b} b ON {on}
            WHERE {' AND '.join(conditions)}
        """

        try:
            _, cursor = Database.connect()
            cursor.execute(query)
            return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")
            return []


    def insert(table: str, data: dict) -> bool:
        """Inserts a key-value pair into a table.

        Args:
            table: The name of the table to insert into.
            data: A dictionary containing the key-value pairs to insert.

        Returns:
            True if the insertion was successful, False otherwise.
        """

        try:
            conn, cursor = Database.connect()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            Database.save(conn, cursor)
            return True

        except sqlite3.Error as e:
            print(f"Error inserting data into table '{table}': {e}")
            return False

    def get(columns: list, table: str, condition: str = "") -> list:
        """Selects data in given columns from a table where the condition matches."""

        try:
            _, cursor = Database.connect()
            query = f"SELECT {', '.join(columns)} FROM {table}" + (
                f" WHERE {condition}" if condition else ""
            )
            cursor.execute(query)
            return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")
            return []

    def update(table: str, data: dict, condition: str = "") -> bool:
        """Updates values in a table where the condition matches."""

        try:
            conn, cursor = Database.connect()
            set_clause = ", ".join([f"{column} = ?" for column in data.keys()])
            query = f"UPDATE {table} SET {set_clause}"
            if condition:
                query += f" WHERE {condition}"
            cursor.execute(query, list(data.values()))
            Database.save(conn, cursor)
            return True

        except sqlite3.Error as e:
            print(f"Error updating data in table '{table}': {e}")
            return False

    def count(table: str, condition: str = "") -> int:
        """Counts the number of rows in a table where the condition matches."""

        try:
            conn, cursor = Database.connect()
            query = f"SELECT COUNT(*) FROM {table}" + (
                f" WHERE {condition}" if condition else ""
            )
            cursor.execute(query)
            count = cursor.fetchone()[0]
            Database.save(conn, cursor)
            return count

        except sqlite3.Error as e:
            print(f"Error counting rows in table '{table}': {e}")
            return 0

    def delete(table: str, condition: str = "") -> bool:
        """Deletes rows from a table where the condition matches."""

        try:
            conn, cursor = Database.connect()
            query = f"DELETE FROM {table}" + (
                f" WHERE {condition}" if condition else ""
            )
            cursor.execute(query)
            conn.commit()
            return True

        except sqlite3.Error as e:
            print(f"Error deleting rows from table '{table}': {e}")
            return False
