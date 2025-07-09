import sqlite3
from tabulate import tabulate
from datetime import datetime

# Connect to DB (or create if not exists)
conn = sqlite3.connect("bookstore.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    quantity INTEGER,
    sale_date TEXT,
    FOREIGN KEY(book_id) REFERENCES books(id)
);
""")
conn.commit()

# Add new book
def add_book(title, author, price, stock):
    cursor.execute("INSERT INTO books (title, author, price, stock) VALUES (?, ?, ?, ?)",
                   (title, author, price, stock))
    conn.commit()
    print("✅ Book added successfully.")

# List all books
def list_books():
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["ID", "Title", "Author", "Price", "Stock"], tablefmt="grid"))

# Sell a book
def sell_book(book_id, quantity):
    cursor.execute("SELECT stock FROM books WHERE id = ?", (book_id,))
    result = cursor.fetchone()
    if result and result[0] >= quantity:
        new_stock = result[0] - quantity
        cursor.execute("UPDATE books SET stock = ? WHERE id = ?", (new_stock, book_id))
        cursor.execute("INSERT INTO sales (book_id, quantity, sale_date) VALUES (?, ?, ?)",
                       (book_id, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        print("🛒 Sale recorded.")
    else:
        print("❌ Not enough stock or book not found.")

# Sales Report
def sales_report():
    cursor.execute("""
    SELECT b.title, SUM(s.quantity) as total_sold, SUM(s.quantity * b.price) as total_revenue
    FROM sales s
    JOIN books b ON s.book_id = b.id
    GROUP BY s.book_id
    ORDER BY total_sold DESC
    """)
    rows = cursor.fetchall()
    print("\n📊 Sales Report:")
    print(tabulate(rows, headers=["Book Title", "Total Sold", "Revenue"], tablefmt="fancy_grid"))

# CLI Menu
def menu():
    while True:
        print("\n📚 Bookstore Menu")
        print("1. Add Book")
        print("2. List Books")
        print("3. Sell Book")
        print("4. Show Sales Report")
        print("5. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            title = input("Title: ")
            author = input("Author: ")
            price = float(input("Price: "))
            stock = int(input("Stock: "))
            add_book(title, author, price, stock)
        elif choice == "2":
            list_books()
        elif choice == "3":
            book_id = int(input("Book ID: "))
            quantity = int(input("Quantity: "))
            sell_book(book_id, quantity)
        elif choice == "4":
            sales_report()
        elif choice == "5":
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid choice.")

menu()
conn.close()
