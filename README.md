<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,50:EA580C,100:0F172A&height=230&section=header&text=CADO%20FASHION&fontSize=50&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Shop%20Smarter%2C%20Save%20Bigger&descAlignY=58&descSize=20" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=21&pause=1000&color=EA580C&center=true&vCenter=true&width=680&lines=Full-stack+fashion+e-commerce+platform;Deals+from+verified+sellers+across+Bangladesh;Cart%2C+wishlist%2C+reviews+%26+real-time+messaging;Built+with+Django+by+Mohammad+Sakib" alt="Typing SVG" />

<br/>

[![Live Site](https://img.shields.io/badge/Live%20Demo-ecommerce--iyil.onrender.com-EA580C?style=for-the-badge&logo=render&logoColor=white)](https://ecommerce-iyil.onrender.com)
[![Stars](https://img.shields.io/github/stars/nawabsakib5/Ecommerce?style=for-the-badge&color=F59E0B&labelColor=1a1a2e)](https://github.com/nawabsakib5/Ecommerce/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/nawabsakib5/Ecommerce?style=for-the-badge&color=8B5CF6&labelColor=1a1a2e)](https://github.com/nawabsakib5/Ecommerce/commits/main)
[![Status](https://img.shields.io/badge/status-active%20development-10B981?style=for-the-badge&labelColor=1a1a2e)](#-status)

</div>

---

## 🛍️ About The Project

**Cado Fashion** (repo: `Ecommerce`) is a full-stack **fashion e-commerce platform** built with **Python & Django** — originally started as *Puddle*, a second-hand marketplace prototype, and iteratively evolved into a full retail storefront for verified sellers across Bangladesh. Customers can browse curated categories (Men's, Baby items, Children's Drop Shoulders, Clothing, Adults Drop Shoulders), search products, add items to a cart or wishlist, leave reviews, message sellers in real time, and sellers get their own dashboard with **Chart.js**-powered analytics.

<div align="center">
<img src="https://skillicons.dev/icons?i=python,django,tailwind,postgresql,js,html,git,github,render&theme=dark" />
</div>

---

## 📚 Table of Contents

- [🖥️ Preview](#️-preview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [⚙️ Environment Variables](#️-environment-variables)
- [☁️ Deployment](#️-deployment)
- [🔒 Security](#-security)
- [🗺️ Roadmap](#️-roadmap)
- [👤 Author](#-author)

---

## 🖥️ Preview

<div align="center">

| Home / Storefront |
|:---:|
| Hero banner, category quick-filters, live search, "Just Dropped" & "Trending Now" panels, and a latest-items feed — all in a clean, dark-accented storefront UI. |

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🏬 Storefront & Browsing
Hero promo banners, category quick-filter chips (Men's, Baby, Kids, Clothing), and a live search bar across products, brands & categories.

### 🛒 Cart & Wishlist
Add products to cart or save them to a wishlist for later.

### ⭐ Reviews
Customers can leave reviews on purchased or listed products.

### 🔔 Notifications & Inbox
In-app notification bell + real-time messaging between buyers and sellers.

</td>
<td width="50%" valign="top">

### 📦 Seller Tools
"+ Add Item" flow for sellers to list products, plus bulk-upload support via a custom Django management command that pushes images/videos straight to **Cloudinary**.

### 📊 Analytics Dashboard
Seller dashboard with **Chart.js**-powered sales/activity visualizations.

### 👥 Buyer / Seller Roles
Role-aware access — separate flows for people browsing vs. people listing products.

### 🔐 Secure Auth
Full login / logout / dashboard access control.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```mermaid
flowchart LR
    U["👤 Customer"] --> Auth["🔐 Login / Register"]
    Auth --> Home["🏠 Storefront\nHero + Categories + Search"]
    Home --> Item["🛍️ Product Listings"]
    Item --> Cart["🛒 Cart"]
    Item --> Wish["💛 Wishlist"]
    Item --> Rev["⭐ Reviews"]
    Item --> Conv["💬 Real-time Messaging"]
    S["🧑‍💼 Seller"] --> Add["➕ Add Item\n(Bulk Upload)"]
    Add --> Cloud[("☁️ Cloudinary\nMedia Storage")]
    S --> Dash["📊 Seller Dashboard\nChart.js Analytics"]
    Conv --> S
    Home --> Notif["🔔 Notifications"]
    subgraph Deploy["Production"]
        Gun["🦄 Gunicorn"] --> WN["📦 WhiteNoise\nStatic Files"]
        Gun --> DB[("🗄️ PostgreSQL")]
    end
    Home -.-> Gun
```

---

## 📁 Project Structure

```text
Ecommerce/
└── puddle/                # Root directory (deployed on Render)
    ├── core/               # Home page & base templates
    ├── item/               # Product listings — add, edit, delete, bulk upload
    ├── conversation/       # Real-time buyer–seller messaging
    ├── dashboard/          # Seller dashboard + Chart.js analytics
    ├── templates/          # Shared HTML templates
    ├── puddle/             # Django project settings & URLs
    ├── requirements.txt
    └── manage.py
├── Procfile                # Gunicorn start command for deployment
├── .gitignore               # Hardened after full security audit
└── requirements.txt
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white) ![Gunicorn](https://img.shields.io/badge/-Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![Tailwind](https://img.shields.io/badge/-TailwindCSS-38BDF8?style=flat-square&logo=tailwindcss&logoColor=white) ![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![Chart.js](https://img.shields.io/badge/-Chart.js-FF6384?style=flat-square&logo=chartdotjs&logoColor=white) |
| **Media Storage** | ![Cloudinary](https://img.shields.io/badge/-Cloudinary-3448C5?style=flat-square&logo=cloudinary&logoColor=white) |
| **Static Files** | ![WhiteNoise](https://img.shields.io/badge/-WhiteNoise-000000?style=flat-square) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| **Hosting** | ![Render](https://img.shields.io/badge/-Render-46E3B7?style=flat-square&logo=render&logoColor=white) |

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

## ⚙️ Environment Variables

Create a `.env` file inside `puddle/` — never commit this file:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=your-database-url
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## ☁️ Deployment

<div align="left">
<img src="https://img.shields.io/badge/Render-Live-46E3B7?style=for-the-badge&logo=render&logoColor=white" />
</div>

Live at **[ecommerce-iyil.onrender.com](https://ecommerce-iyil.onrender.com)** — deployed on **Render** with:
- Root directory set to `puddle`
- **Gunicorn** as the production WSGI server
- **Cloudinary** for all product image/video storage
- **WhiteNoise** for serving static files

> Originally deployed on Railway; migrated to Render after Railway's free tier expired. A future move to a self-hosted home server is planned.

---

## 🔒 Security

A full security audit was performed on this repository:
- ✅ Removed all hardcoded secrets from source
- ✅ Cleaned git history with `git filter-repo`
- ✅ Added a proper, hardened `.gitignore`
- ✅ Secrets now loaded exclusively via environment variables

---

## 🗺️ Roadmap

- [ ] 💳 Full checkout & payment gateway integration
- [ ] 📦 Order tracking & history
- [ ] ⭐ Verified seller badges
- [ ] 📱 Mobile app companion
- [ ] 🏠 Migrate hosting to self-hosted home server

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
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,50:EA580C,100:0F172A&height=100&section=footer" width="100%"/>
</div>
