#!/usr/bin/env python3
"""
Diagnostic script to identify "Method Not Allowed" errors

This script will help you identify exactly which URL and method
is causing the "Method Not Allowed" error.
"""

import requests
import sys

def diagnose_method_error():
    """Diagnose the Method Not Allowed error."""
    base_url = "http://127.0.0.1:5002"
    
    print("🔍 Diagnosing 'Method Not Allowed' Error")
    print("=" * 50)
    
    # Test all possible URLs and methods
    test_cases = [
        # (URL, Method, Should Work, Description)
        ("/", "GET", True, "Main page"),
        ("/", "POST", False, "Main page with POST"),
        ("/health", "GET", True, "Health check"),
        ("/health", "POST", False, "Health check with POST"),
        ("/upload", "GET", False, "Upload page with GET (causes error)"),
        ("/upload", "POST", True, "Upload page with POST"),
        ("/api/scan", "GET", False, "API scan with GET (causes error)"),
        ("/api/scan", "POST", True, "API scan with POST"),
        ("/api/results", "GET", True, "API results"),
        ("/api/results", "POST", False, "API results with POST"),
    ]
    
    print("Testing all possible URL and method combinations:\n")
    
    for url, method, should_work, description in test_cases:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{url}", timeout=5)
            else:
                response = requests.post(f"{base_url}{url}", timeout=5)
            
            status = response.status_code
            
            if should_work:
                if status == 200:
                    print(f"✅ {method} {url} - {description} - OK")
                else:
                    print(f"⚠️ {method} {url} - {description} - Status: {status}")
            else:
                if status == 405:
                    print(f"❌ {method} {url} - {description} - METHOD NOT ALLOWED (expected)")
                elif status == 200:
                    print(f"✅ {method} {url} - {description} - OK (unexpected)")
                else:
                    print(f"⚠️ {method} {url} - {description} - Status: {status}")
                    
        except Exception as e:
            print(f"❌ {method} {url} - {description} - Error: {e}")
    
    print("\n" + "=" * 50)
    print("📝 SUMMARY:")
    print("❌ URLs that cause 'Method Not Allowed' with GET:")
    print("   - /upload (use POST or web form)")
    print("   - /api/scan (use POST with file)")
    print()
    print("✅ URLs that work with GET:")
    print("   - / (main page)")
    print("   - /health (health check)")
    print("   - /api/results (results)")
    print()
    print("🌐 CORRECT USAGE:")
    print("1. Open browser to: http://127.0.0.1:5002")
    print("2. Use the web form to upload images")
    print("3. Don't type /upload or /api/scan directly in browser")

def test_specific_url():
    """Test a specific URL that user might be having trouble with."""
    if len(sys.argv) > 1:
        url = sys.argv[1]
        method = sys.argv[2] if len(sys.argv) > 2 else "GET"
        
        print(f"🧪 Testing specific URL: {method} {url}")
        print("=" * 40)
        
        try:
            if method.upper() == "GET":
                response = requests.get(f"http://127.0.0.1:5002{url}", timeout=10)
            else:
                response = requests.post(f"http://127.0.0.1:5002{url}", timeout=10)
            
            print(f"Status: {response.status_code}")
            print(f"Reason: {response.reason}")
            
            if response.status_code == 405:
                print("❌ This is the 'Method Not Allowed' error!")
                print(f"   {method} is not allowed for {url}")
                
                # Suggest correct method
                if url in ["/upload", "/api/scan"]:
                    print(f"   Try using POST instead of {method}")
                elif url in ["/", "/health", "/api/results"]:
                    print(f"   Try using GET instead of {method}")
            elif response.status_code == 200:
                print("✅ This URL works!")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        test_specific_url()
    else:
        diagnose_method_error()

if __name__ == '__main__':
    main()
