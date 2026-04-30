# 🛒 Puddle — Second-hand Marketplace

A full-stack e-commerce marketplace built with **Python & Django** where users can buy and sell second-hand items, communicate with sellers, and manage their own listings.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat&logo=django)
![HTML](https://img.shields.io/badge/HTML-44.5%25-orange?style=flat&logo=html5)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38bdf8?style=flat&logo=tailwindcss)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat&logo=sqlite)

---

## Features

- User registration, login & logout
- Add, edit and delete item listings with images
- Search items by name or description
- Filter items by category
- Built-in messaging system between buyers and sellers
- User dashboard to manage own listings

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Django |
| Frontend | HTML, Tailwind CSS |
| Database | SQLite |
| Authentication | Django built-in auth |

---

## Project Structure

```
Ecommerce/
└── puddle/
    ├── core/             # Home page & base templates
    ├── item/             # Item listings — add, edit, delete
    ├── conversation/     # Messaging between buyers & sellers
    ├── dashboard/        # User dashboard
    ├── templates/        # Shared HTML templates
    ├── puddle/           # Project settings & URLs
    ├── requirements.txt
    └── manage.py
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/nawabsakib5/Ecommerce.git
cd Ecommerce

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# Install dependencies
pip install -r puddle/requirements.txt

# Run migrations
cd puddle
python manage.py migrate

# Start the development server
python manage.py runserver
```

Open your browser and go to → `http://127.0.0.1:8000`

---

## Usage

1. Register a new account or log in
2. Post items for sale with images, price & category
3. Browse or search items by name or category
4. Contact sellers via the built-in messaging system
5. Manage your listings from your personal dashboard

---

## Status

> 🚧 Under active development — new features being added regularly.

---

## Author

**Mohammad Sakib**
BSc in CSE — Habibullah Bahar University College, Bangladesh
[GitHub](https://github.com/nawabsakib5)
