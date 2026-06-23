# 🚀 Full-Stack Flask Blog & Community Platform

🌍 **Live Demo:** [View the Live Website on Render](https://upgraded-blog-blog-post-capstone.onrender.com/)

A robust, fully functional multi-user blog application built with Python and Flask. Originally a personal portfolio, this project has been scaled into a community platform featuring a complete CRUD content management system, role-based access control, secure user authentication, interactive commenting, and a dynamic contact form.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

## ✨ Key Features

* **Cloud Infrastructure:** Fully deployed on **Render** with a serverless **PostgreSQL** database hosted by **Neon**, featuring custom retry logic to handle cold starts gracefully.
* **User Authentication & Authorization:** Secure registration and login system utilizing **Werkzeug** for password hashing and **Flask-Login** for session management.
* **Role-Based Access Control (RBAC):** Tiered permissions separating Super Admins, Moderators, Authors, and standard Users, dictating who can create, edit, or delete specific posts and comments.
* **Relational Database Architecture:** Engineered using SQLAlchemy ORM with bi-directional One-to-Many relationships mapping Users to Posts, Users to Comments, and Posts to Comments, fully utilizing cascading deletes.
* **Interactive Community Features:**
  * Rich-text commenting system hidden behind a smooth JavaScript UI toggle.
  * Integration with **Gravatar** to automatically fetch and display user avatars.
* **Complete CRUD System:** Seamlessly create, read, update, and delete blog posts directly from the web interface using **CKEditor** for professional article formatting.
* **Robust Security Architecture:**
  * **XSS Protection:** Implemented backend sanitization using **Bleach** to scrub malicious `<script>` injections from rich-text inputs before they hit the database.
  * **Anti-Enumeration:** Unified login failure handling to prevent username enumeration attacks.
  * **Data Validation:** Utilized **WTForms** to enforce strict backend validation on all user inputs.
* **Responsive UI:** Fully styled using **Bootstrap 5**, **bootstrap-flask**, and Jinja templating, ensuring a flawless experience on both desktop and mobile devices.

## 🛠️ Technologies Used

* **Backend:** Python 3, Flask, Flask-Login
* **Database:** PostgreSQL (Production via Neon), SQLite (Local Testing), SQLAlchemy (ORM)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Jinja2, Bootstrap 5, bootstrap-flask
* **Security & Utilities:** Werkzeug (Cryptography), Flask-WTF (Form Handling), Bleach (Sanitization), Python-dotenv, smtplib

## 📂 Project Structure

```text
├── .env                 # Environment variables (Ignored by Git)
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Python project metadata and dependencies
├── uv.lock              # Lockfile for dependency management
├── main.py              # Application factory and routing logic
├── admin.py             # Administrative routing and logic
├── extensions.py        # Flask extensions initialization
├── forms.py             # WTForms class definitions
├── models.py            # SQLAlchemy database schemas
├── utils.py             # Utility functions and helpers
├── instance/
│   └── posts.db         # SQLite Database (Local Dev Only)
├── static/
│   ├── assets/          # Images and favicon
│   ├── css/             # Stylesheets
│   └── js/              # Frontend scripts
└── templates/
    ├── 403.html         # Custom forbidden error page
    ├── about.html       # Biography page
    ├── admin_portal.html# Dashboard for administrative controls
    ├── contact.html     # Contact form page
    ├── footer.html      # Reusable footer
    ├── header.html      # Reusable navigation/head with Flash messaging
    ├── index.html       # Home page (Blog feed)
    ├── login.html       # User authentication
    ├── register.html    # User registration
    ├── make-post.html   # Create/Edit post form
    └── post.html        # Single article view & comment section

```

## 🚀 Installation & Setup

Follow these steps to run the application locally.

### 1. Clone the repository

```bash
git clone [https://github.com/Joshuaongith/your-repo-name.git](https://github.com/Joshuaongith/your-repo-name.git)
cd your-repo-name

```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install Flask Flask-SQLAlchemy Flask-WTF Flask-CKEditor Flask-Login bootstrap-flask bleach werkzeug python-dotenv

```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add the following keys. (Do not use quotation marks around the values).

```env
SECRET_KEY=your_secure_random_key
MY_EMAIL=your_sending_email@gmail.com
MY_PASSWORD=your_app_password
RECEIVER_EMAIL=your_receiving_email@gmail.com
DB_URL=sqlite:///posts.db 

```

*Note: To connect to a live database instead of local SQLite, replace the `DB_URL` value with your PostgreSQL connection string. If using Gmail for contact forms, you must generate an [App Password](https://support.google.com/accounts/answer/185833?hl=en) to use as `MY_PASSWORD`.*

### 5. Run the Application

```bash
python main.py

```

The server will start on `http://127.0.0.1:5000/`. If using the local SQLite setup, the database (`posts.db`) and all relational tables will automatically generate inside the `instance` folder upon the first run.

### 6. 🧪 Optional: Inject Sample Data

To test the application immediately without manually creating users and posts, you can populate the database with dummy data. Create a file named `seed_data.py` in the root directory, paste the following code, and run it once:

```python
from main import app
from extensions import db
from models import User, BlogPost, Comment
from werkzeug.security import generate_password_hash
from datetime import date

with app.app_context():
    # 1. Create an Admin User
    hashed_pwd = generate_password_hash("password123", method="pbkdf2:sha256", salt_length=8)
    admin_user = User(email="admin@test.com", password=hashed_pwd, name="Admin User", is_admin=True)
    db.session.add(admin_user)
    db.session.commit()

    # 2. Create a Sample Blog Post
    sample_post = BlogPost(
        title="Welcome to the Community",
        subtitle="This is a beautifully formatted sample post.",
        date=date.today().strftime("%B %d, %Y"),
        body="<p>This is the main body of the blog post. CKEditor allows for <strong>bold text</strong>, <em>italics</em>, and <a href='#'>hyperlinks</a>.</p>",
        img_url="[https://images.unsplash.com/photo-1499750310107-5fef28a66643](https://images.unsplash.com/photo-1499750310107-5fef28a66643)",
        author=admin_user
    )
    db.session.add(sample_post)
    db.session.commit()

    # 3. Create a Sample Comment
    sample_comment = Comment(
        text="<p>This is a test comment from the admin!</p>",
        comment_author=admin_user,
        parent_post=sample_post
    )
    db.session.add(sample_comment)
    db.session.commit()

    print("✅ Sample data successfully injected!")

```

Run the script using: `python seed_data.py`. You can now log in using `admin@test.com` and `password123`.

## 🏆 Acknowledgments & Credits

This project was brought to life with the combination of excellent educational resources, powerful tools, and modern frameworks.

* **Curriculum & Foundation**
* **Udemy:** The core project concept, starting HTML/CSS templates, and foundational architecture were provided as part of Dr. Angela Yu's *100 Days of Code: The Complete Python Pro Bootcamp*. The multi-user database relations, role-based access control, security hardening, and interactive community features were custom-built to expand significantly upon the original curriculum.


* **Tools & Development**
* **IDE:** Entirely coded, built, and debugged using PyCharm by JetBrains.
* **AI Pair Programming:** Architecture brainstorming, security hardening (including anti-enumeration and Bleach sanitization), UI/UX standardization, cloud deployment infrastructure, and advanced code documentation were assisted by Google Gemini, acting as a virtual senior engineering mentor.
* **Tech Stack:** Powered by Python, Flask, SQLAlchemy, Werkzeug, Flask-Login, Bootstrap-Flask, and Neon Serverless Postgres.



## 👨‍💻 Author

**Joshua Uzochukwu**

* [LinkedIn](https://www.linkedin.com/in/joshua-uzochukwu-5a7637299/)
* [GitHub](https://github.com/Joshuaongith)
* [X (Twitter)](https://x.com/JoshuaUzochukw8)

---

*Developed as a comprehensive capstone project focusing on full-stack architecture, secure data pipelines, relational database management, and responsive UI design.*
