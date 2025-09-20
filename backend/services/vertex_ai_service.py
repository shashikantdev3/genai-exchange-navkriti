import os
from typing import List, Dict, Any
import json
import google.generativeai as genai
from google.cloud import aiplatform
import re

class VertexAIService:
    def __init__(self):
        # Configure Gemini API
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'))
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found, using mock data")
        
        # Initialize Vertex AI
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        
        if project_id:
            aiplatform.init(project=project_id, location=location)
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict]:
        """Parse Gemini response and extract test cases"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return data.get('test_cases', [])
            else:
                # Fallback parsing if JSON is not properly formatted
                return self._parse_text_response(response_text)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._get_fallback_test_cases()
    
    def _parse_text_response(self, text: str) -> List[Dict]:
        """Parse text response when JSON parsing fails"""
        # Simple text parsing logic for test cases
        test_cases = []
        lines = text.split('\n')
        current_case = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Test Case'):
                if current_case:
                    test_cases.append(current_case)
                current_case = {
                    "id": f"TC{len(test_cases) + 1:03d}",
                    "title": line,
                    "description": "",
                    "preconditions": "",
                    "steps": [],
                    "expected_result": "",
                    "priority": "Medium",
                    "category": "Functional"
                }
            elif line.startswith('Description:'):
                current_case["description"] = line.replace('Description:', '').strip()
            elif line.startswith('Steps:'):
                current_case["steps"] = [line.replace('Steps:', '').strip()]
            elif line.startswith('Expected:'):
                current_case["expected_result"] = line.replace('Expected:', '').strip()
        
        if current_case:
            test_cases.append(current_case)
        
        return test_cases if test_cases else self._get_fallback_test_cases()
    
    def _get_fallback_test_cases(self) -> List[Dict]:
        """Return fallback test cases when Gemini is unavailable"""
        return [
            {
                "id": "TC001",
                "title": "Patient Data Validation",
                "description": "Verify patient data input validation for healthcare compliance",
                "preconditions": "User logged in with valid healthcare provider credentials",
                "steps": [
                    "Navigate to patient registration form",
                    "Enter invalid patient data (missing required fields)",
                    "Attempt to submit the form",
                    "Verify validation messages appear"
                ],
                "expected_result": "System displays appropriate validation errors and prevents submission",
                "priority": "High",
                "category": "Functional"
            },
            {
                "id": "TC002",
                "title": "HIPAA Compliance Check",
                "description": "Verify system maintains HIPAA compliance for patient data access",
                "preconditions": "Multiple user roles configured in system",
                "steps": [
                    "Login as unauthorized user",
                    "Attempt to access patient records",
                    "Verify access is denied",
                    "Check audit logs for access attempt"
                ],
                "expected_result": "Access denied and security event logged",
                "priority": "Critical",
                "category": "Security"
            }
        ]

    async def generate_test_cases(self, requirements: str, context: Dict[str, Any] = None) -> List[Dict]:
        """Generate test cases using Gemini AI"""
        if not self.model:
            print("Gemini model not available, returning fallback test cases")
            return self._get_fallback_test_cases()
        
        context = context or {}
        
        prompt = f"""
        As a healthcare software testing expert with deep knowledge of medical device regulations, HIPAA compliance, and FDA requirements, generate comprehensive test cases for the following requirements:
        
        Requirements: {requirements}
        Context: {json.dumps(context, indent=2)}
        
        Generate test cases in the following JSON format:
        {{
            "test_cases": [
                {{
                    "id": "TC001",
                    "title": "Descriptive Test Case Title",
                    "description": "Detailed description of what this test validates",
                    "preconditions": "Prerequisites and setup required",
                    "steps": ["Step 1: Action to perform", "Step 2: Next action", "Step 3: Verification step"],
                    "expected_result": "Clear expected outcome",
                    "priority": "Critical|High|Medium|Low",
                    "category": "Functional|Security|Performance|Usability|Compliance"
                }}
            ]
        }}
        
        Requirements for test cases:
        1. Focus on healthcare compliance (HIPAA, FDA 21 CFR Part 820, IEC 62304)
        2. Include security testing for patient data protection
        3. Cover accessibility requirements (Section 508, WCAG 2.1)
        4. Include performance testing for critical healthcare workflows
        5. Test error handling and system resilience
        6. Validate data integrity and audit trails
        7. Test user authentication and authorization
        8. Include boundary testing for medical data inputs
        
        Generate at least 5-8 comprehensive test cases covering different aspects.
        """
        
        try:
            response = self.model.generate_content(prompt)
            test_cases = self._parse_gemini_response(response.text)
            
            # Ensure we have valid test cases
            if not test_cases or len(test_cases) == 0:
                return self._get_fallback_test_cases()
            
            return test_cases
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_test_cases()

    async def regenerate_test_cases(self, original_cases: List[Dict], clarifications: str) -> List[Dict]:
        """Regenerate test cases with user clarifications using Gemini AI"""
        if not self.model:
            print("Gemini model not available, returning original test cases")
            return original_cases
        
        prompt = f"""
        As a healthcare software testing expert, improve and regenerate the following test cases based on user feedback and clarifications:
        
        Original Test Cases: {json.dumps(original_cases, indent=2)}
        
        User Clarifications and Feedback: {clarifications}
        
        Please:
        1. Address all user feedback and clarifications
        2. Improve test case clarity and completeness
        3. Add missing test scenarios based on feedback
        4. Ensure healthcare compliance requirements are met
        5. Maintain the same JSON format as the original
        
        Return the improved test cases in the same JSON format:
        {{
            "test_cases": [
                // Improved test cases here
            ]
        }}
        
        Focus on making the test cases more comprehensive, clearer, and better aligned with the user's requirements.
        """
        
        try:
            response = self.model.generate_content(prompt)
            improved_cases = self._parse_gemini_response(response.text)
            
            # Return improved cases if successful, otherwise return originals
            return improved_cases if improved_cases else original_cases
            
        except Exception as e:
            print(f"Gemini API regeneration error: {e}")
            return original_cases