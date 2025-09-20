# Healthcare AI Test Case Generator - Backend

This is the FastAPI backend for the Healthcare AI Test Case Generator project, which integrates with Google Cloud services to generate, manage, and audit healthcare test cases.

## Features

- **File Upload**: Upload requirements documents (PDF, Word, text)
- **Test Case Generation**: Generate structured test cases from requirements using Vertex AI
- **Test Case Regeneration**: Refine test cases with user clarifications using Agent Builder
- **Traceability Matrix**: View requirement ↔ test case mappings
- **Audit Trail**: Track all user activities
- **Export**: Export data to CSV, XLSX, or PDF formats

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Google Cloud Services**:
  - Vertex AI (Gemini Pro)
  - BigQuery
  - Firestore
  - Cloud Storage
  - Agent Builder
- **Firebase**: Authentication and storage integration

## Setup

1. **Clone the repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the backend directory with the following variables:
   ```
   FIREBASE_API_KEY=your_firebase_api_key
   FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
   FIREBASE_APP_ID=your_firebase_app_id
   BIGQUERY_PROJECT_ID=your_bigquery_project_id
   AGENT_BUILDER_ENDPOINT=your_agent_builder_endpoint
   VERTEX_AI_MODEL=gemini-1.5-pro
   API_BASE_URL=http://localhost:8000
   ```

4. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- **POST /upload**: Upload requirements documents
- **POST /generate**: Generate test cases from requirements
- **POST /regenerate**: Regenerate test cases with clarifications
- **GET /traceability**: Get traceability matrix
- **GET /audit**: Get audit trail
- **GET /export/{format}**: Export data (csv, xlsx, pdf)

## Deployment

The backend is designed to be deployable to Google Cloud Run or Cloud Functions with Python 3.11 runtime.

To deploy using Docker:
1. Build the Docker image
2. Push to a container registry
3. Deploy to Cloud Run

## Resilience

The backend includes mock data generation for all endpoints to ensure resilience during development or when external APIs are unavailable.

## Integration with Frontend

This backend is designed to work seamlessly with the existing React frontend that has Firebase integration already configured.