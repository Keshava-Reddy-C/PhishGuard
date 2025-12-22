"""
Pre-Flight Check Script for PhishGuard
Verifies all dependencies, configurations, and files before running
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE} {text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {text}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.ENDC} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.ENDC} {text}")

def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version: {version_str} (OK)")
        return True
    else:
        print_error(f"Python version: {version_str} (Required: 3.8+)")
        return False

def check_dependencies():
    """Check if all required Python packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = {
        'django': 'Django',
        'rest_framework': 'djangorestframework',
        'corsheaders': 'django-cors-headers',
        'xgboost': 'xgboost',
        'sklearn': 'scikit-learn',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'bs4': 'beautifulsoup4',
        'requests': 'requests',
        'whois': 'python-whois',
        'dns': 'dnspython',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    installed = []
    
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print_success(f"{package} is installed")
            installed.append(package)
        except ImportError:
            print_error(f"{package} is NOT installed")
            missing.append(package)
    
    print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
    print(f"  Installed: {len(installed)}/{len(required_packages)}")
    
    if missing:
        print(f"\n{Colors.YELLOW}Missing packages:{Colors.ENDC}")
        for pkg in missing:
            print(f"  - {pkg}")
        print(f"\n{Colors.YELLOW}Install with:{Colors.ENDC}")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def check_project_structure():
    """Check if all required directories and files exist"""
    print_header("Checking Project Structure")
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    required_paths = [
        ('backend', True),
        ('backend/manage.py', False),
        ('backend/phishingUrlDetectionApp', True),
        ('backend/phishingUrlDetectionApp/views.py', False),
        ('backend/phishingUrlDetectionApp/external_apis.py', False),
        ('backend/phishingUrlDetectionApp/email_analysis_enhanced.py', False),
        ('backend/phishingUrlDetectionApp/feature.py', False),
        ('backend/phishingUrlDetectionApp/reputation_check.py', False),
        ('backend/phishingUrlDetectionBackend', True),
        ('backend/phishingUrlDetectionBackend/settings.py', False),
        ('backend/requirements.txt', False),
        ('ml', True),
        ('ml/train_enhanced_model.py', False),
        ('frontend', True),
        ('frontend/package.json', False),
        ('scripts', True),
    ]
    
    all_exist = True
    
    for path, is_dir in required_paths:
        full_path = project_root / path
        if is_dir:
            if full_path.is_dir():
                print_success(f"Directory exists: {path}")
            else:
                print_error(f"Directory missing: {path}")
                all_exist = False
        else:
            if full_path.is_file():
                print_success(f"File exists: {path}")
            else:
                print_error(f"File missing: {path}")
                all_exist = False
    
    return all_exist

def check_ml_models():
    """Check if ML models exist"""
    print_header("Checking ML Models")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    model_paths = [
        project_root / 'backend' / 'phishingUrlDetectionBackend' / 'model' / 'XGBoostClassifier.sav',
        project_root / 'backend' / 'phishingUrlDetectionApp' / 'ML' / 'model' / 'XGBoostClassifier.sav'
    ]
    
    model_found = False
    for model_path in model_paths:
        if model_path.exists():
            print_success(f"Model found: {model_path.relative_to(project_root)}")
            model_found = True
    
    if not model_found:
        print_warning("No trained ML model found")
        print(f"\n{Colors.YELLOW}Train a model with:{Colors.ENDC}")
        print(f"  cd ml")
        print(f"  python train_enhanced_model.py")
        print(f"\n{Colors.YELLOW}Note:{Colors.ENDC} System will create a fallback model on startup")
        return False
    
    return True

def check_api_configuration():
    """Check if API keys are configured"""
    print_header("Checking API Configuration")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_path = project_root / 'backend' / '.env'
    
    if not env_path.exists():
        print_warning(".env file not found")
        print(f"\n{Colors.YELLOW}Configure API keys with:{Colors.ENDC}")
        print(f"  python scripts/setup_api_keys.py")
        print(f"\n{Colors.YELLOW}Or manually:{Colors.ENDC}")
        print(f"  1. Copy backend/env.example to backend/.env")
        print(f"  2. Add your API keys")
        print(f"\n{Colors.YELLOW}Note:{Colors.ENDC} System will work without APIs but with reduced accuracy")
        return False
    
    print_success(".env file exists")
    
    # Check if it has content
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            
        # Check for key indicators
        has_gsb = 'GOOGLE_SAFEBROWSING_API_KEY' in content and 'your_' not in content.split('GOOGLE_SAFEBROWSING_API_KEY')[1].split('\n')[0]
        has_urlscan = 'URLSCAN_API_KEY' in content and 'your_' not in content.split('URLSCAN_API_KEY')[1].split('\n')[0] if 'URLSCAN_API_KEY' in content else False
        
        if has_gsb:
            print_success("Google Safe Browsing API key configured")
        else:
            print_warning("Google Safe Browsing API key not configured")
        
        if has_urlscan:
            print_success("URLScan.io API key configured")
        else:
            print_warning("URLScan.io API key not configured")
        
        if not (has_gsb or has_urlscan):
            print(f"\n{Colors.YELLOW}For best accuracy, configure at least:{Colors.ENDC}")
            print(f"  - Google Safe Browsing API")
            print(f"  - URLScan.io API")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error reading .env file: {e}")
        return False

def check_database():
    """Check if database is set up"""
    print_header("Checking Database")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / 'backend' / 'db.sqlite3'
    
    if db_path.exists():
        print_success("Database file exists")
        return True
    else:
        print_warning("Database file not found")
        print(f"\n{Colors.YELLOW}Initialize database with:{Colors.ENDC}")
        print(f"  cd backend")
        print(f"  python manage.py migrate")
        return False

def check_frontend_dependencies():
    """Check if frontend dependencies are installed"""
    print_header("Checking Frontend Dependencies")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    node_modules = project_root / 'frontend' / 'node_modules'
    
    if node_modules.exists() and node_modules.is_dir():
        print_success("Frontend dependencies installed (node_modules exists)")
        return True
    else:
        print_warning("Frontend dependencies not installed")
        print(f"\n{Colors.YELLOW}Install with:{Colors.ENDC}")
        print(f"  cd frontend")
        print(f"  npm install")
        return False

def print_summary(results):
    """Print final summary"""
    print_header("Pre-Flight Check Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: PASSED")
        else:
            print_error(f"{check}: FAILED")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.ENDC}")
    print(f"  Total Checks: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.ENDC}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.ENDC}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! Ready to run!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print(f"  1. Start backend:  cd backend && python manage.py runserver")
        print(f"  2. Start frontend: cd frontend && npm start")
        print(f"  3. Open browser:   http://localhost:3000")
        return True
    else:
        print(f"\n{Colors.YELLOW}⚠ Some checks failed. Please fix the issues above.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Critical:{Colors.ENDC}")
        print(f"  - Install missing Python dependencies")
        print(f"  - Ensure project structure is intact")
        print(f"\n{Colors.BOLD}Optional but Recommended:{Colors.ENDC}")
        print(f"  - Train ML model for better offline accuracy")
        print(f"  - Configure API keys for real-time detection")
        print(f"  - Install frontend dependencies")
        print(f"  - Run database migrations")
        return False

def main():
    """Run all checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE} PhishGuard Pre-Flight Check{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    
    results = {}
    
    # Run all checks
    results['Python Version'] = check_python_version()
    results['Python Dependencies'] = check_dependencies()
    results['Project Structure'] = check_project_structure()
    results['ML Models'] = check_ml_models()
    results['API Configuration'] = check_api_configuration()
    results['Database'] = check_database()
    results['Frontend Dependencies'] = check_frontend_dependencies()
    
    # Print summary
    all_passed = print_summary(results)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Check cancelled by user.{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)









