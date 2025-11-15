# Learn.AI Backend API

FastAPI backend server for handling lesson generation requests.

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. (Optional) Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

1. Create a `.env` file in the `backend/` directory (if not already present)

2. Add the following environment variables:
```env
AIRIA_API_KEY=your_api_key_here
AIRIA_API_URL=https://api.airia.ai/v2/PipelineExecution/3da63a17-1f41-4352-891a-40a1bdf7080e
AIRIA_USER_ID=your_user_id_here
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
```

## Running the Server

### Development Mode (with auto-reload):
```bash
uvicorn main:app --reload --port 8000
```

Or:
```bash
python -m uvicorn main:app --reload --port 8000
```

Or directly run the main.py:
```bash
python main.py
```

### Production Mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- **GET** `/` or `/health`
- Returns server status

### Generate Lesson
- **POST** `/generateLesson`
- **Request Body**:
```json
{
  "userInput": "How are clouds formed"
}
```
- **Response**:
```json
{
  "topic": "How are clouds formed",
  "segments": [
    {
      "segment_id": 1,
      "imageUrl": "https://example.com/image.jpg",
      "audioBase64": "UklGRu4AAABXQVZFZm10IBAAAAAB...",
      "prompt": "How are clouds formed: illustrate..."
    }
  ]
}
```

## CORS Configuration

The backend is configured to allow requests from:
- `http://localhost:8080`
- `http://localhost:8081`
- `http://127.0.0.1:8080`
- `http://127.0.0.1:8081`

To add more origins, edit the `allow_origins` list in `main.py`.

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, change it in the `.env` file:
```env
BACKEND_PORT=8001
```

### Module Not Found
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables Not Loading
Ensure the `.env` file is in the `backend/` directory and contains all required variables.

### CORS Errors
Check that your frontend URL matches one of the allowed origins in `main.py`.

## Logging

The server logs all requests and responses. Check the console output for:
- Request details
- API call status
- Response parsing information
- Error details

