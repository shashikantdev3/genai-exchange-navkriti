import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import the Vertex AI platform library for initialization
import google.cloud.aiplatform as aiplatform
import google.generativeai as genai

load_dotenv()

class VertexAIService:
    def __init__(self):
        """
        Initializes the service using Application Default Credentials (ADC),
        the standard and secure way to authenticate on Google Cloud.
        """
        self.model = None
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

        if project_id:
            try:
                # Initialize the Vertex AI SDK with your project
                aiplatform.init(project=project_id)
                
                # The GenerativeModel will now automatically use the authenticated
                # service account instead of an API key.
                self.model = genai.GenerativeModel(
                    self.model_name,
                    # The system instruction can stay here
                    system_instruction="""
                    You are an expert in software quality assurance for healthcare systems. Your task is to analyze raw software requirements text and convert it into a structured set of test cases. The output must be a single, valid JSON array. Each object in the array represents one test case and must conform to the following schema:
                    {"test_case_id": "string", "title": "string", "requirement_id": "string", "steps": ["string"], "expected_result": "string", "priority": "string", "compliance_reference": ["string"], "status": "Not Tested"}
                    Return only the raw JSON array, with no additional text or markdown.
                    """
                )
                print(f"Successfully initialized Vertex AI and created model: {self.model_name}")
            except Exception as e:
                print(f"Error initializing Vertex AI or GenerativeModel: {e}")
                self.model = None
        
        if not self.model:
            print("Warning: Could not initialize Vertex AI. Service will use mock data.")

    # --- The rest of the file remains the same ---
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parses the Gemini response to extract a JSON array of test cases."""
        try:
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            return json.loads(response_text)
        except Exception as e:
            print(f"Error decoding or parsing Gemini response: {e}")
            return self._get_fallback_test_cases()

    def _get_fallback_test_cases(self) -> List[Dict]:
        """Returns a list of mock test cases when the primary service fails."""
        print("Returning fallback test cases.")
        return [
            {
                "test_case_id": "TC-FALLBACK-01", "title": "Fallback: Verify patient data validation",
                "requirement_id": "REQ-001", "steps": ["Check validation messages."],
                "expected_result": "System should validate all fields.", "priority": "Medium",
                "compliance_reference": ["HIPAA"], "status": "Not Tested",
            }
        ]
        
    async def generate_test_cases(self, requirements_text: str) -> List[Dict]:
        """Generates test cases using the configured GenerativeModel."""
        if not self.model or not requirements_text:
            return self._get_fallback_test_cases()
        
        try:
            print(f"Generating test cases with model {self.model_name}...")
            response = await self.model.generate_content_async(
                contents=requirements_text,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._parse_gemini_response(response.text)
        except Exception as e:
            print(f"An error occurred during Gemini API call: {e}")
            return self._get_fallback_test_cases()