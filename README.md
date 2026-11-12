# TurfTrack – Turf Booking and Management System

TurfTrack is a web-based turf booking and management application developed using Django. It provides a platform where users can explore available sports turfs, book time slots, manage reservations, and interact with turf owners.

## Project Overview

The application simplifies the turf booking process by providing separate functionalities for users, turf owners, and administrators.

## Key Features

- **User Management:** User registration, login, and account management.
- **Turf Discovery:** Browse and explore available sports turfs.
- **Online Booking:** Book available turf time slots.
- **Booking Management:** View booking history and booking confirmations.
- **Turf Owner Dashboard:** Manage turf details, slots, and reservations.
- **Admin Dashboard:** Administrative management of the platform.
- **Payment Management:** Payment-related booking functionality.
- **Reviews and Ratings:** Users can submit reviews and feedback.
- **Job Management:** Job posting and job-related functionality.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| JavaScript | Frontend interactivity |
| SQLite | Database |
| Bootstrap | Responsive UI (if used) |

## Project Structure

```text
TurfTrack/
│
├── turfowner/
├── turftrack/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── views.py
│   └── urls.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/aryanandha-mg/TurfTrack.git
```

### 2. Navigate to the project directory

```bash
cd TurfTrack
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Create an administrator account (optional)

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Open your browser and visit:

`http://127.0.0.1:8000/`

## Future Enhancements

- Integration of secure online payment gateways.
- Improved booking availability and notification systems.
- Enhanced analytics and reporting.
- Mobile-friendly user experience.

## Author

**Aryanandha**

GitHub: [aryanandha-mg](https://github.com/aryanandha-mg)

---

*Developed as a web application project using Python and Django.*
