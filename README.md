# The D2D Backend Project

The `d2d-backend` powers the backend services for the D2D CRM mobile app, a tool designed to help door-to-door sales reps track leads, manage customer interactions, and log field activity efficiently.

## 🚀 Purpose

This backend provides a simple, scalable foundation for:

- User account creation and login  
- Data storage for prospects, knocks, and trips  
- API endpoints for syncing mobile data with the server  
- Cross-origin support for iOS frontend access  

## 🛠 Architecture

- **Framework:** [Flask](https://flask.palletsprojects.com/) (Python microframework)  
- **API Style:** RESTful JSON  
- **CORS:** Enabled via `flask-cors` to support mobile client communication  
- **Storage:** In-memory user store (temporary; future upgrade to persistent database planned)  
- **Deployment:** Containerized with Docker + Docker Compose  

### Example Endpoints

- `POST /signup` – Register a new user  
- `POST /login` – Authenticate a user  
- `GET /users` – List all users (temporary/debug endpoint)  

## 🐳 Running Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/yourusername/d2d-backend.git
   cd d2d-backend
   docker-compose up --build
   docker-compose down -v