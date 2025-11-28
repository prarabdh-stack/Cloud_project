from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date, timedelta, datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase (ensure firebase_credentials.json is in project root)
if not firebase_admin._apps:
    cred = credentials.Certificate(r"project(Library_management_system_using_HTML_Fire_Base)\firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------- Helpers ----------
def book_doc_to_tuple(doc):
    data = doc.to_dict()
    # tuple: (book_id, title, author, genre, published_year, available_copies)
    return (doc.id,
            data.get('title'),
            data.get('author'),
            data.get('genre'),
            data.get('published_year'),
            data.get('available_copies'))

def member_doc_to_tuple(doc):
    data = doc.to_dict()
    # tuple: (member_id, name, email, phone, join_date, password)
    return (doc.id,
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('join_date'),
            data.get('password'))

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    username = request.form['username']
    password = request.form['password']

    error = None

    if role == 'librarian':
        users_ref = db.collection('users')
        query = users_ref.where('username', '==', username).where('password', '==', password).limit(1).get()
        if query:
            session['username'] = username
            session['role'] = 'librarian'
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid librarian credentials"

    elif role == 'member':
        members_ref = db.collection('members')
        query = members_ref.where('name', '==', username).where('password', '==', password).limit(1).get()
        if query:
            session['username'] = username
            session['role'] = 'member'
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid member credentials"

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', user=session['username'], role=session['role'])

@app.route('/books')
def view_books():
    books_ref = db.collection('books').stream()
    books = [book_doc_to_tuple(doc) for doc in books_ref]
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year = int(request.form['year'])
        copies = int(request.form['copies'])

        # Generate new Firestore document automatically
        new_book_ref = db.collection('books').document()

        new_book_ref.set({
            'book_id': new_book_ref.id,
            'title': title,
            'author': author,
            'genre': genre,
            'published_year': year,
            'available_copies': copies,
            'title_lower': title.lower(),
            'author_lower': author.lower(),
            'genre_lower': genre.lower(),
        })

        return redirect(url_for('view_books'))

    return render_template('add_book.html')


@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']

        book_doc = db.collection('books').document(book_id).get()
        if book_doc.exists:
            book = book_doc.to_dict()
            available = book.get('available_copies', 0)
            if available > 0:
                borrow_date = date.today().isoformat()
                due_date = (date.today() + timedelta(days=14)).isoformat()

                db.collection('borrowed_books').document().set({
                    "book_id": book_id,
                    "member_id": member_id,
                    "borrow_date": borrow_date,
                    "due_date": due_date,
                    "return_date": None
                })
                # decrement available copies
                db.collection('books').document(book_id).update({
                    "available_copies": available - 1
                })

        return redirect(url_for('view_books'))

    return render_template('borrow_book.html')

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']

        borrowed_ref = db.collection('borrowed_books')
        query = borrowed_ref.where('book_id', '==', book_id)\
                            .where('member_id', '==', member_id)\
                            .where('return_date', '==', None)\
                            .limit(1).get()

        if query:
            borrow_doc = query[0]
            borrow_data = borrow_doc.to_dict()
            due_date_str = borrow_data.get('due_date')
            return_date = date.today()
            overdue_days = 0
            try:
                due_dt = datetime.fromisoformat(due_date_str).date()
                overdue_days = (return_date - due_dt).days
            except Exception:
                overdue_days = 0

            fee = max(overdue_days * 10, 0) 

            # update return_date
            borrowed_ref.document(borrow_doc.id).update({
                "return_date": return_date.isoformat()
            })

            # increment available copies
            book_doc = db.collection('books').document(book_id).get()
            if book_doc.exists:
                avail = book_doc.to_dict().get('available_copies', 0)
                db.collection('books').document(book_id).update({
                    "available_copies": avail + 1
                })

        return redirect(url_for('view_books'))

    return render_template('return_book.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/my_books')
def my_borrowed_books():
    if 'username' not in session or session['role'] != 'member':
        return redirect(url_for('home'))

    members_ref = db.collection('members')
    q = members_ref.where('name', '==', session['username']).limit(1).get()
    if not q:
        return redirect(url_for('dashboard'))

    member_doc = q[0]
    member_id = member_doc.id

    borrowed_ref = db.collection('borrowed_books').where('member_id', '==', member_id).stream()
    books = []

    for b in borrowed_ref:
        bdata = b.to_dict()
        book_id = bdata.get('book_id')
        book_doc = db.collection('books').document(book_id).get()
        title = book_doc.to_dict().get('title') if book_doc.exists else 'Unknown'

        borrow_date = bdata.get('borrow_date')
        due_date = bdata.get('due_date')
        returned_date = bdata.get('return_date')

        # compute fee
        fee = "-"
        if returned_date:
            try:
                due_dt = datetime.fromisoformat(due_date).date()
                ret_dt = datetime.fromisoformat(returned_date).date()
                overdue = (ret_dt - due_dt).days
                fee = max(overdue * 10, 0)
            except:
                fee = "-"

        books.append((book_id, title, borrow_date, due_date, returned_date, fee))

    return render_template('my_books.html', books=books)

@app.route('/members')
def manage_members():
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    members = [member_doc_to_tuple(doc) for doc in db.collection('members').stream()]
    return render_template('members.html', members=members)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session or session['role'] != 'member':
        return redirect(url_for('home'))

    if request.method == 'POST':
        old = request.form['old_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']
        email = request.form['email']

        members_ref = db.collection('members')
        q = members_ref.where('name', '==', session['username']).where('email', '==', email).limit(1).get()
        error = None
        if q:
            mem_doc = q[0]
            mem_data = mem_doc.to_dict()
            if mem_data.get('password') == old:
                if new == confirm:
                    members_ref.document(mem_doc.id).update({"password": new})
                    return redirect(url_for('dashboard'))
                else:
                    error = "New passwords do not match."
            else:
                error = "Invalid email or current password."
        else:
            error = "Invalid email or current password."

        return render_template('change_password.html', error=error)

    return render_template('change_password.html')

@app.route('/search', methods=['GET', 'POST'])
def search_books():
    books = []

    if request.method == 'POST':
        title = request.form.get('title', '').strip().lower()
        author = request.form.get('author', '').strip().lower()
        genre = request.form.get('genre', '').strip().lower()
        year = request.form.get('year', '').strip()

        books_ref = db.collection('books')
        query = books_ref

        if title:
            query = query.where('title_lower', '>=', title).where('title_lower', '<=', title + '\uf8ff')

        if author:
            query = query.where('author_lower', '>=', author).where('author_lower', '<=', author + '\uf8ff')

        if genre:
            query = query.where('genre_lower', '>=', genre).where('genre_lower', '<=', genre + '\uf8ff')

        if year:
            query = query.where('published_year', '==', int(year))

        results = query.stream()

        for doc in results:
            data = doc.to_dict()
            data['book_id'] = doc.id

            books.append(data)

    return render_template('search.html', books=books)


from datetime import datetime

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        members_ref = db.collection('members').order_by('member_id').stream()

        last_id = 0
        found_any = False

        for m in members_ref:
            found_any = True
            data = m.to_dict()
            if data.get('member_id', 0) > last_id:
                last_id = data['member_id']

        if found_any:
            new_member_id = last_id + 1
        else:
            new_member_id = 1  

        db.collection('members').document(str(new_member_id)).set({
            'member_id': new_member_id,
            'name': name,
            'email': email,
            'phone': phone,
            'password': 'password123',   # Default password
            'join_date': datetime.now()
        })

        return redirect(url_for('manage_members'))

    return render_template('add_member.html')


@app.route('/update_book/<book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    book_ref = db.collection('books').document(book_id)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year = int(request.form['year'])
        copies = int(request.form['copies'])

        book_ref.update({
            'title': title,
            'author': author,
            'genre': genre,
            'published_year': year,
            'available_copies': copies,

            'title_lower': title.lower(),
            'author_lower': author.lower(),
            'genre_lower': genre.lower()
        })

        return redirect(url_for('view_books'))

    doc = book_ref.get()
    if not doc.exists:
        return "Error: Book not found"

    book = doc.to_dict()
    book['book_id'] = book_id

    return render_template('update_book.html', book=book)



@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    db.collection('books').document(book_id).delete()
    return redirect(url_for('view_books'))

@app.route('/delete_member/<member_id>')
def delete_member(member_id):
    if 'username' not in session or session['role'] != 'librarian':
        return redirect(url_for('home'))

    # Check if member has any unreturned books
    borrowed_ref = db.collection('borrowed_books')
    q = borrowed_ref.where('member_id', '==', member_id).where('return_date', '==', None).limit(1).get()

    if q:
        return "<script>alert('This member cannot be deleted because they have unreturned books.'); window.location.href='/members';</script>"
    db.collection('members').document(member_id).delete()
    return redirect(url_for('manage_members'))

if __name__ == '__main__':
    app.run(debug=True)
