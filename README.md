# Library Management System

A web-based Library Management System built using **Python Flask** and **Firebase Firestore**.

The project provides a simple interface to manage library book records through basic CRUD operations such as adding, viewing, updating, and deleting books.

## Overview

The Library Management System is designed to make book record management easier by replacing manual tracking with a simple digital system.

It uses Flask for backend routing and request handling, while Firebase Firestore is used as the cloud database for storing library records.

This project helped me understand Flask-based web development, Firebase integration, CRUD operations, template rendering, and secure handling of application credentials.

## Features

* Add new books to the library
* View available book records
* Update existing book details
* Delete book records
* Store and retrieve data using Firebase Firestore
* Simple and clean web interface
* Basic CRUD functionality
* Secure handling of credentials by avoiding hardcoded secrets

## Tech Stack

* Python
* Flask
* Firebase Firestore
* Firebase Admin SDK
* HTML
* CSS
* JavaScript

## Project Structure

```txt
Library-Management-System/
│
├── app.py
├── migrate_mysql_to_firestore.py
├── templates/
│   ├── index.html
│   ├── add_book.html
│   └── update_book.html
│
├── static/
│   ├── css/
│   └── js/
│
├── requirements.txt
└── README.md
```

## How It Works

The application provides a web interface where library book records can be managed easily.

Flask handles the backend routes and processes user requests.

Firebase Firestore is used as the database to store and manage book records.

HTML, CSS, and JavaScript are used for the frontend interface.

The basic workflow is:

```txt
User Interface
      ↓
Flask Routes
      ↓
Application Logic
      ↓
Firebase Firestore Database
```

## Firebase Setup

To run this project locally, you need to configure Firebase.

1. Create a Firebase project from the Firebase Console.
2. Enable Firestore Database.
3. Generate a Firebase service account key.
4. Store the service account key securely on your local system.
5. Do not commit Firebase credentials or service account files to GitHub.

Example Firebase initialization:

```python
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
```

## How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/your-username/library-management-system.git
```

2. Move into the project folder:

```bash
cd library-management-system
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the virtual environment:

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Add your Firebase service account key securely.

7. Run the Flask application:

```bash
python app.py
```

8. Open the application in your browser:

```txt
http://127.0.0.1:5000
```

## Security Note

Firebase credentials, API keys, service account files, and other secrets should never be committed to GitHub.

Use one of the following safer methods:

* Store credentials locally and add them to `.gitignore`
* Use environment variables
* Use a separate configuration file that is not pushed to GitHub

Example `.gitignore` entries:

```gitignore
serviceAccountKey.json
.env
__pycache__/
venv/
```

## Future Improvements

* Add user authentication
* Add admin and student roles
* Add book issue and return functionality
* Add due date tracking
* Add fine calculation
* Add search and filter options
* Improve UI design
* Add deployment configuration

## Learning Outcomes

Through this project, I learned about:

* Building web applications using Flask
* Creating backend routes
* Rendering HTML templates
* Performing CRUD operations
* Connecting Flask with Firebase Firestore
* Managing project dependencies
* Handling credentials securely
* Structuring a small full-stack web application

## Conclusion

This Library Management System is a basic but useful web application for managing library book records.

It demonstrates the use of Flask for backend development and Firebase Firestore for cloud-based data storage.
