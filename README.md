# Fashion Inventory Management System (FIMS)

A solution for managing **inventory, sales, and analytics** for fashion retailers.  
This system is built with **Python (PyQt5)** and uses **SQLite** for data storage.

---

## Table of Contents
- [Introduction](#-introduction)  
- [System Requirements](#-system-requirements)  
- [Features](#-features)  
  - [User Authentication](#user-authentication)  
  - [Inventory Management](#inventory-management)  
  - [Sales Processing](#sales-processing)  
  - [Reporting & Analytics](#reporting--analytics)  
  - [Data Export](#data-export)  
- [User Interface](#-user-interface)  
- [Database](#-database)  
- [Security Features](#-security-features)  
- [Future Enhancements](#-future-enhancements)  
- [Conclusion](#-conclusion)  

---

## Introduction
The **Fashion Inventory Management System (FIMS)** provides retailers with tools to:
- Track and manage inventory  
- Process sales in real-time  
- Analyze sales and inventory trends  
- Export and share data  

---

## System Requirements
- **Python** 3.7+  
- **PyQt5** 5.15.6  
- **matplotlib** 3.5.2  
- **SQLite3** (bundled with Python)

---

## Features

### User Authentication
- Secure login with hashed passwords  
- Role-based access control *(Manager, Inventory Manager, Sales Staff)*  
- Manager-only user creation  

### Inventory Management
- Add, view, and update product information  
- Manage categories & brands  
- Set low-stock thresholds with automatic alerts  

### Sales Processing
- Process sales transactions  
- Generate customer bills  
- Auto-update inventory after each sale  

### Reporting & Analytics
- Sales reports *(daily, weekly, monthly)*  
- Inventory reports & analysis  
- Top-selling item tracking  
- Inventory turnover metrics  
- Sales trend visualization with graphs  

### Data Export
- Export inventory data to **CSV format**

---

## User Interface
- Intuitive **tab-based design**  
- Built with **PyQt5**  
- Color-coded UI for better usability  

---

## Database
- **SQLite** for data storage  
- Tables: `products`, `brands`, `sales`, `users`  

---

## Security Features
- Password hashing with **SHA-256**  
- Role-based access control  


