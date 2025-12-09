[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)


# Project README

## Description

We made a practical web application that helps businesses organize and manage their daily deliveries with ease. The platform allows admins to create routes, assign drivers and vehicles, and select the right orders for each delivery round. It automatically calculates the total weight of all assigned orders and ensures that the vehicle’s maximum capacity is never exceeded.
This RoutePlanner also optimizes the sequence of stops, making routes shorter and more efficient. Drivers receive a clear overview of their tasks, including customer details, delivery addresses, and the order in which they should complete their stops. This makes it easier for them to follow the route and update progress throughout the day.
The goal of our RoutePlanner is to simplify delivery planning, reduce errors, and create a smoother workflow between the office and drivers on the road.

## Installation & Usage

How to run the app locally
* 1. Create and activate a virtual environment
     
     Windows:
     python -m venv venv
     venv\Scripts\activate
     
     MacOs:
     python3 -m venv venv
     source venv/bin/activate
     
  * Render link:
     https://web-application-2025-group-5.onrender.com/login
     
* 2. Install dependencies:
    pip install -r requirements.txt

* 3. Create a .env file in the project root
* 4. Start the application:
     python3 run.py
* 5. Open the app in your browser:
     http://127.0.0.1:5000/

## UI Prototype

* https://route-wizard-37.lovable.app

## Kanban Board

* https://www.canva.com/design/DAG6jw5qEkM/5FUxDVmcyR5h0UMez4I5qQ/edit?utm_content=DAG6jw5qEkM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Feedback Sessions

* Link to sprint 1: https://ugentbe-my.sharepoint.com/:v:/g/personal/victorien_vermeersch_ugent_be/Edi2W6wGy7JMpKB3N8SnxFYBPhff8iLoWZdP1yW2dYCQpg?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=k76rMe
* Link to sprint 2: https://ugentbe-my.sharepoint.com/:v:/g/personal/victorien_vermeersch_ugent_be/EcVaoNV888hKsiFzgrlSL0sBXaIhPaxLhvwppNbgLfrMjw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&email=Thomas.Derave%40UGent.be&e=QGRxHX 

## Project Structure
```txt
routeplanner/
├── app/
│   ├── __pycache__/
│   │
│   ├── templates/
│   │   ├── admin_dashboard.html
│   │   ├── base.html
│   │   ├── driver_dashboard.html
│   │   ├── login.html
│   │   ├── order_create.html
│   │   ├── order_edit.html
│   │   ├── route_assign.html
│   │   ├── route_create.html
│   │   ├── user_create.html
│   │   └── vehicle_create.html
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── admin_routes.py
│   │   ├── auth_routes.py
│   │   ├── driver_routes.py
│   │   └── preview_routes.py
│   │
│   ├── Database/
│   ├── migrations/
│   │
│   ├── models.py
│   ├── config.py
│   └── admin_routes.py
│
├── scripts/
│
├── requirements.txt
├── README.md
├── run.py
└── .gitignore
```


## Additional information





