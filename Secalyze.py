#!/usr/bin/python3.13
"""
Secalyze - AI-Powered Multi-Purpose Security Assessment & Automation CLI
"""

__version__ = "v1.3.0"  # Manual semantic version

import os
import time
import random
import argparse
import requests
import json
import pandas as pd
from urllib.parse import urlparse
import yaml  # Add YAML support
from helpers.colours import INFO, SUCCESS, FAILED, ERROR, TEXT, RESET, print_banner
from helpers.file_ops import *
from model.run_model import run_model
from helpers.mimetype_map import resolve_mimetype
import sys
import tempfile
import zipfile
import shutil
import re
import datetime
import subprocess

def load_template(template_path):
    """Load and validate YAML template"""
    try:
        with open(template_path) as f:
            config = yaml.safe_load(f)
        if not config or not isinstance(config, dict):
            raise ValueError("Template file is empty or invalid")
        required_sections = ['system_instruction', 'task_config', 'model_config']
        if not all(k in config for k in required_sections):
            raise ValueError(f"Template missing required sections: {required_sections}")
        return config
    except Exception as e:
        print(f"{ERROR}[!] Failed to load template: {e}{RESET}")
        return None

def fetch_request(url, max_retries=10, retry_delay=5):
    """Fetch a webpage with retries."""
    proxy_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    try:
        response = requests.get(proxy_url)
        proxy_list = response.text.splitlines()
        http_proxies = [proxy for proxy in proxy_list if proxy.startswith('http')]
    except Exception as e:
        print(f"{ERROR}[?] Error fetching proxies: {e}{RESET}")
        http_proxies = []

    headers_list = [
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'},
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'},
        {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2'},
    ]

    for attempt in range(max_retries):
        try:
            print(f"{INFO}[*] Attempt {attempt + 1}: Fetching page...{RESET}")
            proxy = random.choice(http_proxies) if http_proxies else None
            proxies = {"http": proxy} if proxy else None
            response = requests.get(url, headers=random.choice(headers_list), proxies=proxies)
            if response.status_code == 200:
                print(f"{SUCCESS}[+] Success! Status code: {response.status_code}{RESET}")
                return response.text
            print(f"{FAILED}[-] Failed with status code: {response.status_code}. Retrying...{RESET}")
        except requests.exceptions.RequestException as e:
            print(f"{ERROR}[?] Error fetching the page: {e}. Retrying...{RESET}")
        time.sleep(retry_delay)
    return None



def only_url_passed(url,max_retries,retry_delay,
                    prompt,system_instruction,model_to_use,mimetype,
                    output_filename,filemode):
    """Function if only url parameter passed..."""
    domain_name=urlparse(url).netloc
    os.makedirs(domain_name, exist_ok=True)
    output_path=os.path.join(domain_name,output_filename)
    webpage=fetch_request(url,max_retries,retry_delay)
    
    if webpage:
        run_model(prompt=f"{prompt}, {webpage}",
                  system_instruction=system_instruction,
                  save_response_filename=output_path,
                  model_to_use=model_to_use,
                  filemode=filemode,response_mime_type=mimetype)
    else:
        print(f"{ERROR}[?] Error fetching webpage.{RESET}")
    
def work_with_multiple_urls(link_file_json,
            prompt, system_instruction,model_to_use,mimetype,filemode,
            output_filename, max_retries, retry_delay):
    """Main scrap function for group of urls."""

    try:
        print(f"{INFO}[*] Reading extracted links...{RESET}")
        
        # Read JSON file
        with open(link_file_json) as f:
            data = json.load(f)
        
        # Handle both JSON objects and arrays
        if isinstance(data, list):
            # Simple array format - create DataFrame with default type
            url_series = pd.DataFrame({'url': data, 'url_type': 'JS Script'})
        else:
            # Object format - process with categories
            url_series = pd.DataFrame.from_dict(
                {k: pd.Series(v) for k, v in data.items()},
                orient='index'
            ).stack().reset_index(level=0)
            url_series.columns = ['url_type', 'url']
        
        for idx, row in url_series.iterrows():
            link = row['url']
            domain_name = urlparse(link).netloc
            
            if not domain_name:
                print(f"{ERROR}[?] Invalid URL: {link}{RESET}")
                continue
                
            os.makedirs(domain_name, exist_ok=True)
            print(f"[{idx}] {link} (Type: {row.get('url_type', 'JS Script')})")
            page_content = fetch_request(link, max_retries, retry_delay)
           
            if page_content:
                print(f"{SUCCESS}[+] Processing page data...{RESET}")
                endpoint = os.path.basename(urlparse(link).path)
                output_path = os.path.join(domain_name,f"{idx}_{endpoint}_{output_filename}")
                run_model(prompt=f"{prompt}, : {page_content}",
                          system_instruction=system_instruction,
                          save_response_filename=output_path,
                          model_to_use=model_to_use,
                          response_mime_type=mimetype,
                          filemode=filemode)
            else:
                print(f"{ERROR}[?] Error loading page: {link}{RESET}")
    
    except FileNotFoundError as e:
        print(f"{ERROR}[?] File not found: {e}{RESET}")
    except Exception as e:
        print(f"{ERROR}[?] Failed to process JSON file (must be either object with URL categories or array of URLs): {e}{RESET}")



if __name__ == "__main__":
    print_banner()
    parser = argparse.ArgumentParser(description=f"{INFO}Secalyze - AI-Powered Multi-Purpose Security Assessment & Automation CLI{RESET}",
    usage="""
> python3 Secalyze.py -url 'https://example.com/' -p 'Analyse JS scripts and enumerate any Vulns if Exists...' -mimetype text -o JSVulns 

> python3 Secalyze.py -f JSurls.json -p 'Analyze this content for exposed API keys and secrets' -mimetype json -o APIKeys

> python3 Secalyze.py -t TEMPLATES/endpoint_discovery.yaml -f files.json -mimetype x.enum -o endpoints.txt 
    """)

    # Input source group
    input_group = parser.add_argument_group(f'{INFO}Input Options{RESET}')
    input_group.add_argument("-url", "--url", type=str, help="target URL ....")
    input_group.add_argument("-f","--file",type=str,help="json file contains target links...")

    # AI Model configuration group
    ai_group = parser.add_argument_group(f'{INFO}AI Model Configuration{RESET}')
    ai_group.add_argument("-system", "--system_instruction", type=str,
                        default="""
You are a professional Vulnerability Assessment and Penetration Testing (VAPT) Analyst.
Your primary objective is to analyze web application assets (HTML, JavaScript, configuration files, etc.) to identify security vulnerabilities, enumerate resources, and execute user-directed security tasks.
You must adhere to the following principles:
Precision: Provide only actionable, technically accurate information.
Brevity: Do not include conversational filler, apologies, or unnecessary commentary.
Formatting: All output must strictly follow the Markdown templates defined below          

[SECTION 1] VULNERABILITY IDENTIFICATION & REPORTING:
Upon analyzing any provided code (JavaScript, HTML, etc.), your primary task is to identify security vulnerabilities.
If vulnerabilities are identified, you will generate a report for each finding using the following strict 

Markdown template:
### Vulnerability: [Clear and Concise Vulnerability Title]
- **Severity:** [Critical | High | Medium | Low | Informational]
- **File/Location:** [Path to the file or URL where the vulnerability exists]
- **CWE:** [CWE-ID, e.g., CWE-79 for XSS, CWE-798 for Hardcoded Credentials]
- **Description:** A brief technical summary of the vulnerability, explaining what it is and how it occurs in the context of the code.
- **Impact:** A clear statement on the potential business and security impact. What can an attacker achieve? (e.g., "An attacker can execute arbitrary JavaScript in the context of the user's browser, leading to session hijacking or data theft.")
- **Steps to Reproduce:**
  1. Detailed, step-by-step instructions that an analyst can follow to confirm the finding.
- **Proof-of-Concept (POC):**
  ```[language]
  // Provide a concise code snippet, URL, or command that demonstrates the vulnerability.
```

Mitigation: Specific, actionable recommendations for developers to fix the vulnerability.

If no vulnerabilities are found after a thorough analysis, you will respond with the following exact line:

`No significant client-side vulnerabilities were identified.`

-------------------------------
**[SECTION 2] ASSET & ENDPOINT ENUMERATION**
-------------------------------

During your analysis, you will passively enumerate all discoverable assets and sensitive information. Present all findings grouped under the following headings.

If a category has no findings, omit the heading. If no resources of any kind are found, respond with the following exact line: `No discoverable resources or sensitive data were found.`

**### Discovered Paths**
*(Format: `<scheme>://<domain>/<path>/`)*
- `https://example.com/admin/`
- `https://example.com/assets/`

**### JavaScript Files**
*(Format: `<scheme>://<domain>/<path>/*.js`)*
- `https://example.com/static/main.js`
- `https://cdn.example.com/vendor.min.js`

**### API Endpoints**
*(Format: `METHOD <scheme>://<domain>/<api-path>`)*
- `GET https://example.com/api/v2/users`
- `POST https://example.com/api/v2/auth/login`

**### Hardcoded Secrets & Sensitive Data**
*(Format: `TYPE: "VALUE" // Location/Context`)*
- `API Key: "ak_live_..." // Found in config.js`
- `JWT Secret: "super-secret-..." // Found in app.js L:42`

-------------------------------
**[SECTION 3] DYNAMIC TASK EXECUTION**
-------------------------------

The USER's direct prompt is your highest priority command. This section overrides Sections 1 and 2 if the user requests a specific, targeted action.

*   **Prioritize the User's Request:** Immediately execute the user's task. Examples include:
    *   "Analyze these HTTP headers for security misconfigurations."
    *   "Suggest a `curl` command to test for weak authentication on `/api/login`."
    *   "Write a Nuclei template for the vulnerability you found in `app.js`."
    *   "Fuzz the `id` parameter on `https://example.com/items?id=1` for SQL injection."
*   **Integrate Findings:** If the task is general (e.g., "Analyze this JS file"), you must perform the analysis and then present the output using the templates from Sections 1 and 2.
*   **Maintain Clarity:** Ensure the output for the specific task is well-formatted, clean, and directly answers the user's query.

**END OF INSTRUCTIONS.**
  
    """,
    help="System instruction for AI model. Default: Expert red team operator instruction")
    
    ai_group.add_argument("-p", "--prompt", type=str, default="Analyze the following JavaScript code for vulnerabilities and enumerate any embedded resources.", help="Prompt for AI model")
    ai_group.add_argument("-mimetype", "--response_mime_type", type=str, default="text/plain",
                        help="Response MIME type for AI model output. Accepts: json, text, xml, yaml, x.enum, etc. (or full MIME type)")
    ai_group.add_argument("-m","--model",type=str,default="gemini-2.5-flash",
                        help="gemini genai model to use.. default: gemini-2.5-flash | gemini-2.5-pro")

    # Template configuration group
    template_group = parser.add_argument_group(f'{INFO}Template Options{RESET}')
    template_group.add_argument('-t', '--template', 
                              help='YAML template file for specialized security tasks',
                              metavar='TEMPLATE_FILE')

    # Output configuration group
    output_group = parser.add_argument_group(f'{INFO}Output Configuration{RESET}')
    output_group.add_argument("-o", "--output", type=str, default="VulnReport", help="Output filename")
    output_group.add_argument("-filemode", "--filemode", type=str, default="a",
                        help="File mode for saving output. 'w' for overwrite, 'a' for append. Default: 'a'")

    # Network configuration group
    network_group = parser.add_argument_group(f'{INFO}Network Configuration{RESET}')
    network_group.add_argument("-retry", "--max_retries", type=int, default=10, help="Maximum retries for HTTP requests")
    network_group.add_argument("-delay", "--retry_delay", type=int, default=5, help="Delay between retries")

    parser.add_argument('--version', action='store_true', help='Show Secalyze version and exit')
    args = parser.parse_args()
    if getattr(args, 'version', False):
        print(f"Secalyze version: {__version__}")
        sys.exit(0)

    try:
        print(f"{INFO}[*] Starting Vulnerability scanning process...{RESET}")
        
        # Load template if specified
        template_config = None
        if args.template:
            template_config = load_template(args.template)
            if not template_config:
                print(f"{FAILED}[-] Aborting due to template loading failure{RESET}")
                sys.exit(1)

            args.system_instruction = template_config.get('system_instruction', args.system_instruction)
            args.prompt = template_config['task_config'].get('prompt', args.prompt)
            args.model = template_config['model_config'].get('model', args.model)
            # Always resolve mimetype from template or CLI
            args.response_mime_type = resolve_mimetype(template_config['model_config'].get('response_mime_type', args.response_mime_type))
        else:
            args.response_mime_type = resolve_mimetype(args.response_mime_type)

        from helpers.mimetype_map import get_extension_for_mimetype
        # Auto-append extension if needed
        def ensure_extension(filename, mimetype):
            import os
            ext = os.path.splitext(filename)[1]
            if ext:
                return filename
            return filename + get_extension_for_mimetype(mimetype)

        output_filename = ensure_extension(args.output, args.response_mime_type)

        if args.file :
            if args.file.endswith('.json'):
                work_with_multiple_urls(args.file,
                    args.prompt, args.system_instruction, args.model,
                    args.response_mime_type, args.filemode,
                    output_filename,
                    args.max_retries, args.retry_delay)
            
            else:
                print(f"{TEXT}...No JSON File detected ; Proceeding with user provided file : {args.file} {RESET}")
                run_model(prompt=f"{args.prompt}, : {read_file_content(args.file)}",
                          system_instruction=args.system_instruction,
                          model_to_use=args.model,
                          response_mime_type=args.response_mime_type,
                          save_response_filename=output_filename,
                          filemode=args.filemode,
                          template_config=template_config) 
    
        elif args.url:
            only_url_passed(args.url,
                            args.max_retries, args.retry_delay,
                            args.prompt, args.system_instruction,
                            args.model, args.response_mime_type,
                            output_filename, args.filemode)
            
        # If no meaningful arguments at all, show usage and exit
        if not (args.url or args.file or args.template or (args.prompt and len(sys.argv) > 1)):
            parser.print_usage()
            sys.exit(0)
        
        # If only a prompt is provided (and at least one argument is present), run the model with the prompt
        if args.prompt and not (args.url or args.file or args.template) and len(sys.argv) > 1:
            run_model(prompt=args.prompt,
                      system_instruction=args.system_instruction,
                      model_to_use=args.model,
                      response_mime_type=args.response_mime_type,
                      save_response_filename=output_filename,
                      filemode=args.filemode,
                      template_config=template_config)


    except KeyboardInterrupt:
        print(f"{FAILED}[-] Process interrupted by user.{RESET}")
    except Exception as e:
        print(f"{ERROR}[?] Unexpected error: {e}{RESET}")
