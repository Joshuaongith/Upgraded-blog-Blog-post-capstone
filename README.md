
# 🚀 Full-Stack Flask Blog

A robust, fully functional personal portfolio and blog application built with Python and Flask. This project features a complete CRUD (Create, Read, Update, Delete) content management system, secure rich-text formatting, and a dynamic contact form.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)

## ✨ Features

* **Complete CRUD System:** Seamlessly create, read, update, and delete blog posts directly from the web interface.
* **Rich-Text Content Creation:** Integrated **CKEditor** allows for professional article formatting, including headers, typography, and embedded elements.
* **Robust Security:** * **XSS Protection:** Implemented backend sanitization using **Bleach** to scrub malicious `<script>` injections before data reaches the database.
  * **Data Validation:** Utilized **WTForms** to enforce strict backend validation on all user inputs.
* **Dynamic Contact System:** A secure contact form that transmits validated user messages directly to an inbox via `smtplib` over SMTP_SSL.
* **Responsive UI:** Fully styled using **Bootstrap 5** and Jinja templating, ensuring a flawless experience on both desktop and mobile devices.

## 🛠️ Technologies Used

* **Backend:** Python 3, Flask
* **Database:** SQLite, SQLAlchemy (ORM)
* **Frontend:** HTML5, CSS3, Jinja2, Bootstrap 5
* **Security & Utilities:** Flask-WTF (Form Handling), Bleach (Sanitization), Python-dotenv (Environment Variables), smtplib

## 📂 Project Structure

```text
├── .env                 # Environment variables (Ignored by Git)
├── .gitignore           # Git ignore rules
├── main.py              # Application factory and routing logic
├── instance/
│   └── posts.db         # SQLite Database
├── static/
│   ├── assets/          # Images and favicon
│   ├── css/             # Stylesheets
│   └── js/              # Frontend scripts
└── templates/
    ├── about.html       # Biography page
    ├── contact.html     # Contact form page
    ├── footer.html      # Reusable footer
    ├── header.html      # Reusable navigation/head
    ├── index.html       # Home page (Blog feed)
    ├── make-post.html   # Create/Edit post form
    └── post.html        # Single article view

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
pip install Flask Flask-Bootstrap Flask-SQLAlchemy Flask-WTF Flask-CKEditor bleach python-dotenv

```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add the following keys. (Do not use quotation marks around the values).

```env
SECRET_KEY=your_secure_random_key
MY_EMAIL=your_sending_email@gmail.com
MY_PASSWORD=your_app_password
RECEIVER_EMAIL=your_receiving_email@gmail.com

```

*Note: If using Gmail, you must generate an [App Password](https://support.google.com/accounts/answer/185833?hl=en) to use as `MY_PASSWORD`.*

### 5. Run the Application

```bash
python main.py

```

The server will start on `http://127.0.0.1:5003/`. The SQLite database (`posts.db`) will automatically generate inside the `instance` folder upon the first run.

## 👨‍💻 Author

**Joshua Uzochukwu**

* [LinkedIn](https://www.linkedin.com/in/joshua-uzochukwu-5a7637299/)
* [GitHub](https://github.com/Joshuaongith)
* [X (Twitter)](https://x.com/JoshuaUzochukw8)

---

*Developed as a capstone project focusing on full-stack architecture, secure data pipelines, and responsive UI design.*

```

```
