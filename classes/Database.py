import sqlite3


class Database:
    def init() -> None:

        conn, cursor = Database.connect()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT,
                password TEXT,
                auth boolean
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                uid TEXT,
                type TEXT,
                user TEXT
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS all_books (
                title TEXT,
                image_data BLOB,
                authors TEXT,
                publisher TEXT,
                description TEXT,
                imageLinks TEXT,
                price NUMERIC,
                uid TEXT,
                pgno INTEGER,
                type_ TEXT,
                saleability BOOLEAN,
                search TEXT
            );
            """
        )
        Database.save(conn, cursor)
        print("Database created successfully!")

    def connect() -> tuple:
        """
        Create connection to database
        returns connection & cursor
        """
        sqliteConnection = sqlite3.connect('./databases/sqlite.db')
        cursor = sqliteConnection.cursor()
        return (sqliteConnection, cursor)

    def save(sqliteConnection: sqlite3.Connection,
             cursor: sqlite3.Cursor) -> bool:
        """
        Commit & Close Connection
        """
        cursor.close()
        sqliteConnection.commit()

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
            conn, cursor = Database.connect()
            query = f"SELECT {', '.join(columns)} FROM {table}" + (f" WHERE {condition}" if condition else "")
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
            query = f"SELECT COUNT(*) FROM {table}" + (f" WHERE {condition}" if condition else "")
            cursor.execute(query)
            count = cursor.fetchone()[0]
            Database.save(conn,cursor)
            return count
                

        except sqlite3.Error as e:
            print(f"Error counting rows in table '{table}': {e}")
            return 0    
    



