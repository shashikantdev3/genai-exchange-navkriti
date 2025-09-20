import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Load environment variables from .env file
load_dotenv()

class VertexAIService:
    def __init__(self):
        """
        Initializes the VertexAIService using the genai.Client for Vertex AI.
        """
        self.client = None
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        
        if api_key:
            try:
                # Initialize the client for Vertex AI integration
                self.client = genai.Client(vertexai=True, api_key=api_key)
                print(f"Successfully configured genai.Client for model: {self.model_name}")
            except Exception as e:
                print(f"Error initializing genai.Client: {e}")
                self.client = None
        
        if not self.client:
            print("Warning: GOOGLE_CLOUD_API_KEY not found or invalid. Service will use mock data.")

    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """
        Parses the Gemini response to extract a JSON array of test cases.
        It cleans the text by removing markdown backticks before parsing.
        """
        try:
            # Clean the response text: remove potential markdown formatting for JSON
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()

            # Find the JSON array within the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
            else:
                print("Warning: Could not find a valid JSON array in the Gemini response.")
                return self._get_fallback_test_cases()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from Gemini response: {e}")
            print(f"Raw response text was: {response_text}")
            return self._get_fallback_test_cases()
        except Exception as e:
            print(f"An unexpected error occurred while parsing the response: {e}")
            return self._get_fallback_test_cases()

    def _get_fallback_test_cases(self) -> List[Dict]:
        """Returns a list of mock test cases when the primary service fails."""
        print("Returning fallback test cases.")
        return [
            # ... (fallback data remains the same)
        ]
        
    async def generate_test_cases(self, requirements_text: str) -> List[Dict]:
        """
        Generates test cases using the genai.Client and a system instruction.
        """
        if not self.client:
            print("Gemini client not available, returning fallback test cases.")
            return self._get_fallback_test_cases()

        # System instruction to guide the model for consistent JSON output
        system_instruction = """
        You are an expert in software quality assurance for healthcare systems. Your task is to analyze raw software requirements text and convert it into a structured set of test cases.

        The output must be a single, valid JSON array. Each object in the array represents one test case and must conform to the following schema:
        {
            "test_case_id": "string (e.g., TC-001)",
            "title": "string",
            "requirement_id": "string (e.g., REQ-001, if identifiable)",
            "steps": ["string", "string", ...],
            "expected_result": "string",
            "priority": "string (Critical, High, Medium, or Low)",
            "compliance_reference": ["string", ...],
            "status": "Not Tested"
        }
        
        Analyze the input carefully to create meaningful test cases covering functional requirements, edge cases, security, data integrity, and compliance. Return only the raw JSON array, with no additional text, explanations, or markdown formatting.
        """

        # Prepare the content for the API call
        contents = [types.Part.from_text(requirements_text)]
        
        try:
            print(f"Generating test cases with model {self.model_name} via Vertex AI...")
            # Use the client to generate content with the system instruction
            response = self.client.models.get(self.model_name).generate_content(
                contents=contents,
                system_instruction=system_instruction
            )
            
            test_cases = self._parse_gemini_response(response.text)
            
            if not test_cases:
                print("Parsing returned no test cases, using fallback.")
                return self._get_fallback_test_cases()
            
            print(f"Successfully generated {len(test_cases)} test cases.")
            return test_cases
        except Exception as e:
            print(f"An error occurred during Gemini API call via Vertex AI: {e}")
            return self._get_fallback_test_cases()