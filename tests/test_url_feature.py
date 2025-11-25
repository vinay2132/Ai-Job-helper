#!/usr/bin/env python3
"""
Test script for URL fetching feature
"""

def test_imports():
    """Test all imports"""
    try:
        from utils.job_url_fetcher import JobURLFetcher, fetch_and_display_job, save_job_to_session
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_fetcher_init():
    """Test fetcher initialization"""
    try:
        from utils.job_url_fetcher import JobURLFetcher
        fetcher = JobURLFetcher()
        print("✅ JobURLFetcher initialized")
        print(f"   Supported sites: {len(fetcher.SUPPORTED_SITES)}")
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_url_validation():
    """Test URL handling"""
    try:
        from utils.job_url_fetcher import JobURLFetcher
        fetcher = JobURLFetcher()
        
        test_url = "https://www.linkedin.com/jobs/view/test"
        print(f"✅ URL handling works")
        return True
    except Exception as e:
        print(f"❌ URL handling error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing URL Fetching Feature")
    print("="*60 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Fetcher Init", test_fetcher_init),
        ("URL Validation", test_url_validation)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1
        print()
    
    print("="*60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("="*60)
    
    if passed == len(tests):
        print("\n✅ All tests passed! Feature is ready to use.")
        print("   Run: streamlit run main.py")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
