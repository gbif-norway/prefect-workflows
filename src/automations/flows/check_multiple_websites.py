"""
Website availability checker using Prefect flows.
"""

from prefect import flow, task
import requests
from typing import List, Dict, Any
import time
from urllib.parse import urlparse


@task
def check_website_validity(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check if a URL contains a valid website.
    
    Args:
        url: The URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing validation results
    """
    result = {
        "url": url,
        "is_valid": False,
        "status_code": None,
        "response_time": None,
        "error": None,
        "redirect_url": None
    }
    
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        # Validate URL format
        parsed = urlparse(url)
        if not parsed.netloc:
            result["error"] = "Invalid URL format"
            return result
            
        # Make the request
        start_time = time.time()
        response = requests.get(
            url, 
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'Prefect-Website-Checker/1.0'}
        )
        end_time = time.time()
        
        result["status_code"] = response.status_code
        result["response_time"] = round(end_time - start_time, 3)
        result["is_valid"] = 200 <= response.status_code < 400
        
        # Check if there was a redirect
        if response.url != url:
            result["redirect_url"] = response.url
            
        print(f"✅ {url} - Status: {response.status_code}, Time: {result['response_time']}s")
        
    except requests.exceptions.Timeout:
        result["error"] = f"Request timeout after {timeout} seconds"
        print(f"⏰ {url} - Timeout")
        
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection error - unable to reach the website"
        print(f"❌ {url} - Connection error")
        
    except requests.exceptions.RequestException as e:
        result["error"] = f"Request error: {str(e)}"
        print(f"❌ {url} - Request error: {str(e)}")
        
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ {url} - Unexpected error: {str(e)}")
        
    return result


@task
def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize the website check results.
    
    Args:
        results: List of website check results
        
    Returns:
        Summary statistics
    """
    total = len(results)
    valid = sum(1 for r in results if r["is_valid"])
    invalid = total - valid
    
    avg_response_time = None
    if valid > 0:
        valid_times = [r["response_time"] for r in results if r["response_time"] is not None]
        if valid_times:
            avg_response_time = round(sum(valid_times) / len(valid_times), 3)
    
    summary = {
        "total_checked": total,
        "valid_websites": valid,
        "invalid_websites": invalid,
        "success_rate": round((valid / total) * 100, 2) if total > 0 else 0,
        "average_response_time": avg_response_time
    }
    
    print(f"\n📊 Summary:")
    print(f"   Total websites checked: {summary['total_checked']}")
    print(f"   Valid websites: {summary['valid_websites']}")
    print(f"   Invalid websites: {summary['invalid_websites']}")
    print(f"   Success rate: {summary['success_rate']}%")
    if avg_response_time:
        print(f"   Average response time: {avg_response_time}s")
    
    return summary


@flow(name="url_check_flow")
def check_multiple_websites(urls: List[str], timeout: int = 10) -> Dict[str, Any]:
    """
    Flow to check the availability of multiple websites.
    
    Args:
        urls: List of URLs to check
        timeout: Request timeout in seconds for each URL
        
    Returns:
        Complete results including individual checks and summary
    """
    print(f"🌐 Starting website availability check for {len(urls)} URLs...")
    print(f"⏱️  Timeout set to {timeout} seconds per request\n")
    
    # Check each website
    results = []
    for url in urls:
        result = check_website_validity(url, timeout)
        results.append(result)
    
    # Generate summary
    summary = summarize_results(results)
    
    return {
        "individual_results": results,
        "summary": summary,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    # Example usage with some popular websites
    test_urls = [
        "https://www.google.com",
        "https://www.github.com", 
        "https://www.python.org",
        "https://prefect.io",
        "invalid-url-that-should-fail.com",
        "https://httpstat.us/404",  # This will return 404
        "https://httpstat.us/500"   # This will return 500
    ]
    
    result = check_multiple_websites(test_urls, timeout=5) 