# Legal Aid Assistant

A Cyber-aesthetic AI Legal Assistant featuring a secure login system and an interactive dashboard.

## Prerequisites
Before running the project, ensure you have the following installed:

### 1. Python 3.8+ (For Backend)
- **Download**: [python.org](https://www.python.org/downloads/)
- **Verify**: Run `python3 --version` in your terminal.

### 2. Node.js 18+ (For Frontend)
- **Download**: [nodejs.org](https://nodejs.org/) (LTS Version recommended)
- **Verify**: Run `node --version` in your terminal.

### 3. Git
- **Download**: [git-scm.com](https://git-scm.com/downloads)
- **Verify**: Run `git --version` in your terminal.

## Installation & Setup

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone <repository-url>
cd Legal-Aid-Assistant
```

### 2. Backend Setup (FastAPI)
Navigate to the project root and install Python dependencies:
```bash
# Create a virtual environment (Optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pyrebase4 requests
```

### 3. Frontend Setup (React + Vite)
Navigate to the frontend directory and install Node dependencies:
```bash
cd frontend-react
npm install
```

## Running the Application
You need to run **both** the backend and frontend terminals simultaneously.

### Terminal 1: Start Backend Server
This runs the API on **Port 8000**.
```bash
# Make sure you are in the root 'Legal-Aid-Assistant' folder
uvicorn login.authapi:app --reload --port 8000
```
*You should see: `Uvicorn running on http://127.0.0.1:8000`*

### Terminal 2: Start Frontend Server
This runs the React App on **Port 5173**.
```bash
# Make sure you are in 'Legal-Aid-Assistant/frontend-react'
cd frontend-react
npm run dev
```
*You should see: `Local: http://localhost:5173/`*

## Accessing the App
Once both terminals are running, open your browser and go to:
👉 **http://localhost:5173**

## Features
- **Cyber Login UI**: Particle network background and glassmorphism design.
- **Secure Auth**: Powered by Firebase and FastAPI.
- **Dashboard**: Legal facts, FAQs, and chat history.
- **Navigation**: Seamless flow from Login -> Home -> Chat.
