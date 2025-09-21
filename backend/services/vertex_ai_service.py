import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import the required Google Cloud and Generative AI libraries
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
                # Initialize the Vertex AI SDK, which sets up the authentication context
                aiplatform.init(project=project_id)
                
                # A detailed system instruction to guide the model's behavior consistently
                system_instruction = """
                You are an expert in software quality assurance for healthcare systems. Your task is to analyze raw software requirements text and convert it into a structured set of test cases.

                The output must be a single, valid JSON array. Each object in the array represents one test case and must conform to the following schema:
                {"test_case_id": "string", "title": "string", "requirement_id": "string", "steps": ["string"], "expected_result": "string", "priority": "string (Critical, High, Medium, or Low)", "compliance_reference": ["string (e.g., HIPAA, FDA 21 CFR Part 11)"], "status": "Not Tested"}

                Analyze the input carefully to create meaningful positive, negative, and edge-case tests. Return only the raw JSON array, with no additional text, explanations, or markdown formatting.
                """

                # Create the model instance with the system instruction
                self.model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction
                )
                print(f"Successfully initialized Vertex AI and created model: {self.model_name}")
            except Exception as e:
                print(f"Error initializing Vertex AI or GenerativeModel: {e}")
                self.model = None
        
        if not self.model:
            print("Warning: Could not initialize Vertex AI. Service will use mock data.")

    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Safely parses the JSON response from the Gemini model."""
        try:
            return json.loads(response_text)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding or parsing Gemini response: {e}")
            return self._get_fallback_test_cases()

    def _get_fallback_test_cases(self) -> List[Dict]:
        """Returns a list of mock test cases when the primary service fails."""
        print("Returning fallback test cases.")
        return [
            {
                "test_case_id": "TC-FALLBACK-01",
                "title": "Fallback: Verify patient data validation",
                "requirement_id": "REQ-001",
                "steps": ["Navigate to patient registration.", "Enter valid and invalid data.", "Check for validation messages."],
                "expected_result": "System should correctly validate all fields.",
                "priority": "Medium",
                "compliance_reference": ["HIPAA"],
                "status": "Not Tested",
            }
        ]
        
    async def generate_test_cases(self, requirements_text: str) -> List[Dict]:
        """
        Generates test cases using a "few-shot" prompting technique for high accuracy.
        """
        if not self.model or not requirements_text:
            return self._get_fallback_test_cases()

        # --- Few-Shot Example ---
        # This high-quality example teaches the model the exact format and quality you expect.
        example_input = "REQ-002: The system shall support secure login for patients and staff using email and password."
        example_output = """
[
  {
    "test_case_id": "TC-002-01",
    "title": "Verify successful login with valid patient credentials",
    "requirement_id": "REQ-002",
    "steps": [
      "Navigate to the patient login page.",
      "Enter a valid, registered patient email.",
      "Enter the correct password for that email.",
      "Click the 'Login' button."
    ],
    "expected_result": "The user is successfully logged in and redirected to the patient dashboard.",
    "priority": "Critical",
    "compliance_reference": ["HIPAA"],
    "status": "Not Tested"
  },
  {
    "test_case_id": "TC-002-02",
    "title": "Verify failed login with invalid password",
    "requirement_id": "REQ-002",
    "steps": [
      "Navigate to the patient login page.",
      "Enter a valid, registered patient email.",
      "Enter an incorrect password.",
      "Click the 'Login' button."
    ],
    "expected_result": "An error message 'Invalid email or password' is displayed. The user is not logged in.",
    "priority": "High",
    "compliance_reference": [],
    "status": "Not Tested"
  }
]
"""
        # Construct the full conversation for the model using the compatible format
        contents = [
            {'role': 'user', 'parts': [example_input]},
            {'role': 'model', 'parts': [example_output]},
            {'role': 'user', 'parts': [requirements_text]}
        ]
        
        try:
            print(f"Generating test cases with model {self.model_name} using few-shot prompt...")
            response = await self.model.generate_content_async(
                contents=contents,
                generation_config={"response_mime_type": "application/json"}
            )
            return self._parse_gemini_response(response.text)
        except Exception as e:
            print(f"An error occurred during Gemini API call: {e}")
            return self._get_fallback_test_cases()