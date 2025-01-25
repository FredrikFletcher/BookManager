import aiosqlite # Import the aiosqlite module
import os

# define the database file path
class BookManager:
    def initialize(self):
        self.database = 'Database/Books.db' # create a database variable to store the path to the database file

        print(f"Database file path: {os.path.abspath(self.database)}") # Print the absolute path to the database file
        #conn = aiosqlite.connect(database) # Create a connection object
        print(f"Connected to database: {self.database}") # Print the connection object


    async def insert_book(self, title, author, year, status, category, format):
        async with aiosqlite.connect(self.database) as db:
            await db.execute('''
        INSERT INTO Books (title, author, year, status, category, format) VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, author, year, status, category, format))
            await db.commit()


    async def list_books(self):
        try:
            async with aiosqlite.connect(self.database) as db:
                async with db.execute('SELECT * FROM Books') as cursor:
                    books = await cursor.fetchall()
            return books # Return a list of all books
        except aiosqlite.OperationalError as e:
            print("Error: Table 'Books' does not exist!")
            return []  # Return an empty list if the table doesn't exist
   

# Update book
    async def update_book(self, id, title, author, year, status, category, format):
        async with aiosqlite.connect(self.database) as db:
            async with db.execute('''
            UPDATE Books
            SET title = ?, author = ?, year = ?, status = ?, Category = ?, format = ?
            WHERE id = ?
            ''', (title, author, year, status, category, format, id)):
                await db.commit()
# Delete book
    async def delete_book(self,id):
        async with aiosqlite.connect(self.database) as db:
            async with db.execute('''DELETE FROM Books WHERE id = ? ''', (id,)):
                await db.commit()

    async def close_connection(self):
        async with aiosqlite.connect(self.database) as db:
            await db.close()
            print("Connection closed")




