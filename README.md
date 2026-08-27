<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:8B5CF6,100:06B6D4&height=220&section=header&text=Puddle&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=32&desc=A%20Full-Stack%20E-Commerce%20Platform&descAlignY=55&descSize=22" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=8B5CF6&center=true&vCenter=true&width=650&lines=Browse+%26+shop+products+with+ease;Built-in+customer-seller+messaging;Search+%2B+category+filtering;Full-Stack+Django+%2B+Tailwind+by+Mohammad+Sakib" alt="Typing SVG" />

<br/>

[![Stars](https://img.shields.io/github/stars/nawabsakib5/Ecommerce?style=for-the-badge&color=8B5CF6&labelColor=1a1a2e)](https://github.com/nawabsakib5/Ecommerce/stargazers)
[![Forks](https://img.shields.io/github/forks/nawabsakib5/Ecommerce?style=for-the-badge&color=06B6D4&labelColor=1a1a2e)](https://github.com/nawabsakib5/Ecommerce/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/nawabsakib5/Ecommerce?style=for-the-badge&color=EC4899&labelColor=1a1a2e)](https://github.com/nawabsakib5/Ecommerce/commits/main)
[![Status](https://img.shields.io/badge/status-active%20development-F59E0B?style=for-the-badge&labelColor=1a1a2e)](#-status)

</div>

---

## 🛒 About The Project

**Cado** is a scalable, full-stack **e-commerce platform** built with **Python & Django**, where users can browse and search products, list and manage items for sale, message sellers about products, and manage everything from a personal dashboard. It's designed with secure authentication and a clean, dynamic product-management flow for a seamless shopping experience.

<div align="center">
<img src="https://skillicons.dev/icons?i=python,django,tailwind,sqlite,html,js,git,github&theme=dark" />
</div>

---

## 📚 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [📖 Usage](#-usage)
- [🚧 Status](#-status)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Author](#-author)

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🔐 Secure Authentication
Full registration, login & logout flow built on Django's auth system.

### 🖼️ Product Management
Add, edit, and delete product listings — complete with images, price & category.

### 🔍 Search & Filter
Find products instantly by name, description, or category.

</td>
<td width="50%" valign="top">

### 💬 Customer–Seller Messaging
Built-in conversation system so customers and sellers can chat about products without leaving the platform.

### 📋 Personal Dashboard
Manage all your own listings from a dedicated user dashboard.

### 🎨 Modern UI
Styled with **Tailwind CSS** for a fast, responsive, clean shopping experience.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```mermaid
flowchart LR
    U["👤 User"] --> Auth["🔐 Register / Login"]
    Auth --> Core["🏠 core\nHome & base templates"]
    Auth --> Dash["📋 dashboard\nManage listings"]
    Dash --> Item["🛍️ item\nAdd / Edit / Delete"]
    Item --> Search["🔍 Search & Category Filter"]
    Item --> Conv["💬 conversation\nCustomer ↔ Seller Chat"]
    Conv --> Seller["🧑‍💼 Seller"]
    Conv --> Buyer["🛒 Customer"]
```

---

## 📁 Project Structure

```text
Ecommerce/
└── puddle/
    ├── core/             # Home page & base templates
    ├── item/             # Product listings — add, edit, delete
    ├── conversation/     # Messaging between customers & sellers
    ├── dashboard/        # User dashboard
    ├── templates/        # Shared HTML templates
    ├── puddle/           # Project settings & URLs
    ├── requirements.txt
    └── manage.py
├── Procfile              # Deployment process config
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![Tailwind](https://img.shields.io/badge/-TailwindCSS-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white) |
| **Database** | ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **Auth** | Django built-in authentication |

---

## 🚀 Getting Started

### ✅ Prerequisites
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-Required-F05032?style=flat-square&logo=git&logoColor=white)

### 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/nawabsakib5/Ecommerce.git
cd Ecommerce

# 2. Create & activate a virtual environment
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r puddle/requirements.txt

# 4. Apply migrations
cd puddle
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Open your browser and go to → **`http://127.0.0.1:8000`** 🎉

---

## 📖 Usage

1. 📝 Register a new account or log in
2. 🏷️ List products for sale with images, price & category
3. 🔍 Browse or search products by name or category
4. 💬 Contact sellers via the built-in messaging system
5. 📋 Manage your listings from your personal dashboard

---

## 🚧 Status

> Under active development — new features being added regularly.

---

## 🗺️ Roadmap

- [ ] ⭐ Ratings & reviews for products
- [ ] 💳 In-app payment / checkout flow
- [ ] 🛒 Shopping cart & order history
- [ ] 📱 Mobile-responsive polish
- [ ] 🔔 Real-time chat notifications

---

## 👤 Author

<div align="center">

<img src="https://github.com/nawabsakib5.png" width="100" style="border-radius:50%"/>

**Mohammad Sakib**
BSc in CSE — Habibullah Bahar University College, Bangladesh

[![GitHub](https://img.shields.io/badge/GitHub-nawabsakib5-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nawabsakib5)

</div>

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:06B6D4,100:8B5CF6&height=100&section=footer" width="100%"/>
</div>
