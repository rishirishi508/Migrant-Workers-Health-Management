# Migrant-Workers-Health-Management
A Dockerized healthcare management platform designed to securely store, manage, and access migrant workers’ medical records across different locations with ease and reliability.
🚀 Overview

Migrant workers often face difficulties in maintaining continuous medical records due to frequent relocation. This system provides a secure, portable, and scalable solution that ensures healthcare data is always accessible when needed.

✨ Key Features

🧑‍🔧 Worker registration with unique ID and QR code

📄 Downloadable digital health card (PDF)

🏥 Doctor portal with OTP-based secure access

🚨 Emergency “Break Glass” access with audit logging

🔐 Secure authentication with password hashing

📊 Admin dashboard with system insights and logs

🤖 AI-powered health assistant (local model integration)

🐳 Fully containerized using Docker

🐳 Docker Support

This project is fully containerized for seamless deployment:

Ensures consistent environments across development and production

Simplifies setup with multi-container architecture (Flask + MySQL)

Easy to scale and deploy

🛠️ Tech Stack

Backend: Flask (Python)

Database: MySQL

AI Integration: Hugging Face Transformers (TinyLlama)

Other Tools: QR Code Generator, PDF Generator

Containerization: Docker

📂 Project Structure
├── app.py
├── templates/
├── static/
├── utils/
│   └── pdf_generator.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
⚙️ Installation & Setup
🔹 Using Docker (Recommended)
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git

# Navigate to project folder
cd your-repo-name

# Build and run containers
docker-compose up --build
🔹 Manual Setup (Without Docker)
pip install -r requirements.txt
python app.py
🔐 Security Features

Password hashing using Werkzeug

OTP-based verification for doctor access

Audit logs for all sensitive actions

Emergency access tracking

🎯 Problem Statement

Migrant workers lack a centralized system to maintain their health records, leading to:

Loss of medical history

Delayed or improper treatment

Poor healthcare coordination

✅ Solution

This system provides a portable digital health record system that:

Ensures data availability anywhere

Maintains security and privacy

Enables quick access during emergencies

📌 Future Enhancements

Mobile application support

Multi-language interface

Government health scheme integration

Advanced AI health insights

🤝 Contribution

Contributions are welcome!
Feel free to fork this repository and submit a pull request.

📜 License

This project is licensed under the MIT License.
