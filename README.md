# HireWise

HireWise is a Flask-based web application designed to help students improve their placement readiness through resume analysis, aptitude assessments, interview preparation, and performance tracking. The platform also includes an admin dashboard for managing users, questions, and assessment results.


## Features

### User Module

* User Registration and Login
* Secure Authentication
* Resume Upload and Analysis
* Aptitude Test Assessment
* Interview Question Preparation
* Performance Tracking Dashboard
* Progress Reports and Analytics

### Resume Analyzer

* Upload resumes in PDF format
* Extract text using PyPDF2
* Analyze resume content
* Generate resume score
* Identify missing skills and provide feedback

### Aptitude Assessment

* Randomized aptitude questions
* Automatic evaluation
* Score calculation and storage
* Performance history tracking

### Interview Preparation

* Browse interview questions by category
* Practice technical and HR questions
* Improve interview readiness

### Performance Dashboard

* Resume score overview
* Aptitude test performance tracking
* Visual charts and summary metrics
* Progress monitoring

### Admin Panel

* Admin Authentication
* User Management
* Interview Question Management
* Aptitude Question Management
* Assessment Result Monitoring
* Dashboard Statistics

---

## Technologies Used

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

### Backend

* Python
* Flask

### Database

* MySQL

### Libraries

* PyPDF2
* PyMySQL
* Werkzeug

---

## Project Structure


HireWise/
│
├── app.py
├── config.py
├── uploads/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── aptitude.html
│   ├── performance.html
│   └── admin/
│
└── README.md


---

## Running the Application

Start the Flask server:

python app.py

Open your browser and visit:

http://127.0.0.1:5000/


---

## Default Admin Credentials

Username: admin
Password: admin123

---

## Screenshots

### Admin Dashboard
(Screenshots/admin.png)

### Home Page
(Screenshots/home.png)

### Login Page
(Screenshots/login.png)

### Dashboard
(Screenshots/dashboard.png)

### Resume Analyzer
(Screenshots/resume.png)

### Aptitude Test
(Screenshots/aptitude.png)

### Performance Analyzer
(Screenshots/performance.png)

---

## Future Enhancements

* AI-powered Resume Suggestions
* Job Recommendation System
* Mock Interview Module
* Email Notifications
* Resume ATS Compatibility Checker
* Placement Analytics Dashboard

---

## Author

Amisha Krishnan

MCA Student | Aspiring Software Developer

## Skills

Python • Flask • MySQL • HTML • CSS • Bootstrap • JavaScript

---

## License

This project is developed for educational and portfolio purposes.
