# 🌿 Kanivu Cares

> *"Technology with compassion — empowering communities through digital welfare."*

---

## 📌 About the Project

**Kanivu Cares** is a web-based charity and welfare management system designed for **Kanivu – A Welfare & Charity Unit**.
The platform digitizes and streamlines welfare activities, improving transparency, coordination, and community engagement.

It replaces traditional manual systems (WhatsApp groups, paper records) with a **centralized, secure, and efficient web application**.

---

## 🚀 Features

### 🌍 Public User

* View ongoing and past welfare programs
* Request assistance
* Contact organization
* View announcements & updates

### 👤 Member (Volunteer)

* View member data (read-only)
* Submit financial reports
* Maintain activity/work logs
* Receive notifications

### 🧑‍💼 Coordinator

* Create and manage member accounts (approval-based)
* Manage financial records
* Add/edit aid receiver details (beneficiaries)
* Send announcements & updates

### 🧑‍💼 Convenor

* Approve/reject member registrations
* Assign roles and responsibilities
* Manage events, finance, and beneficiaries
* Oversee all volunteer activities

### ⚙️ Admin

* Full system control
* Manage users and roles
* Monitor system activity
* Maintain platform integrity

---

## 🏗️ Tech Stack

### 💻 Frontend

* HTML5
* CSS3
* JavaScript

### ⚙️ Backend

* Python
* Django Framework

### 🗄️ Database

* SQLite (Development)
* PostgreSQL (Production - Recommended)

---

## 📂 Project Structure (Example)

```
kanivu_cares/
│
├── manage.py
├── kanivu_cares/
│   ├── settings.py
│   ├── urls.py
│
├── users/
├── volunteers/
├── coordinator/
├── convenor/
├── admin_panel/
│
├── templates/
├── static/
└── db.sqlite3
```

---

## 🔐 User Roles & Access Control

| Role        | Permissions              |
| ----------- | ------------------------ |
| Public      | View-only access         |
| Member      | Submit logs & reports    |
| Coordinator | Manage members & records |
| Convenor    | Full operational control |
| Admin       | System-wide control      |

---

## 🧠 Key Modules

* User Authentication System
* Volunteer (Member) Management
* Financial Record Management
* Beneficiary (Aid Receiver) Management
* Notification & Announcement System
* Role-Based Access Control

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/kanivu-cares.git
cd kanivu-cares
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Run Server

```bash
python manage.py runserver
```

---

## 📊 Future Enhancements

* 📍 Geolocation tracking for beneficiaries
* 📱 Mobile app integration
* 🧾 Advanced financial analytics
* 🏆 Volunteer performance tracking
* 🔔 Real-time notifications

---

## 🤝 Contribution

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

This project is developed for educational and social welfare purposes.

---

## 🙌 Acknowledgment

Developed as part of **BCA Final Year Project**
C.H.M.M College for Advanced Studies

---

## 💬 Quote

> *"Small acts, when multiplied by millions of people, can transform the world."*

---
