import sqlite3
from classes.Accounts import Accounts
from classes.Database import Database as DB


class Library:

    def searches() -> list:
        tuple_list = DB.get(["username", "search"], "searches")
        return list(map(lambda tup: tup[1], tuple_list)) if tuple_list else []

    def books(columns: list, search_by: str = '', value: str = '') -> list:
        condition = f"{search_by} = '{value}'" if '' not in (search_by,value) else ''
        tuple_list = DB.get(columns, "library", condition)
        print(tuple_list)
        return tuple_list
    

    def set_image(uid: str, data: bytes) -> bool:
        DB.update('library', {
            'image_data': data
        }, f"uid = '{uid}'")
        return True

    def set_books(data: dict, search: str) -> bool:
        books = []
        for book in data.get("items", []):
            volume_info = book.get("volumeInfo", {})
            sales_info = book.get("saleInfo", {})
            saleability, price = (
                False, 0) if sales_info["saleability"] == "NOT_FOR_SALE" else (
                True, sales_info["listPrice"]["amount"])
            title = volume_info.get("title")
            author = volume_info.get("authors")[0]
            uid = book.get("id")
            books.append((title, author, uid))
            book_data = {
                "title": title,
                "image_data": None,
                "author": author,
                "publisher": volume_info.get("publisher"),
                "description": volume_info.get("description"),
                "imageLinks": volume_info["imageLinks"]["thumbnail"],
                "price": price,
                "uid": uid,
                "pgno": volume_info.get("pageCount"),
                "type": volume_info.get("maturityRating"),
                "saleability": saleability,
                "search": search
            }
            DB.insert('library', book_data)
        try:
            DB.insert('searches', {
                'search': search,
                'username': Accounts.username()
            })
        except sqlite3.Error as error:
            print('Search Exists', error)
        return books
