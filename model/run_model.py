#!/usr/bin/python3.13

import os 
from google import genai 
from google.genai import types
from helpers.file_ops import *
from helpers.colours import INFO, SUCCESS, FAILED, ERROR, TEXT, RESET
import re  # Add regex support

def validate_response(response, template_config):
    """Validate AI response against template requirements"""
    if not template_config or 'validation' not in template_config:
        return True
    
    validation_rules = template_config['validation']
    
    try:
        # URL pattern validation (for endpoint discovery)
        if 'url_pattern' in validation_rules and isinstance(response, dict):
            for endpoint in response.get('endpoints', []):
                if not re.match(validation_rules['url_pattern'], endpoint.get('url', '')):
                    print(f"{ERROR}[!] Invalid URL format: {endpoint.get('url')}{RESET}")
                    return False
        
        # Required fields validation (for API keys finder)
        if 'required_fields' in validation_rules and isinstance(response, dict):
            for finding in response.get('findings', []):
                if not all(field in finding for field in validation_rules['required_fields']):
                    print(f"{ERROR}[!] Missing required fields in finding: {finding}{RESET}")
                    return False
        
        # Findings count validation
        if 'max_findings' in validation_rules and isinstance(response, dict):
            if len(response.get('findings', [])) > validation_rules['max_findings']:
                print(f"{ERROR}[!] Exceeds max_findings limit ({validation_rules['max_findings']}){RESET}")
                return False
                
        return True
    except Exception as e:
        print(f"{ERROR}[!] Validation error: {e}{RESET}")
        return False

def run_model(prompt,
            system_instruction,
            model_to_use,
            response_mime_type,
            save_response_filename,
            filemode,
            template_config=None):
    
    """Run the Gemini API Model.
     - prompt: Your Prompt
     - system_instruction: system instruction for gemini to behave like that 
     - model_to_use: default: gemini-2.5-flash
     - response_mime_type: 'application/json' or 'text/plain'
     - save_response_filename: gemini output file name
     - filemode: 'w' or 'a' (a for appending)
     - template_config: template configuration for validation

     - note : compitable gemini api model: 
              - gemini-2.5-flash,
              - gemini-2.5-pro,
    """
    try:
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        
        response = client.models.generate_content_stream(
            
            model=model_to_use,
            config=types.GenerateContentConfig(
                safety_settings=safety_settings,
                system_instruction=system_instruction,
                response_mime_type=response_mime_type,
                temperature=1),
            contents=[prompt], 
                )

        full_text = ""
        for chunk in response:
            print(f"{TEXT}{chunk.text}{RESET}")
            full_text += chunk.text
        
        if template_config:
            if not validate_response(response, template_config):
                print(f"{ERROR}[!] Validation failed{RESET}")
                return
        
        save_content(full_text, save_response_filename, filemode)

    except Exception as e:
        print(f"{ERROR}[?] Error in AI Model: {e}{RESET}")