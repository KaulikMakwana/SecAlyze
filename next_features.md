# Red Teaming Features for Secalyze

## **Phase 1: Quick Wins (Minimal Code Changes)**

1. **Security Header Auditor**  
   - Check for missing `CSP`, `HSTS`, `X-Frame-Options`  
   - Rate and report security posture  

2. **Common Vulnerability Path Scanner**  
   - Auto-check for `.git/config`, `wp-admin/`, `debug.php`  
   - Flag exposed dev/backup files  

3. **Login Page Analyzer**  
   - Catalog all auth endpoints (HTML forms, OAuth)  
   - Detect weak password policies  

---

## **Phase 2: Advanced Features**  

4. **JavaScript Secrets Hunter**  
   - AST/regex scanning for API keys, tokens  
   - Extract hardcoded credentials  

5. **Endpoint Discovery from JS/CSS**  
   - Parse `fetch()`, `axios` calls  
   - Map hidden API routes  

6. **Credential Harvesting Mode**  
   - `--harvest-passwords` flag for form analysis  
   - Export findings for brute-force testing  

---

## **Phase 3: AI-Powered Offensive**  

7. **Gemini-Powered Vuln Analysis**  
   - AI review of scraped content for:  
     - Exposed PII/sensitive data  
     - Logical flaws in web flows  

8. **Phishing Template Generator**  
   - Auto-clone pages + inject payloads  
   - AI-generated pretexts  

---

*Last Updated: 2025-07-14*  
*Maintainer: KaulikMakwana*
