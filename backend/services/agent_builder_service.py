import os
import json
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

async def refine_prompt(requirements: List[Dict[str, Any]], clarifications: str) -> str:
    """
    Refine the prompt for test case generation using Agent Builder
    
    Args:
        requirements: List of requirements to generate test cases for
        clarifications: User clarifications for test case regeneration
        
    Returns:
        Refined prompt for Vertex AI
    """
    try:
        # Get Agent Builder endpoint from environment variables
        agent_endpoint = os.getenv('AGENT_BUILDER_ENDPOINT')
        
        if not agent_endpoint:
            raise Exception("Agent Builder endpoint not configured")
        
        # Format requirements for the prompt
        requirements_json = json.dumps(requirements, indent=2)
        
        # Prepare request payload
        payload = {
            "requirements": requirements_json,
            "clarifications": clarifications
        }
        
        # Call Agent Builder API
        response = requests.post(agent_endpoint, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Agent Builder API returned status code {response.status_code}")
        
        # Extract refined prompt from response
        response_data = response.json()
        refined_prompt = response_data.get('refined_prompt')
        
        if not refined_prompt:
            raise Exception("No refined prompt returned from Agent Builder")
        
        return refined_prompt
    except Exception as e:
        print(f"Error refining prompt with Agent Builder: {str(e)}")
        
        # Generate a fallback prompt if Agent Builder fails
        requirements_json = json.dumps(requirements, indent=2)
        fallback_prompt = f"""
        Given these healthcare requirements: {requirements_json}
        
        And these clarifications from the user: {clarifications}
        
        Generate comprehensive test cases with the following fields:
        - test_case_id: A unique identifier (TC-XXX format)
        - title: A descriptive title for the test case
        - requirement_id: The ID of the requirement this test case covers
        - steps: A list of steps to execute the test
        - expected_result: The expected outcome of the test
        - priority: The priority level (Critical, High, Medium, Low)
        - compliance_reference: List of compliance standards this test case helps satisfy (e.g., FDA 21 CFR Part 11, HIPAA, ISO 13485)
        - status: "Not Tested" (default)
        
        Focus on:
        1. Edge cases and boundary conditions
        2. Security considerations
        3. Performance requirements
        4. Negative testing scenarios
        5. Healthcare-specific compliance requirements
        6. The specific clarifications provided by the user
        
        Return the test cases as a valid JSON array.
        """
        
        return fallback_prompt