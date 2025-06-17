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

class RateLimitTest:
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
    
    async def single_request(self, request_id: int, endpoint: str = "node/") -> Dict[str, Any]:
        """
        Single request to test rate limiting
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = await self.client.get(endpoint, headers=headers)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Use datetime for timestamp
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
            
            result = {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "timestamp": timestamp,
                "success": response.status_code == 200,
                "rate_limited": response.status_code == 429
            }
            
            # Check for rate limit headers
            rate_limit_headers = {
                "x-ratelimit-limit": response.headers.get("X-RateLimit-Limit"),
                "x-ratelimit-remaining": response.headers.get("X-RateLimit-Remaining"),
                "x-ratelimit-reset": response.headers.get("X-RateLimit-Reset"),
                "retry-after": response.headers.get("Retry-After")
            }
            result["rate_limit_headers"] = rate_limit_headers
            
            try:
                result["response_body"] = response.json()
            except:
                result["response_body"] = response.text
                
            return result
            
        except Exception as e:
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S.") + f"{current_time.microsecond // 1000:03d}"
            
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time_ms": 0,
                "timestamp": timestamp,
                "success": False,
                "rate_limited": False,
                "error": str(e),
                "response_body": None,
                "rate_limit_headers": {}
            }
    
    async def test_rate_limit_burst(self, total_requests: int = 10, delay_between: float = 0.1) -> List[Dict[str, Any]]:
        """
        Test rate limiting by sending rapid requests
        """
        print(f"⚡ Starting rate limit test with {total_requests} requests")
        print(f"⏱️  Delay between requests: {delay_between}s")
        print(f"🎯 Target endpoint: {self.base_url}/node/")
        print("=" * 80)
        
        results = []
        start_time = time.time()
        
        for i in range(total_requests):
            result = await self.single_request(i + 1, "node/")
            results.append(result)
            
            # Print real-time status
            status_icon = "✅" if result["success"] else "⚠️" if result["rate_limited"] else "❌"
            print(f"{status_icon} Request #{i+1}: {result['status_code']} ({result['response_time_ms']}ms)")
            
            # Check if we got rate limited
            if result["rate_limited"]:
                print(f"   🚨 RATE LIMITED! Retry-After: {result['rate_limit_headers'].get('retry-after', 'N/A')}s")
            
            # Add delay between requests (except for the last one)
            if i < total_requests - 1:
                await asyncio.sleep(delay_between)
        
        total_time = (time.time() - start_time) * 1000
        
        # Print detailed results
        self.print_rate_limit_results(results, total_time)
        
        return results
    
    async def test_rate_limit_concurrent(self, concurrent_requests: int = 15) -> List[Dict[str, Any]]:
        """
        Test rate limiting with concurrent requests
        """
        print(f"🚀 Starting concurrent rate limit test with {concurrent_requests} simultaneous requests")
        print(f"🎯 Target endpoint: {self.base_url}/node/")
        print("=" * 80)
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_requests):
            task = self.single_request(i + 1, "node/")
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
                    "rate_limited": False,
                    "error": str(result),
                    "response_body": None,
                    "rate_limit_headers": {}
                })
            else:
                processed_results.append(result)
        
        # Print results
        self.print_rate_limit_results(processed_results, total_time)
        
        return processed_results
    
    def print_rate_limit_results(self, results: List[Dict[str, Any]], total_time: float):
        """Print formatted results of the rate limit test"""
        
        print("\n⚡ RATE LIMIT TEST RESULTS")
        print("=" * 80)
        
        # Individual request results
        for result in results:
            if result["success"]:
                status_icon = "✅"
                status_text = "SUCCESS"
            elif result["rate_limited"]:
                status_icon = "🚨"
                status_text = "RATE LIMITED"
            else:
                status_icon = "❌"
                status_text = "ERROR"
            
            print(f"{status_icon} Request #{result['request_id']} - {status_text}:")
            print(f"   Status: {result['status_code']}")
            print(f"   Time: {result['response_time_ms']}ms")
            print(f"   Timestamp: {result['timestamp']}")
            
            # Show rate limit headers if available
            headers = result.get("rate_limit_headers", {})
            if any(headers.values()):
                print(f"   Rate Limit Info:")
                if headers.get("x-ratelimit-limit"):
                    print(f"     Limit: {headers['x-ratelimit-limit']}")
                if headers.get("x-ratelimit-remaining"):
                    print(f"     Remaining: {headers['x-ratelimit-remaining']}")
                if headers.get("retry-after"):
                    print(f"     Retry After: {headers['retry-after']}s")
            
            if result.get("error"):
                print(f"   Error: {result['error']}")
            elif result.get("response_body") and result["rate_limited"]:
                response = result["response_body"]
                if isinstance(response, dict):
                    if response.get("message"):
                        print(f"   Message: {response['message']}")
                    if response.get("detail"):
                        print(f"   Detail: {response['detail']}")
            print()
        
        # Summary statistics
        successful_requests = sum(1 for r in results if r["success"])
        rate_limited_requests = sum(1 for r in results if r["rate_limited"])
        error_requests = len(results) - successful_requests - rate_limited_requests
        
        if successful_requests > 0:
            avg_response_time = sum(r["response_time_ms"] for r in results if r["success"]) / successful_requests
        else:
            avg_response_time = 0
        
        print("📊 SUMMARY")
        print("=" * 40)
        print(f"Total requests: {len(results)}")
        print(f"Successful: {successful_requests}")
        print(f"Rate Limited (429): {rate_limited_requests}")
        print(f"Errors: {error_requests}")
        print(f"Success rate: {(successful_requests/len(results))*100:.1f}%")
        print(f"Rate limit rate: {(rate_limited_requests/len(results))*100:.1f}%")
        print(f"Total execution time: {total_time:.2f}ms")
        print(f"Average response time: {avg_response_time:.2f}ms")
        
        # Rate limiting analysis
        print("\n🔍 RATE LIMITING ANALYSIS")
        print("=" * 40)
        
        status_codes = {}
        for result in results:
            code = result["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        for code, count in status_codes.items():
            if code == 200:
                print(f"✅ Status {code} (OK): {count} requests")
            elif code == 429:
                print(f"🚨 Status {code} (Rate Limited): {count} requests")
            elif code == 0:
                print(f"❌ Status {code} (Network Error): {count} requests")
            else:
                print(f"⚠️  Status {code}: {count} requests")
        
        if rate_limited_requests > 0:
            print(f"✅ GOOD: Rate limiting is working! {rate_limited_requests} requests were rate limited.")
            
            # Find the first rate limited request
            first_rate_limited = None
            for result in results:
                if result["rate_limited"]:
                    first_rate_limited = result
                    break
            
            if first_rate_limited:
                print(f"   First rate limit hit at request #{first_rate_limited['request_id']}")
                retry_after = first_rate_limited["rate_limit_headers"].get("retry-after")
                if retry_after:
                    print(f"   Retry-After header: {retry_after}s")
        else:
            print("⚠️  No rate limiting detected. Either:")
            print("   1. Rate limits are very high")
            print("   2. Rate limiting is not configured")
            print("   3. Not enough requests to trigger limits")
    
    async def test_rate_limit_with_delay(self, requests_per_batch: int = 5, batches: int = 3, delay_between_batches: float = 2.0):
        """
        Test rate limiting with batches and delays
        """
        print(f"📊 Testing rate limits with batches")
        print(f"   Requests per batch: {requests_per_batch}")
        print(f"   Number of batches: {batches}")
        print(f"   Delay between batches: {delay_between_batches}s")
        print("=" * 80)
        
        all_results = []
        
        for batch_num in range(batches):
            print(f"\n🔄 Batch {batch_num + 1}/{batches}")
            
            # Send batch of requests
            batch_tasks = []
            for i in range(requests_per_batch):
                request_id = batch_num * requests_per_batch + i + 1
                task = self.single_request(request_id, "node/")
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            
            # Print batch summary
            batch_success = sum(1 for r in batch_results if r["success"])
            batch_rate_limited = sum(1 for r in batch_results if r["rate_limited"])
            
            print(f"   Batch results: {batch_success} success, {batch_rate_limited} rate limited")
            
            # Wait between batches (except for the last one)
            if batch_num < batches - 1:
                print(f"   ⏳ Waiting {delay_between_batches}s before next batch...")
                await asyncio.sleep(delay_between_batches)
        
        # Final summary
        print(f"\n📈 OVERALL BATCH TEST RESULTS")
        print("=" * 60)
        
        total_success = sum(1 for r in all_results if r["success"])
        total_rate_limited = sum(1 for r in all_results if r["rate_limited"])
        
        print(f"Total requests: {len(all_results)}")
        print(f"Total successful: {total_success}")
        print(f"Total rate limited: {total_rate_limited}")
        
        return all_results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main function to run the rate limit tests"""
    
    # Check environment variables
    if not FIREBASE_API_KEY or not EMAIL or not PASSWORD:
        print("❌ ERROR: Missing environment variables!")
        print("Make sure these are set in your .env file:")
        print("- FIREBASE_API_KEY")
        print("- TESTING_LOGIN_EMAIL")
        print("- TESTING_LOGIN_PASSWORD")
        return
    
    tester = RateLimitTest("https://lokasync.tech/api/v1")
    
    try:
        # Login first
        print("🔑 Logging in with Firebase...")
        token = tester.login_firebase(EMAIL, PASSWORD)
        print(f"✅ Login successful! Got token: {token[:20]}...")
        print()
        
        while True:
            print("\n⚡ LokaSync Rate Limit Tester")
            print("=" * 50)
            options = input(
                "Choose a test:\n"
                "1. Rapid requests test (10 requests with 0.1s delay)\n"
                "2. Burst test (15 concurrent requests)\n"
                "3. Heavy load test (50 requests with 0.05s delay)\n"
                "4. Batch test with recovery (3 batches of 5 requests)\n"
                "5. Custom rapid test\n"
                "6. Custom concurrent test\n"
                "7. Exit\n"
                "Enter your choice: "
            )
            
            if options == "1":
                await tester.test_rate_limit_burst(10, 0.1)
            
            elif options == "2":
                await tester.test_rate_limit_concurrent(15)
            
            elif options == "3":
                await tester.test_rate_limit_burst(50, 0.05)
            
            elif options == "4":
                await tester.test_rate_limit_with_delay(5, 3, 2.0)
            
            elif options == "5":
                try:
                    num_requests = int(input("Enter number of requests (1-100): "))
                    delay = float(input("Enter delay between requests in seconds (0-5): "))
                    if 1 <= num_requests <= 100 and 0 <= delay <= 5:
                        await tester.test_rate_limit_burst(num_requests, delay)
                    else:
                        print("❌ Invalid range. Requests: 1-100, Delay: 0-5s")
                except ValueError:
                    print("❌ Please enter valid numbers")
            
            elif options == "6":
                try:
                    num_requests = int(input("Enter number of concurrent requests (1-50): "))
                    if 1 <= num_requests <= 50:
                        await tester.test_rate_limit_concurrent(num_requests)
                    else:
                        print("❌ Please enter a number between 1 and 50")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            elif options == "7":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await tester.close()

if __name__ == "__main__":
    print("⚡ LokaSync Rate Limit Testing Tool")
    print("=" * 60)
    print("📧 Testing with email:", EMAIL)
    print("🌐 Target API:", "https://lokasync.tech/api/v1/node/")
    print()
    
    asyncio.run(main())