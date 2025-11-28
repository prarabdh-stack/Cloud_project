# migrate_mysql_to_firestore.py
import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

# --- CONFIG ---
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nilay',     # change if needed
    'database': 'library'
}
# path to your service account JSON (rename if needed)
SERVICE_ACCOUNT = r"project(Library_management_system_using_HTML_Fire_Base)\firebase_credentials.json"
# ----------------

# init firebase
cred = credentials.Certificate(SERVICE_ACCOUNT)
firebase_admin.initialize_app(cred)
db = firestore.client()

# connect mysql
cnx = mysql.connector.connect(**MYSQL_CONFIG)
cursor = cnx.cursor(dictionary=True)  # get dict rows

def migrate_books():
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    for r in rows:
        # Map your MySQL columns to Firestore fields
        book_doc = {
            "title": r.get("title"),
            "author": r.get("author"),
            "genre": r.get("genre"),
            "published_year": r.get("published_year") or r.get("year"),
            "available_copies": int(r.get("available_copies") or r.get("copies") or 0)
        }
        # Use original book_id as doc id if you want stable ids
        doc_id = str(r.get("book_id"))
        db.collection("books").document(doc_id).set(book_doc)
    print(f"Imported {len(rows)} books")

def migrate_members():
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    for r in rows:
        member_doc = {
            "name": r.get("name"),
            "email": r.get("email"),
            "phone": r.get("phone"),
            "join_date": (r.get("join_date").isoformat() if isinstance(r.get("join_date"), (date,)) else (str(r.get("join_date")) if r.get("join_date") else date.today().isoformat())),
            "password": r.get("password") or "password123"
        }
        doc_id = str(r.get("member_id"))
        db.collection("members").document(doc_id).set(member_doc)
    print(f"Imported {len(rows)} members")

def migrate_users():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for r in rows:
        user_doc = {
            "username": r.get("username"),
            "password": r.get("password"),
            "role": r.get("role") or "librarian"
        }
        doc_id = str(r.get("user_id") or r.get("username"))
        db.collection("users").document(doc_id).set(user_doc)
    print(f"Imported {len(rows)} users")

def migrate_borrowed():
    cursor.execute("SELECT * FROM borrowed_books")
    rows = cursor.fetchall()
    for r in rows:
        borrow_doc = {
            "book_id": str(r.get("book_id")),
            "member_id": str(r.get("member_id")),
            "borrow_date": (r.get("borrow_date").isoformat() if hasattr(r.get("borrow_date"), 'isoformat') else str(r.get("borrow_date"))),
            "due_date": (r.get("due_date").isoformat() if hasattr(r.get("due_date"), 'isoformat') else str(r.get("due_date"))),
            "return_date": (r.get("return_date").isoformat() if getattr(r.get("return_date"), 'isoformat', None) else (str(r.get("return_date")) if r.get("return_date") else None))
        }
        db.collection("borrowed_books").document().set(borrow_doc)
    print(f"Imported {len(rows)} borrowed entries")

if __name__ == "__main__":
    migrate_books()
    migrate_members()
    migrate_users()
    migrate_borrowed()
    cursor.close()
    cnx.close()
    print("Migration completed.")
