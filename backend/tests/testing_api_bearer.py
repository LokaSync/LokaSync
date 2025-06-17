import httpx
import asyncio
import requests
from os.path import join, dirname
from dotenv import load_dotenv
from os import getenv
from pprint import pprint

# Load environment variables
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

FIREBASE_API_KEY = getenv("FIREBASE_API_KEY")
EMAIL = getenv("TESTING_LOGIN_EMAIL")
PASSWORD = getenv("TESTING_LOGIN_PASSWORD")

class HitAPI():
    def __init__(self, base_url: str = None):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            verify=True,  # SSL verification enabled
            follow_redirects=True,
            headers={
                "User-Agent": "python-httpx/async",
                "Content-Type": "application/json",
            }
        )
    
    def login_firebase(self, email: str, password: str):
        """Login with Firebase and get idToken"""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get('idToken')
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            raise ValueError(f"Login failed: {error_msg}")
    
    async def get_with_token(self, api_endpoint: str, token: str) -> httpx.Response:
        """
        Perform a GET request with Bearer token authentication.
        
        :param api_endpoint: The API endpoint to hit.
        :param token: The Bearer token.
        :return: Response object from the GET request.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        url = f"{self.base_url}/{api_endpoint}"
        response = await self.client.get(url, headers=headers)
        return response
    
    async def get_without_token(self, api_endpoint: str) -> httpx.Response:
        """
        Perform a GET request without authentication.
        
        :param api_endpoint: The API endpoint to hit.
        :return: Response object from the GET request.
        """
        url = f"{self.base_url}/{api_endpoint}"
        response = await self.client.get(url)
        return response
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

def print_response(response: httpx.Response, test_type: str):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"TEST: {test_type}")
    print(f"{'='*50}")
    print(f"URL: {response.url}")
    print(f"Status Code: {response.status_code}")
    print(f"Status Text: {response.reason_phrase}")
    
    try:
        json_data = response.json()
        print(f"Response Body:")
        pprint(json_data)
    except:
        print(f"Response Body (Text):")
        print(response.text)
    
    print(f"{'='*50}")

async def main():
    client = HitAPI("https://lokasync.tech/api/v1")
    
    try:
        while True:
            print("\n🔐 LokaSync API Bearer Token Tester")
            print("=" * 40)
            options = input(
                "Choose an option:\n"
                "1. GET /api/v1/node/ with Bearer token (login first)\n"
                "2. GET /api/v1/node/ without token (should get 401)\n"
                "3. Exit\n"
                "Enter your choice: "
            )
            
            if options == "1":
                print("\n🔑 Logging in with Firebase...")
                try:
                    # Login and get token
                    token = client.login_firebase(EMAIL, PASSWORD)
                    print("✅ Login successful! Got idToken.")
                    
                    # Make API request with token
                    print("\n📡 Making API request with Bearer token...")
                    response = await client.get_with_token("node/", token)
                    print_response(response, "GET /api/v1/node/ WITH Bearer Token")
                    
                    if response.status_code == 200:
                        print("✅ SUCCESS: API request with token worked!")
                    else:
                        print(f"❌ UNEXPECTED: Expected 200, got {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ ERROR during login or API request: {e}")
            
            elif options == "2":
                print("\n📡 Making API request without Bearer token...")
                try:
                    response = await client.get_without_token("node/")
                    print_response(response, "GET /api/v1/node/ WITHOUT Bearer Token")
                    
                    if response.status_code == 401:
                        print("✅ SUCCESS: Got 401 Unauthorized (Expected)")
                    else:
                        print(f"❌ SECURITY ISSUE: Expected 401, got {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ ERROR during API request: {e}")
            
            elif options == "3":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
    
    finally:
        await client.close()

if __name__ == "__main__":
    # Check if environment variables are loaded
    if not FIREBASE_API_KEY or not EMAIL or not PASSWORD:
        print("❌ ERROR: Missing environment variables!")
        print("Make sure these are set in your .env file:")
        print("- FIREBASE_API_KEY")
        print("- TESTING_LOGIN_EMAIL") 
        print("- TESTING_LOGIN_PASSWORD")
        exit(1)
    
    print("🚀 Starting LokaSync API Bearer Token Test")
    print(f"📧 Using email: {EMAIL}")
    print(f"🌐 Testing against: https://lokasync.tech/api/v1/node/")
    
    asyncio.run(main())