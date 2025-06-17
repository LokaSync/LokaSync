import httpx
import asyncio
import requests
from os.path import join, dirname
from dotenv import load_dotenv
from os import getenv
import time
from datetime import datetime
from typing import List, Dict, Any

# Load environment variables
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path=dotenv_path)

FIREBASE_API_KEY = getenv("FIREBASE_API_KEY")
EMAIL = getenv("TESTING_LOGIN_EMAIL")
PASSWORD = getenv("TESTING_LOGIN_PASSWORD")

class RaceConditionTest:
    def __init__(self, base_url: str = "https://lokasync.tech/api/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            verify=True,  # SSL verification enabled
            follow_redirects=True,
            headers={
                "User-Agent": "python-httpx/async",
                "Content-Type": "application/json",
            },
            timeout=30.0
        )
        self.token = None
    
    def login_firebase(self, email: str, password: str) -> str:
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
            self.token = data.get('idToken')
            return self.token
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            raise ValueError(f"Login failed: {error_msg}")
    
    async def add_node_request(self, request_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Single request to add a new node
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = await self.client.post("/node/add-new", json=payload, headers=headers)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Fix: Use datetime instead of time.strftime for microseconds
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
            
            result = {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "timestamp": timestamp,
                "success": response.status_code in [200, 201]
            }
            
            try:
                result["response_body"] = response.json()
            except:
                result["response_body"] = response.text
                
            return result
            
        except Exception as e:
            # Fix: Same timestamp fix for error case
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
            
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time_ms": 0,
                "timestamp": timestamp,
                "success": False,
                "error": str(e),
                "response_body": None
            }
    
    async def test_race_condition_add_node(self, concurrent_requests: int = 5) -> List[Dict[str, Any]]:
        """
        Test race condition by sending multiple concurrent requests to add the same node
        """
        # Node payload to be sent
        node_payload = {
            "node_id": "1x",
            "node_location": "Cibubur-SayuranPagi", 
            "node_type": "Pembibitan",
            "description": "This is an optional field."
        }
        
        print(f"🏁 Starting race condition test with {concurrent_requests} concurrent requests")
        print(f"📦 Payload: {node_payload}")
        print(f"🎯 Target endpoint: {self.base_url}/node/add-new")
        print("=" * 80)
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_requests):
            task = self.add_node_request(i + 1, node_payload)
            tasks.append(task)
        
        # Execute all requests simultaneously
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.time() - start_time) * 1000
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                current_time = datetime.now()
                timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
                
                processed_results.append({
                    "request_id": i + 1,
                    "status_code": 0,
                    "response_time_ms": 0,
                    "timestamp": timestamp,
                    "success": False,
                    "error": str(result),
                    "response_body": None
                })
            else:
                processed_results.append(result)
        
        # Print results
        self.print_race_condition_results(processed_results, total_time)
        
        return processed_results
    
    def print_race_condition_results(self, results: List[Dict[str, Any]], total_time: float):
        """Print formatted results of the race condition test"""
        
        print("🏁 RACE CONDITION TEST RESULTS")
        print("=" * 80)
        
        # Individual request results
        for result in results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} Request #{result['request_id']}:")
            print(f"   Status: {result['status_code']}")
            print(f"   Time: {result['response_time_ms']}ms")
            print(f"   Timestamp: {result['timestamp']}")
            
            if result.get("error"):
                print(f"   Error: {result['error']}")
            elif result.get("response_body"):
                response = result["response_body"]
                if isinstance(response, dict):
                    if response.get("message"):
                        print(f"   Message: {response['message']}")
                    if response.get("detail"):
                        print(f"   Detail: {response['detail']}")
                    # Also show response data if available
                    if response.get("data"):
                        print(f"   Data: {response['data']}")
                else:
                    print(f"   Response: {str(response)[:100]}...")
            print()
        
        # Summary statistics
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = len(results) - successful_requests
        
        if successful_requests > 0:
            avg_response_time = sum(r["response_time_ms"] for r in results if r["success"]) / successful_requests
        else:
            avg_response_time = 0
        
        print("📊 SUMMARY")
        print("=" * 40)
        print(f"Total requests: {len(results)}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success rate: {(successful_requests/len(results))*100:.1f}%")
        print(f"Total execution time: {total_time:.2f}ms")
        print(f"Average response time: {avg_response_time:.2f}ms")
        
        # Race condition analysis
        print("\n🔍 RACE CONDITION ANALYSIS")
        print("=" * 40)
        
        status_codes = {}
        for result in results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        for code, count in status_codes.items():
            print(f"Status {code}: {count} requests")
        
        if successful_requests > 1:
            print("⚠️  POTENTIAL RACE CONDITION: Multiple requests succeeded!")
            print("   This might indicate that the same node was created multiple times.")
        elif successful_requests == 1:
            print("✅ GOOD: Only one request succeeded (expected behavior)")
            print("   Race condition is properly handled by the backend.")
        else:
            print("❌ UNEXPECTED: No requests succeeded")
            print("   Check if the API endpoint is working correctly.")
    
    async def test_different_payloads_race(self, concurrent_requests: int = 3):
        """
        Test race condition with slightly different payloads
        """
        base_payload = {
            "node_location": "Cibubur-SayuranPagi",
            "node_type": "Pembibitan", 
            "description": "This is an optional field."
        }
        
        # Create different payloads with different node_ids
        payloads = []
        for i in range(concurrent_requests):
            payload = base_payload.copy()
            payload["node_id"] = f"1a-{i+1}"  # Different node_ids
            payloads.append(payload)
        
        print(f"🔄 Testing race condition with different node_ids")
        print("=" * 60)
        
        # Create concurrent tasks with different payloads
        tasks = []
        for i, payload in enumerate(payloads):
            task = self.add_node_request(i + 1, payload)
            tasks.append(task)
        
        # Execute all requests simultaneously
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.time() - start_time) * 1000
        
        # Process and print results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                current_time = datetime.now()
                timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
                
                processed_results.append({
                    "request_id": i + 1,
                    "status_code": 0,
                    "success": False,
                    "error": str(result),
                    "payload": payloads[i],
                    "timestamp": timestamp
                })
            else:
                result["payload"] = payloads[i]
                processed_results.append(result)
        
        print("🔄 DIFFERENT PAYLOADS TEST RESULTS")
        print("=" * 60)
        
        for result in processed_results:
            status_icon = "✅" if result["success"] else "❌" 
            print(f"{status_icon} Request #{result['request_id']} (node_id: {result['payload']['node_id']}):")
            print(f"   Status: {result['status_code']}")
            print(f"   Time: {result.get('response_time_ms', 0)}ms")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            elif result.get("response_body"):
                response = result["response_body"]
                if isinstance(response, dict) and response.get("message"):
                    print(f"   Message: {response['message']}")
            print()
        
        successful_different = sum(1 for r in processed_results if r["success"])
        print(f"📊 Results: {successful_different}/{len(processed_results)} requests succeeded")
        
        return processed_results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main function to run the race condition tests"""
    
    # Check environment variables
    if not FIREBASE_API_KEY or not EMAIL or not PASSWORD:
        print("❌ ERROR: Missing environment variables!")
        print("Make sure these are set in your .env file:")
        print("- FIREBASE_API_KEY")
        print("- TESTING_LOGIN_EMAIL")
        print("- TESTING_LOGIN_PASSWORD")
        return
    
    tester = RaceConditionTest("https://lokasync.tech/api/v1")
    
    try:
        # Login first
        print("🔑 Logging in with Firebase...")
        token = tester.login_firebase(EMAIL, PASSWORD)
        print(f"✅ Login successful! Got token: {token[:20]}...")
        print()
        
        while True:
            print("\n🏁 LokaSync Race Condition Tester")
            print("=" * 50)
            options = input(
                "Choose a test:\n"
                "1. Test race condition - same payload (5 concurrent requests)\n"
                "2. Test race condition - same payload (10 concurrent requests)\n"
                "3. Test race condition - different node_ids (3 concurrent requests)\n"
                "4. Custom number of concurrent requests\n"
                "5. Exit\n"
                "Enter your choice: "
            )
            
            if options == "1":
                await tester.test_race_condition_add_node(5)
            
            elif options == "2":
                await tester.test_race_condition_add_node(10)
            
            elif options == "3":
                await tester.test_different_payloads_race(3)
            
            elif options == "4":
                try:
                    num_requests = int(input("Enter number of concurrent requests (1-20): "))
                    if 1 <= num_requests <= 20:
                        await tester.test_race_condition_add_node(num_requests)
                    else:
                        print("❌ Please enter a number between 1 and 20")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            elif options == "5":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()  # This will help debug any other errors
    
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🏁 LokaSync Race Condition Testing Tool")
    print("=" * 60)
    print("📧 Testing with email:", EMAIL)
    print("🌐 Target API:", "https://lokasync.tech/api/v1")
    print()
    
    asyncio.run(main())