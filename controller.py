from tkinter import *
import book_manager as db

class Controller:
    def __init__(self):
        self.book_manager = db.BookManager()

    async def initialize_control(self):
        await self.book_manager.initialize()

    async def add_book(self, title, author, year, status, category, format):
        if not title or not author or not year or not status:
            raise ValueError("All fields are required.")
        await self.book_manager.insert_book(title, author, year, status, category, format)

    async def get_books(self):
        return await self.book_manager.list_books()

    async def delete_book(self, book_id):
        await self.book_manager.delete_book(book_id)

    async def update_book(self,id, title, author, year, status, category, format):
        print(f"Received arguments: id={id}, title={title}, author={author}, year={year}, status={status}, category={category}, format={format}")

        if not title or not author or not year or not status:
            raise ValueError("All fields are required.")
        await self.book_manager.update_book( id, title, author, year, status, category, format)
    
    async def calculate_books(self):
        return await self.book_manager.calculate_books()
    
    async def calculate_read_books(self, status):
        return await self.book_manager.calculate_read_books(status)
    
    async def calculate_categories(self):
        return await self.book_manager.calculate_categories()
    
    

    async def close(self):
        await self.book_manager.close_connection()

