from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("bookshop.db")
    conn.row_factory = sqlite3.Row
    return conn

# สร้าง table ครั้งแรก
def init_db():
    conn = get_db()

    # Create categories table (ประเภทหนังสือ)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Create books table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        price REAL,
        image TEXT,
        stock INTEGER DEFAULT 0,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    """)

    # เพิ่ม column กรณีอัปเดตระบบ
    try:
        conn.execute("ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute("ALTER TABLE books ADD COLUMN category_id INTEGER REFERENCES categories(id)")
    except sqlite3.OperationalError:
        pass

    # default categories
    default_categories = ["Fiction", "Non-fiction", "Education", "Comics", "Children"]
    for cat in default_categories:
        try:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

init_db()

# หน้าเมนู
@app.route("/")
def bookmenu():
    conn = get_db()
    books = conn.execute("""
        SELECT books.*, categories.name as category_name
        FROM books
        LEFT JOIN categories ON books.category_id = categories.id
    """).fetchall()
    conn.close()
    return render_template("bookmenu.html", books=books)

# เพิ่มหนังสือ
@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        image = request.form["image"]
        stock = request.form.get("stock", "0")
        category_id = request.form.get("category_id")

        try:
            stock = int(stock)
        except ValueError:
            stock = 0

        try:
            category_id = int(category_id) if category_id else None
        except ValueError:
            category_id = None

        conn.execute("""
            INSERT INTO books (title, author, price, image, stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, author, price, image, stock, category_id))

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("append.html", categories=categories)

# แก้ไข
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        image = request.form["image"]
        stock = request.form.get("stock", "0")
        category_id = request.form.get("category_id")

        try:
            stock = int(stock)
        except ValueError:
            stock = 0

        try:
            category_id = int(category_id) if category_id else None
        except ValueError:
            category_id = None

        conn.execute("""
            UPDATE books
            SET title=?, author=?, price=?, image=?, stock=?, category_id=?
            WHERE id=?
        """, (title, author, price, image, stock, category_id, id))

        conn.commit()
        conn.close()
        return redirect("/")

    book = conn.execute("""
        SELECT books.*, categories.name as category_name
        FROM books
        LEFT JOIN categories ON books.category_id = categories.id
        WHERE books.id=?
    """, (id,)).fetchone()

    conn.close()
    return render_template("edit.html", book=book, categories=categories)

# ลบ
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)