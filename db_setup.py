import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# --- DATABASE SETUP ---
conn = sqlite3.connect("bookstore.db")
cursor = conn.cursor()

# Drop old tables to avoid schema conflicts
cursor.execute("DROP TABLE IF EXISTS users;")
cursor.execute("DROP TABLE IF EXISTS books;")
cursor.execute("DROP TABLE IF EXISTS sales;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
);
""")

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

# --- GLOBAL ROOT ---
root = tk.Tk()
root.withdraw()

# --- FUNCTIONS ---
def open_login_screen():
    register_frame.destroy()
    show_login_screen()

def open_register_again():
    login_frame.destroy()
    show_register_screen()

def register_user():
    u = username_entry.get()
    e = email_entry.get()
    p = password_entry.get()
    if not u or not p or not e:
        messagebox.showerror("Error", "All fields are required.")
        return
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (u, e, p))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful. Please login.")
        register_frame.destroy()
        show_login_screen()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username or Email already exists. Please login.")
        register_frame.destroy()
        show_login_screen()

def login_user():
    u = login_username.get()
    p = login_password.get()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p))
    if cursor.fetchone():
        login_frame.destroy()
        main_screen()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def forgot_password():
    messagebox.showinfo("Forgot Password", "Please register again with a new email or contact admin.")

def show_register_screen():
    global register_frame, username_entry, email_entry, password_entry
    register_frame = tk.Toplevel()
    register_frame.title("Register - Bookstore")
    register_frame.geometry("320x300")
    register_frame.configure(bg="#ffe4e1")

    tk.Label(register_frame, text="📚", font=("Arial", 40), bg="#ffe4e1").pack(pady=10)
    tk.Label(register_frame, text="Username", bg="#ffe4e1").pack()
    username_entry = tk.Entry(register_frame, relief="groove", bd=2)
    username_entry.pack(pady=3)

    tk.Label(register_frame, text="Email", bg="#ffe4e1").pack()
    email_entry = tk.Entry(register_frame, relief="groove", bd=2)
    email_entry.pack(pady=3)

    tk.Label(register_frame, text="Password", bg="#ffe4e1").pack()
    password_entry = tk.Entry(register_frame, show="*", relief="groove", bd=2)
    password_entry.pack(pady=3)

    tk.Button(register_frame, text="Register", bg="#4CAF50", fg="white", command=register_user).pack(pady=10)

def show_login_screen():
    global login_frame, login_username, login_password
    login_frame = tk.Toplevel()
    login_frame.title("Login - Bookstore")
    login_frame.geometry("300x240")
    login_frame.configure(bg="#e6f7ff")

    tk.Label(login_frame, text="📘", font=("Arial", 40), bg="#e6f7ff").pack(pady=5)
    tk.Label(login_frame, text="Username", bg="#e6f7ff").pack()
    login_username = tk.Entry(login_frame, relief="groove", bd=2)
    login_username.pack(pady=3)

    tk.Label(login_frame, text="Password", bg="#e6f7ff").pack()
    login_password = tk.Entry(login_frame, show="*", relief="groove", bd=2)
    login_password.pack(pady=3)

    tk.Button(login_frame, text="Login", bg="#2196F3", fg="white", command=login_user).pack(pady=5)
    tk.Button(login_frame, text="Forgot Password?", bg="#ffc107", command=forgot_password).pack(pady=2)
    tk.Button(login_frame, text="Register Again", bg="#9C27B0", fg="white", command=open_register_again).pack(pady=2)

def main_screen():
    main = tk.Toplevel()
    main.title("📚 Bookstore Dashboard")
    main.configure(bg="#f5f5dc")

    style = {"bg": "#f5f5dc", "fg": "#1f4e79", "font": ("Arial", 10, "bold")}

    def clear_fields():
        title.delete(0, tk.END)
        author.delete(0, tk.END)
        price.delete(0, tk.END)
        stock.delete(0, tk.END)

    def add_book():
        try:
            t, a = title.get(), author.get()
            pr, s = float(price.get()), int(stock.get())
            if not t or not a:
                messagebox.showerror("Error", "Title and Author are required.")
                return
            cursor.execute("INSERT INTO books (title, author, price, stock) VALUES (?, ?, ?, ?)", (t, a, pr, s))
            conn.commit()
            messagebox.showinfo("Success", f"Book '{t}' added.")
            clear_fields()
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock.")

    def sell_book():
        try:
            b_id = int(book_id.get())
            qty = int(quantity.get())
            cursor.execute("SELECT stock, title FROM books WHERE id = ?", (b_id,))
            result = cursor.fetchone()
            if result:
                current_stock, title_txt = result
                if current_stock >= qty:
                    new_stock = current_stock - qty
                    cursor.execute("UPDATE books SET stock = ? WHERE id = ?", (new_stock, b_id))
                    cursor.execute("INSERT INTO sales (book_id, quantity, sale_date) VALUES (?, ?, ?)",
                                   (b_id, qty, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    messagebox.showinfo("Success", f"{qty} copies of '{title_txt}' sold.")
                else:
                    messagebox.showerror("Stock Error", f"Only {current_stock} copies of '{title_txt}' available.")
            else:
                messagebox.showerror("Not Found", f"No book found with ID {b_id}.")
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid numbers for Book ID and Quantity.")

    def view_report():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("""
        SELECT b.title, SUM(s.quantity), SUM(s.quantity * b.price)
        FROM sales s JOIN books b ON s.book_id = b.id
        GROUP BY s.book_id
        """)
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def view_books():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT id, title, author, price, stock FROM books")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def export_csv():
        cursor.execute("""
        SELECT b.title, SUM(s.quantity), SUM(s.quantity * b.price)
        FROM sales s JOIN books b ON s.book_id = b.id
        GROUP BY s.book_id
        """)
        rows = cursor.fetchall()
        with open("sales_report.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Quantity Sold", "Revenue"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", "Report saved as sales_report.csv")

    def show_chart():
        cursor.execute("""
        SELECT b.title, SUM(s.quantity)
        FROM sales s JOIN books b ON s.book_id = b.id
        GROUP BY s.book_id
        """)
        data = cursor.fetchall()
        if data:
            titles = [row[0] for row in data]
            sales = [row[1] for row in data]
            plt.figure(figsize=(8, 5))
            plt.bar(titles, sales, color="orange")
            plt.title("Top Selling Books")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            messagebox.showinfo("Info", "No sales data to display.")

    # --- Form Fields ---
    tk.Label(main, text="Title", **style).grid(row=0, column=0)
    title = tk.Entry(main); title.grid(row=0, column=1, ipady=3)

    tk.Label(main, text="Author", **style).grid(row=1, column=0)
    author = tk.Entry(main); author.grid(row=1, column=1, ipady=3)

    tk.Label(main, text="Price", **style).grid(row=2, column=0)
    price = tk.Entry(main); price.grid(row=2, column=1, ipady=3)

    tk.Label(main, text="Stock", **style).grid(row=3, column=0)
    stock = tk.Entry(main); stock.grid(row=3, column=1, ipady=3)

    tk.Button(main, text="Add Book", bg="#4CAF50", fg="white", command=add_book).grid(row=4, column=1, pady=5)

    tk.Label(main, text="Book ID", **style).grid(row=5, column=0)
    book_id = tk.Entry(main); book_id.grid(row=5, column=1, ipady=3)

    tk.Label(main, text="Quantity", **style).grid(row=6, column=0)
    quantity = tk.Entry(main); quantity.grid(row=6, column=1, ipady=3)

    tk.Button(main, text="Sell Book", bg="#f44336", fg="white", command=sell_book).grid(row=7, column=1, pady=5)
    tk.Button(main, text="View Sales Report", bg="#2196F3", fg="white", command=view_report).grid(row=8, column=0, columnspan=2, pady=5)
    tk.Button(main, text="📖 View All Books", bg="#795548", fg="white", command=view_books).grid(row=9, column=0, columnspan=2, pady=5)
    tk.Button(main, text="Export CSV", bg="#9C27B0", fg="white", command=export_csv).grid(row=10, column=0, columnspan=2, pady=5)
    tk.Button(main, text="📊 Show Chart", bg="#FF9800", fg="black", command=show_chart).grid(row=11, column=0, columnspan=2, pady=5)

    # --- Treeview for reports and book list ---
    tree = ttk.Treeview(main, columns=("Col1", "Col2", "Col3", "Col4", "Col5"), show='headings')
    tree.grid(row=12, column=0, columnspan=2, pady=10)
    for i, heading in enumerate(["ID/Title", "Title/Qty", "Author/Sold", "Price/Revenue", "Stock"], start=1):
        tree.heading(f"Col{i}", text=heading)
        tree.column(f"Col{i}", width=120)

# --- START APP ---
show_register_screen()
root.mainloop()

# The Code is modified with some login page
