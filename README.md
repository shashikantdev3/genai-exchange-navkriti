# 🚀 Navkriti: AI-Powered Healthcare Test Case Generator

[](https://vision.hack2skill.com/event/genaiexchangehackathon)
**Challenge:** Automating Test Case Generation with AI
**Team:** Navkriti

This repository contains the full-stack application for the Navkriti project, an AI-driven platform that intelligently converts healthcare software requirements into structured, compliant, and audit-ready test cases.

-----

## \#\# 🌟 Vision

To deliver an AI-driven platform that minimizes manual effort, accelerates test case generation, and ensures every test case is tracked, versioned, and validated with compliance by design.

-----

## \#\# 🏗️ Architecture & Tech Stack

This project uses a modern, scalable architecture leveraging Google Cloud services.

  * **Frontend**: A dynamic single-page application built with **React** and **Material-UI (MUI)**.
  * **Backend**: An asynchronous API built with **Python** and the **FastAPI** framework.
  * **AI Engine**: **Google's Gemini model** accessed via the **Vertex AI** platform.
  * **Databases**:
      * **Google Cloud Firestore**: For storing generated test cases and audit trail logs.
      * **Google BigQuery**: For scalable, long-term storage and maintaining a requirements traceability matrix.
  * **Cloud Storage**: **Google Cloud Storage** for securely storing uploaded requirements documents.
  * **Authentication**: **Google Cloud Service Account** using Application Default Credentials (ADC).

-----

## \#\# ⚙️ How to Set Up and Run the Project

Follow these steps to get the full-stack application running on your local machine.

### \#\#\# 1. Pre-requisites

Before you begin, ensure you have the following:

  * **Google Cloud Project**: A GCP project with billing enabled.
  * **Node.js and npm**: For running the React frontend.
  * **Python 3.10+ and pip**: For running the FastAPI backend.
  * **gcloud CLI**: Authenticated with your Google Cloud account (`gcloud auth application-default login`).
  * **Service Account Key**: A JSON key file for a service account with the necessary permissions.

### \#\#\# 2. Enable Required Google Cloud APIs

For your project to function, you must enable the following APIs in your Google Cloud project console:

  * **Vertex AI API**: For accessing the Gemini models.
  * **Generative Language API**: A dependency for the AI functionalities.
  * **BigQuery API**: For database operations.
  * **Cloud Storage API**: For file uploads.
  * **Firestore API**: For the NoSQL database.

### \#\#\# 3. Backend Setup

The backend server powers the AI generation and data management.

1.  **Navigate to the backend directory**:

    ```bash
    cd backend
    ```

2.  **Create and Activate a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```

3.  **Place Your Service Account Key**:

      * Create a folder named `keys` inside the `backend` directory.
      * Place your downloaded `serviceAccountKey.json` file inside the `backend/keys/` folder.

4.  **Set Up Environment Variables**:

      * Create a new file named `.env` in the `backend` directory.
      * Copy and paste the following content into it, replacing the placeholder values with your actual project details.

    <!-- end list -->

    ```ini
    # backend/.env

    # Your Google Cloud Project ID
    FIREBASE_PROJECT_ID="your-gcp-project-id"
    BIGQUERY_PROJECT_ID="your-gcp-project-id"
    GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # Your Firebase Storage Bucket URL (e.g., your-project-id.appspot.com)
    FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"

    # The model name you want to use
    GEMINI_MODEL="gemini-1.5-flash-latest"

    # This tells all Google libraries where to find your key file
    GOOGLE_APPLICATION_CREDENTIALS="keys/serviceAccountKey.json"
    ```

5.  **Install Python Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

6.  **Run the Backend Server**:

    ```bash
    uvicorn main:app --reload
    ```

    The backend will be running at `http://127.0.0.1:8000`.

### \#\#\# 4. Frontend Setup

The frontend provides the user interface for interacting with the application.

1.  **Navigate to the root project directory** (if you are in the `backend` folder, go up one level).

2.  **Install Node.js Dependencies**:

    ```bash
    npm install
    ```

3.  **Set Up Environment Variables**:

      * The frontend code (`firebase.js`) will read environment variables starting with `REACT_APP_`.
      * Create a new file named `.env` in the **root** project directory.
      * Add your Firebase project configuration to it. You can get these details from your Firebase project settings.

    <!-- end list -->

    ```
    # Root .env file for React

    REACT_APP_FIREBASE_API_KEY="your-firebase-api-key"
    REACT_APP_FIREBASE_AUTH_DOMAIN="your-project-id.firebaseapp.com"
    REACT_APP_FIREBASE_PROJECT_ID="your-project-id"
    REACT_APP_FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
    REACT_APP_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
    REACT_APP_FIREBASE_APP_ID="your-app-id"
    ```

4.  **Run the Frontend Development Server**:

    ```bash
    npm start
    ```

    The frontend will be running at `http://localhost:3000`.

-----

## \#\# ✨ Features & API Endpoints

The platform provides a seamless workflow for test case generation, management, and auditing.

| Feature                 | API Endpoint               | Method | Description                                                               |
| ----------------------- | -------------------------- | ------ | ------------------------------------------------------------------------- |
| **Upload Document** | `/upload`                  | `POST` | Uploads a requirements document (PDF, DOCX, TXT) to Cloud Storage.        |
| **Generate Test Cases** | `/generate`                | `POST` | Extracts text and generates test cases from the document using Vertex AI. |
| **View Traceability** | `/traceability`            | `GET`    | Retrieves the requirements-to-test-cases matrix from BigQuery.            |
| **View Audit Trail** | `/audit`                   | `GET`    | Fetches the full history of user and system actions from Firestore.       |
| **Export Data** | `/export/{data_format}`    | `GET`    | Exports test data in the specified format (`csv`, `xlsx`, or `pdf`).      |