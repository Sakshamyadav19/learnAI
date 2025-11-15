# Welcome to your Lovable project

## Project info

**URL**: https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
npm run dev

# Step 5 (Optional): Set up and run the backend API server
cd backend
pip install -r requirements.txt
# Create .env file with API credentials (see backend/README.md)
uvicorn main:app --reload --port 8000
```

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with .

**Frontend:**
- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

**Backend:**
- FastAPI (Python)
- Uvicorn (ASGI server)
- httpx (HTTP client)

## Backend Setup

This project includes a FastAPI backend for handling lesson generation API calls.

1. **Navigate to backend directory:**
   ```sh
   cd backend
   ```

2. **Install Python dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Create `.env` file** (already created with default values, or create new):
   ```env
   AIRIA_API_KEY=your_api_key
   AIRIA_API_URL=https://api.airia.ai/v2/PipelineExecution/...
   AIRIA_USER_ID=your_user_id
   BACKEND_PORT=8000
   ```

4. **Run the backend server:**
   ```sh
   uvicorn main:app --reload --port 8000
   ```

For detailed backend setup instructions, see [backend/README.md](backend/README.md).

## Development Workflow

1. Start the backend server (port 8000):
   ```sh
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. Start the frontend dev server (port 8080) in a separate terminal:
   ```sh
   npm run dev
   ```

3. Frontend will call `http://localhost:8000/generateLesson` for lesson generation

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/35d72d2e-6e25-40e5-9b0c-c0d1a7c1b727) and click on Share -> Publish.

## I want to use a custom domain - is that possible?

We don't support custom domains (yet). If you want to deploy your project under your own domain then we recommend using Netlify. Visit our docs for more details: [Custom domains](https://docs.lovable.dev/tips-tricks/custom-domain/)
