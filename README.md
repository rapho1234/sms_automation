# SMS Automation

This project automatically sends SMS reminder messages to clients every day at **8:00 AM** using a Python script, a MySQL database, and Linux cron jobs.

The system checks customer subscription expiry dates from the database and sends SMS notifications to customers whose internet service will expire in 2 days.

---

## Features

- Automatic daily SMS reminders
- MySQL database integration
- Cron job scheduling on Ubuntu/Linux
- Automatic phone number formatting
- JSON API integration with TextSMS
- Error handling and logging
- Supports customer account-based reminders

---

## Technologies Used

- Python 3
- MySQL
- Linux Cron Jobs
- TextSMS API
- Requests Library
- MySQL Connector/Python

---

## Project Structure

```bash
sms_automation/
│
├── sms_automation.py
├── keys_sms.py
├── requirements.txt
└── README.md
