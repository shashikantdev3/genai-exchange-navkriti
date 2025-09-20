# GCP Deployment & Gemini Integration Guide

## 🚀 Google Cloud Platform Deployment

### Prerequisites
1. Google Cloud Account with billing enabled
2. Google Cloud CLI installed
3. Docker installed locally
4. Project with required APIs enabled

### Step 1: Enable Required APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com
```

### Step 2: Set Up Environment Variables
Create a `.env` file in your backend directory:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro
VERTEX_AI_LOCATION=us-central1

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIRESTORE_DATABASE=(default)

# BigQuery Configuration
BIGQUERY_DATASET=healthcare_test_cases
BIGQUERY_TABLE=test_case_data

# Cloud Storage Configuration
STORAGE_BUCKET=your-bucket-name

# Agent Builder Configuration
AGENT_BUILDER_ENGINE_ID=your-engine-id
AGENT_BUILDER_LOCATION=global
```

### Step 3: Deploy Backend to Cloud Run

#### Option A: Using Cloud Build
1. Create `cloudbuild.yaml`:
```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/healthcare-backend', './backend']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/healthcare-backend']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
    - 'run'
    - 'deploy'
    - 'healthcare-backend'
    - '--image'
    - 'gcr.io/$PROJECT_ID/healthcare-backend'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
```

2. Deploy:
```bash
gcloud builds submit --config cloudbuild.yaml
```

#### Option B: Direct Deployment
```bash
# Build and deploy
cd backend
gcloud run deploy healthcare-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id
```

### Step 4: Deploy Frontend to Firebase Hosting
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and initialize
firebase login
firebase init hosting

# Build and deploy
npm run build
firebase deploy
```

## 🤖 Gemini AI Integration

### 1. Update Vertex AI Service
The Gemini integration should be implemented in the Vertex AI service. Here's where to add the API calls:

**Location**: `backend/services/vertex_ai_service.py`

### 2. Install Required Dependencies
Add to `requirements.txt`:
```
google-generativeai>=0.3.0
google-cloud-aiplatform>=1.38.0
```

### 3. Gemini Integration Code
Here's how to integrate Gemini in your existing service:

```python
# backend/services/vertex_ai_service.py
import google.generativeai as genai
from google.cloud import aiplatform
import os
from typing import List, Dict, Any

class VertexAIService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'))
        
        # Initialize Vertex AI
        aiplatform.init(
            project=os.getenv('GOOGLE_CLOUD_PROJECT'),
            location=os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        )
    
    async def generate_test_cases(self, requirements: str, context: Dict[str, Any]) -> List[Dict]:
        """Generate test cases using Gemini AI"""
        prompt = f"""
        As a healthcare software testing expert, generate comprehensive test cases for the following requirements:
        
        Requirements: {requirements}
        Context: {context}
        
        Generate test cases in the following JSON format:
        {{
            "test_cases": [
                {{
                    "id": "TC001",
                    "title": "Test Case Title",
                    "description": "Detailed description",
                    "preconditions": "Prerequisites",
                    "steps": ["Step 1", "Step 2"],
                    "expected_result": "Expected outcome",
                    "priority": "High|Medium|Low",
                    "category": "Functional|Security|Performance|Usability"
                }}
            ]
        }}
        
        Focus on healthcare compliance (HIPAA, FDA), security, and patient safety.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse and return structured data
            return self._parse_gemini_response(response.text)
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_test_cases()
    
    async def regenerate_with_clarifications(self, original_cases: List[Dict], clarifications: str) -> List[Dict]:
        """Regenerate test cases with user clarifications"""
        prompt = f"""
        Improve the following test cases based on user clarifications:
        
        Original Test Cases: {original_cases}
        User Clarifications: {clarifications}
        
        Return improved test cases in the same JSON format, addressing the clarifications.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_gemini_response(response.text)
        except Exception as e:
            print(f"Gemini API error: {e}")
            return original_cases
```

### 4. Update Main Application
In `backend/main.py`, update the endpoints to use Gemini:

```python
@app.post("/generate")
async def generate_test_cases_endpoint(
    requirements: str = Form(...),
    context: str = Form(default=""),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        # Parse context
        context_data = json.loads(context) if context else {}
        
        # Generate test cases using Gemini
        vertex_service = VertexAIService()
        test_cases = await vertex_service.generate_test_cases(requirements, context_data)
        
        # Store in BigQuery and Firestore
        background_tasks.add_task(store_test_cases, test_cases)
        background_tasks.add_task(log_audit_event, "generate", {"requirements": requirements})
        
        return {
            "success": True,
            "test_cases": test_cases,
            "message": "Test cases generated successfully"
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return {"success": False, "error": str(e)}
```

## 🔐 Secure Credential Management

### 1. Service Account Setup
```bash
# Create service account
gcloud iam service-accounts create healthcare-app-sa \
  --display-name="Healthcare App Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:healthcare-app-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:healthcare-app-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:healthcare-app-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:healthcare-app-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=healthcare-app-sa@your-project-id.iam.gserviceaccount.com
```

### 2. Secret Manager Integration
```bash
# Store secrets in Secret Manager
gcloud secrets create gemini-api-key --data-file=gemini-key.txt
gcloud secrets create service-account-key --data-file=key.json

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:healthcare-app-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 3. Environment Configuration for Production
Update your Cloud Run deployment to use secrets:

```bash
gcloud run deploy healthcare-backend \
  --source . \
  --region us-central1 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --service-account healthcare-app-sa@your-project-id.iam.gserviceaccount.com
```

## 📊 Monitoring and Logging

### 1. Enable Cloud Logging
```python
# Add to main.py
import google.cloud.logging

# Setup Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()
```

### 2. Set Up Monitoring
```bash
# Enable monitoring API
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud alpha monitoring uptime create healthcare-backend-check \
  --hostname=your-cloud-run-url \
  --path=/health
```

## 🔧 Local Development with GCP Services

### 1. Authentication
```bash
# Authenticate with your user account
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```

### 2. Local Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT=your-project-id
export GEMINI_API_KEY=your-gemini-key

# Run locally
uvicorn main:app --reload
```

## 🚨 Security Best Practices

1. **Never commit credentials** to version control
2. **Use IAM roles** with least privilege principle
3. **Enable audit logging** for all GCP services
4. **Use HTTPS** for all communications
5. **Implement rate limiting** for API endpoints
6. **Validate all inputs** to prevent injection attacks
7. **Use Secret Manager** for sensitive configuration

## 📈 Scaling Considerations

1. **Cloud Run**: Automatically scales based on traffic
2. **BigQuery**: Handles large datasets efficiently
3. **Firestore**: Scales automatically with usage
4. **Gemini API**: Has rate limits - implement proper retry logic
5. **Cloud Storage**: Virtually unlimited storage

This setup provides a production-ready deployment with proper security, monitoring, and scalability.