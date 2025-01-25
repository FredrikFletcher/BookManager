import asyncio
from tkinter import *
from tkinter import ttk, messagebox
import controller as controller

class BookManagerApp:
    # this function is called when an instance of the Bookmanager app is created
    def __init__(self, root):
        self.root = root
        self.root.title("Book Manager")
        self.root.geometry("900x700")
        self.root.minsize(400, 300)
        self.ctrl = controller.Controller()

        self.ctrl.initialize_control()

        # Configure layout
        self.root.grid_rowconfigure(1, weight=4)  
        self.root.grid_rowconfigure(2, weight=1)  
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        search_frame = Frame(self.root)
        search_frame.grid(row=0, column=0, sticky="EW", padx=20, pady=10) # Add padding to the search frame

        search_label = Label(search_frame, text="Search:")
        search_label.pack(side=LEFT, padx=(0, 10))

        self.search_entry = Entry(search_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda event: self.run_asyncio_task(self.search_books, event))

        # Table Section
        self.setup_table()

        # Input Section
        self.setup_inputs()

        # Buttons
        self.setup_buttons()

        # Center Window
        self.center_window()


    def run_asyncio_task(self, coro, *args):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            asyncio.create_task(coro(*args))
        else:
            loop.run_until_complete(coro(*args))

    
    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def setup_table(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        table_frame = Frame(self.root)
        table_frame.grid(row=1, column=0, sticky="NSEW", padx=20, pady=10)

        columns = ("ID", "Title", "Author", "Year", "Status", "Category", "Format")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="NSEW")
    

        # Configure table headers
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=W)

        self.tree.bind("<<TreeviewSelect>>", self.populate_fields)

    def setup_inputs(self):
        input_frame = Frame(self.root)
        input_frame.grid(row=2, column=0, sticky="NSEW", padx=20, pady=10)

        self.fields = {}
        labels = ["title", "author", "year", "status", "category", "format"]
        for i, label in enumerate(labels):
            Label(input_frame, text=label).grid(row=i, column=0, sticky="W", pady=5)
            if label == "status":
                self.fields[label] = StringVar(value="To Read")
                OptionMenu(input_frame, self.fields[label], "To Read ", "Read").grid(
                    row=i, column=1, padx=10, pady=5, sticky="EW"
                )
            elif label in ["category", "format"]:
                values = (
                    ["General", "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance", "Dystopian", "Horror", "Biography", "Autobiography", "Self-Help", "History", "Science", "Travel", "Cooking", "Art", "Poetry", "Religion", "Philosophy"]
                    if label == "category"
                    else ["Physical", "E-Book", "Audio"]
                )
                self.fields[label] = StringVar(value=values[0])
                ttk.Combobox(
                    input_frame, textvariable=self.fields[label], values=values, state="readonly"
                ).grid(row=i, column=1, padx=10, pady=5, sticky="EW")
            else:
                entry = Entry(input_frame)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky="EW")
                self.fields[label] = entry

    def setup_buttons(self):
        button_frame = Frame(self.root)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        Button(button_frame, text="Add Book", command=lambda: self.run_asyncio_task(self.handle_add_book)).grid(
            row=0, column=0, padx=5, pady=5
        )
        Button(button_frame, text="Delete Book", command=lambda: self.run_asyncio_task(self.handle_delete_book)).grid(
            row=0, column=1, padx=5, pady=5
        )
        Button(button_frame, text="Update Book", command=lambda: self.run_asyncio_task(self.handle_update_book)).grid(
            row=0, column=2, padx=5, pady=5
        )

    async def search_books(self, _):
        query = self.search_entry.get().lower()
        books = await self.ctrl.get_books()
        filtered_books = [book for book in books if query in " ".join(map(str, book)).lower()]
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in filtered_books:
            self.tree.insert("", END, values=book)

    def clear_inputs(self):
        for field in self.fields.values():
            if isinstance(field, Entry):
                field.delete(0, END)
            else:
                field.set(" ")

    async def refresh_book_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        books = await self.ctrl.get_books()
        for book in books:
            self.tree.insert("", END, values=book)

    async def handle_add_book(self):
        try:
            # Get the values from the input fields, strip the values and store them in a dictionary, values, with the key as the field name
            values = {k: (v.get() if isinstance(v, StringVar) else v.get().strip()) for k, v in self.fields.items()}
            if values["format"] == "Other":
            # Map "Other" to a default acceptable value, e.g., "Physical"
                values["format"] = "Physical"  # Or handle this in a way that makes sense for your app
            
            if not all(values.values()):
                raise ValueError("All fields are required.")
            await self.ctrl.add_book(**values)
            await self.refresh_book_list()
            self.clear_inputs()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    async def handle_delete_book(self):
        try:
            selected_item = self.tree.selection()[0]
            book_id = self.tree.item(selected_item, "values")[0]
            await self.ctrl.delete_book(book_id)
            await self.refresh_book_list()
            self.clear_inputs()
        except IndexError:
            messagebox.showerror("Error", "No book selected!")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    async def handle_update_book(self):
        
        try:
            selected_item = self.tree.selection()[0]
            book_id = self.tree.item(selected_item, "values")[0]
            values = {k: (v.get() if isinstance(v, StringVar) else v.get().strip()) for k, v in self.fields.items()}
            print(f"Values to update: {values}")
            await self.ctrl.update_book(book_id, **values)
            self.clear_inputs()
            await self.refresh_book_list()
        except IndexError:
            messagebox.showerror("Error", "No book selected!")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    def populate_fields(self, _):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                self.clear_inputs()
                return
            book = self.tree.item(selected_item[0], "values") # Get the values of the selected item
            for i, key in enumerate(self.fields): # Loop through the fields
                if isinstance(self.fields[key], Entry): # Check if the field is an Entry widget
                    self.fields[key].delete(0, END) # Delete the value in the field
                    self.fields[key].insert(0, book[i + 1]) # Insert the value of the book at index i+1 into the field
                else:
                    self.fields[key].set(book[i + 1])
        except Exception as e:
            self.clear_inputs()
            print(f"Error populating fields: {e}")


if __name__ == "__main__":
    root = Tk()
    app = BookManagerApp(root) # Create an instance of the BookManagerApp class
    app.ctrl.initialize_control() # Initialize the database
    asyncio.run(app.refresh_book_list()) # List all books
    

    def on_closing():
        asyncio.run(app.ctrl.close())# Close the connection
        root.destroy() # Close the window
    
    root.protocol("WM_DELETE_WINDOW", on_closing) # Call the close function when the window is closed
    root.mainloop()# Path: controller.py
