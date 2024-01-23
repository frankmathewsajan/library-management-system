import sqlite3
import base64
from classes.Accounts import Accounts
from classes.Database import Database as DB



class Library:
    def searches() -> list:
        tuple_list = DB.get(["username", "search"], "searches")
        return list(map(lambda tup: tup[1], tuple_list)) if tuple_list else []

    def books(columns: list, search_by: str = '', value: str = '') -> list:
        condition = f"{search_by} = '{value}'" if '' not in (search_by,value) else ''
        tuple_list = DB.get(columns, "library", condition)
        return tuple_list
    

    def set_image(uid: str, data: bytes) -> bool:
        DB.update('library', {
            'image_data': data
        }, f"uid = '{uid}'")
        return True

    def set_books(data: dict, search: str) -> bool:
        books = []

        for book in data.get("items", []):
            try:
                from project import log,decode,encode
                log('set_books', book)
                volume_info = book.get("volumeInfo", {})
                author = encode(volume_info.get("authors", [None])[0]) if volume_info.get("authors") else None
                pgno = volume_info.get("pageCount")
                if author and pgno != 0:
                    sales_info = book.get("saleInfo", {})
                    saleability, price = (False, 0) if sales_info.get("saleability") == "NOT_FOR_SALE" else (True, sales_info.get("listPrice", {}).get("amount",0))
                    title = volume_info.get("title")
                    author = encode(volume_info.get("authors", [None])[0]) if volume_info.get("authors") else None
                    uid = book.get("id")
                    books.append((title, author , uid))
                    book_data = {
                        "title": title,
                        "image_data": None,
                        "author": author,
                        "publisher": encode(volume_info.get("publisher", "")) if volume_info.get("publisher") else None,
                        "description": encode(volume_info.get("description", "")) if volume_info.get("description") else None,
                        "imageLinks": volume_info.get("imageLinks", {}).get("thumbnail", None),
                        "price": price,
                        "uid": uid,
                        "pgno": pgno,
                        "type": volume_info.get("maturityRating"),
                        "saleability": saleability,
                        "search": search
                    }
                    DB.insert('library', book_data)
                    log('set_books',f'{uid} added')
            except Exception as e:
                log('set_books',f'Error: {str(e)}')


        try:
            DB.insert('searches', {
                'search': search,
                'username': Accounts.username()
            })
        except sqlite3.Error as error:
            print('Search Exists', error)
        return books
