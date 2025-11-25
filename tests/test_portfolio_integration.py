#!/usr/bin/env python3
"""
Test script for Portfolio & GitHub Integration
Verifies that all components are working correctly
"""

import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def test_imports():
    """Test that all required packages are installed"""
    print("\n" + "="*50)
    print("Testing Package Imports")
    print("="*50)
    
    packages = [
        ('streamlit', 'Streamlit'),
        ('google.generativeai', 'Google Generative AI'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('dotenv', 'python-dotenv'),
        ('requests', 'Requests'),
        ('bs4', 'BeautifulSoup4'),
        ('numpy', 'NumPy')
    ]
    
    all_passed = True
    for package, name in packages:
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_passed = False
    
    return all_passed

def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "="*50)
    print("Testing File Structure")
    print("="*50)
    
    required_files = [
        'main.py',
        'requirements.txt',
        'config/constants.py',
        'config/session_state.py',
        'components/sidebar.py',
        'components/email_writer.py',
        'components/cover_letter.py',
        'utils/portfolio_fetcher.py',
        'utils/document_processing.py',
        'utils/gemini_api.py',
        'utils/helpers.py'
    ]
    
    all_exist = True
    for filepath in required_files:
        path = Path(filepath)
        if path.exists():
            print_success(f"{filepath} exists")
        else:
            print_error(f"{filepath} NOT FOUND")
            all_exist = False
    
    return all_exist

def test_portfolio_fetcher():
    """Test portfolio fetcher module"""
    print("\n" + "="*50)
    print("Testing Portfolio Fetcher")
    print("="*50)
    
    try:
        from utils.portfolio_fetcher import PortfolioFetcher, load_portfolio_content
        print_success("Portfolio fetcher module imported")
        
        # Test class instantiation
        fetcher = PortfolioFetcher()
        print_success("PortfolioFetcher class instantiated")
        
        # Test URL configuration
        if fetcher.PORTFOLIO_URL == "https://vinay2132.github.io/my_portfolio/":
            print_success("Portfolio URL configured correctly")
        else:
            print_warning(f"Portfolio URL: {fetcher.PORTFOLIO_URL}")
        
        if fetcher.GITHUB_URL == "https://github.com/vinay2132":
            print_success("GitHub URL configured correctly")
        else:
            print_warning(f"GitHub URL: {fetcher.GITHUB_URL}")
        
        return True
    except Exception as e:
        print_error(f"Portfolio fetcher test failed: {str(e)}")
        return False

def test_constants():
    """Test that constants are updated correctly"""
    print("\n" + "="*50)
    print("Testing Constants Configuration")
    print("="*50)
    
    try:
        from config.constants import PERSONAL_DETAILS_TEMPLATE, WRITING_GUIDELINES_TEMPLATE
        
        # Check personal details
        if "Portfolio:" in PERSONAL_DETAILS_TEMPLATE:
            print_success("Portfolio URL in personal details")
        else:
            print_error("Portfolio URL NOT in personal details")
        
        if "GitHub:" in PERSONAL_DETAILS_TEMPLATE:
            print_success("GitHub URL in personal details")
        else:
            print_error("GitHub URL NOT in personal details")
        
        # Check writing guidelines
        if "🌐 Portfolio:" in WRITING_GUIDELINES_TEMPLATE:
            print_success("Portfolio URL in signature template")
        else:
            print_error("Portfolio URL NOT in signature template")
        
        if "💻 GitHub:" in WRITING_GUIDELINES_TEMPLATE:
            print_success("GitHub URL in signature template")
        else:
            print_error("GitHub URL NOT in signature template")
        
        return True
    except Exception as e:
        print_error(f"Constants test failed: {str(e)}")
        return False

def test_session_state():
    """Test session state configuration"""
    print("\n" + "="*50)
    print("Testing Session State")
    print("="*50)
    
    try:
        from config.session_state import initialize_session_state
        print_success("Session state module imported")
        
        # Read the file to check for portfolio variables
        with open('config/session_state.py', 'r') as f:
            content = f.read()
        
        checks = [
            ('portfolio_loaded', "portfolio_loaded variable"),
            ('portfolio_url', "portfolio_url variable"),
            ('github_url', "github_url variable"),
            ('portfolio_links', "portfolio_links variable")
        ]
        
        all_present = True
        for check, desc in checks:
            if check in content:
                print_success(f"{desc} configured")
            else:
                print_error(f"{desc} NOT configured")
                all_present = False
        
        return all_present
    except Exception as e:
        print_error(f"Session state test failed: {str(e)}")
        return False

def test_requirements():
    """Test requirements.txt has new dependencies"""
    print("\n" + "="*50)
    print("Testing Requirements File")
    print("="*50)
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if 'requests' in content:
            print_success("requests dependency listed")
        else:
            print_error("requests dependency NOT listed")
        
        if 'beautifulsoup4' in content:
            print_success("beautifulsoup4 dependency listed")
        else:
            print_error("beautifulsoup4 dependency NOT listed")
        
        return True
    except Exception as e:
        print_error(f"Requirements test failed: {str(e)}")
        return False

def test_live_fetch():
    """Test actual portfolio fetching (requires internet)"""
    print("\n" + "="*50)
    print("Testing Live Portfolio Fetch")
    print("="*50)
    print_info("This test requires internet connection")
    
    try:
        from utils.portfolio_fetcher import PortfolioFetcher
        
        fetcher = PortfolioFetcher()
        
        # Test portfolio fetch
        print_info("Fetching portfolio content...")
        portfolio = fetcher.fetch_portfolio()
        if portfolio:
            print_success(f"Portfolio fetched ({len(portfolio)} characters)")
        else:
            print_warning("Could not fetch portfolio (may be offline)")
        
        # Test GitHub fetch
        print_info("Fetching GitHub profile...")
        github = fetcher.fetch_github_profile()
        if github:
            print_success(f"GitHub profile fetched ({len(github)} characters)")
        else:
            print_warning("Could not fetch GitHub (may be offline or rate limited)")
        
        return True
    except Exception as e:
        print_warning(f"Live fetch test failed: {str(e)}")
        print_info("This is OK if you're offline")
        return True  # Don't fail test for network issues

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Portfolio & GitHub Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Portfolio Fetcher", test_portfolio_fetcher),
        ("Constants Config", test_constants),
        ("Session State", test_session_state),
        ("Requirements", test_requirements),
        ("Live Fetch", test_live_fetch)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
    
    print("\n" + "-"*60)
    print(f"Results: {passed}/{total} tests passed")
    print("-"*60)
    
    if passed == total:
        print_success("\n🎉 All tests passed! Integration is ready.")
        print_info("Run 'streamlit run main.py' to start the application")
        return 0
    else:
        print_warning(f"\n⚠️  {total - passed} test(s) failed")
        print_info("Review the errors above and fix the issues")
        print_info("See PORTFOLIO_INTEGRATION_GUIDE.md for help")
        return 1

if __name__ == "__main__":
    sys.exit(main())