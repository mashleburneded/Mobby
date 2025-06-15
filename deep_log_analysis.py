#!/usr/bin/env python3
"""
Deep Log Analysis - Extract and categorize ALL real problems from logs
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

def analyze_log_content(log_content):
    """Analyze log content and extract all problems"""
    
    problems = {
        "critical_errors": [],
        "api_errors": [],
        "format_errors": [],
        "missing_methods": [],
        "database_errors": [],
        "intent_recognition_failures": [],
        "response_generation_failures": [],
        "import_errors": [],
        "configuration_errors": [],
        "performance_issues": [],
        "data_processing_errors": [],
        "authentication_errors": []
    }
    
    lines = log_content.split('\n')
    
    for i, line in enumerate(lines):
        if any(keyword in line.upper() for keyword in ['ERROR', 'FAILED', 'EXCEPTION', 'WARNING']):
            
            # API Authentication Errors
            if 'Invalid API Key' in line or '401 Unauthorized' in line:
                problems["authentication_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Format String Errors
            elif 'unsupported format string' in line:
                problems["format_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Missing Method Errors
            elif 'has no attribute' in line or 'method not found' in line:
                problems["missing_methods"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Database Errors
            elif any(db_keyword in line.lower() for db_keyword in ['database', 'sqlite', 'sql']):
                problems["database_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # API Request Errors
            elif any(api_keyword in line.lower() for api_keyword in ['api error', 'http', 'request failed', 'connection']):
                problems["api_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Intent Recognition Issues
            elif 'intent mismatch' in line.lower() or 'intent recognition' in line.lower():
                problems["intent_recognition_failures"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Response Generation Issues
            elif 'response generation' in line.lower() or 'no response' in line.lower():
                problems["response_generation_failures"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Import Errors
            elif 'import' in line.lower() and ('error' in line.lower() or 'failed' in line.lower()):
                problems["import_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Configuration Errors
            elif any(config_keyword in line.lower() for config_keyword in ['config', 'environment', 'missing']):
                problems["configuration_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Performance Issues
            elif any(perf_keyword in line for perf_keyword in ['timeout', 'slow', 'taking too long']):
                problems["performance_issues"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Data Processing Errors
            elif any(data_keyword in line.lower() for data_keyword in ['parsing', 'json', 'data', 'processing']):
                problems["data_processing_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
            
            # Catch-all for other critical errors
            elif 'ERROR' in line.upper() and not any(problems[category] for category in problems if line.strip() in [p["error"] for p in problems[category]]):
                problems["critical_errors"].append({
                    "line": i+1,
                    "error": line.strip(),
                    "context": lines[max(0, i-2):i+3] if i < len(lines)-2 else lines[i:i+1]
                })
    
    return problems

def analyze_specific_issues(log_content):
    """Analyze specific issues mentioned by user"""
    
    specific_issues = {
        "message_saving": False,
        "intent_mapping": False,
        "tool_selection": False,
        "conversation_intelligence": False,
        "nlp_patterns": False,
        "proper_responses": False
    }
    
    # Check if messages are being saved
    if "storing message for learning" in log_content or "stream_message" in log_content:
        specific_issues["message_saving"] = True
    
    # Check intent mapping
    intent_patterns = ["intent_recognition", "analyze_intent", "enhanced_intent"]
    if any(pattern in log_content for pattern in intent_patterns):
        specific_issues["intent_mapping"] = True
    
    # Check tool selection
    tool_patterns = ["tool_call", "function_call", "api_call"]
    if any(pattern in log_content for pattern in tool_patterns):
        specific_issues["tool_selection"] = True
    
    # Check conversation intelligence
    if "conversation_intelligence" in log_content or "ConversationIntelligence" in log_content:
        specific_issues["conversation_intelligence"] = True
    
    # Check NLP patterns
    if "nlp_processor" in log_content or "natural_language" in log_content:
        specific_issues["nlp_patterns"] = True
    
    # Check proper responses (not just fallbacks)
    if "fallback" not in log_content and "response" in log_content:
        specific_issues["proper_responses"] = True
    
    return specific_issues

def main():
    """Run deep log analysis"""
    
    # Get the most recent log content from our test
    print("🔍 DEEP LOG ANALYSIS - EXTRACTING ALL REAL PROBLEMS")
    print("=" * 60)
    
    # Since we don't have a log file, let's run a quick test to generate logs
    import subprocess
    import tempfile
    
    try:
        # Run a quick test to capture logs
        result = subprocess.run([
            sys.executable, "live_telegram_test.py"
        ], capture_output=True, text=True, timeout=30, cwd="/workspace/mody")
        
        log_content = result.stdout + result.stderr
        
    except subprocess.TimeoutExpired:
        # Get partial output
        log_content = result.stdout + result.stderr if 'result' in locals() else ""
    except Exception as e:
        print(f"❌ Could not run test: {e}")
        return
    
    if not log_content:
        print("❌ No log content captured")
        return
    
    # Analyze problems
    problems = analyze_log_content(log_content)
    specific_issues = analyze_specific_issues(log_content)
    
    # Report findings
    print("\n🚨 CRITICAL PROBLEMS FOUND:")
    print("=" * 40)
    
    total_problems = sum(len(problems[category]) for category in problems)
    print(f"📊 Total Problems Detected: {total_problems}")
    
    for category, issues in problems.items():
        if issues:
            print(f"\n🔴 {category.upper().replace('_', ' ')} ({len(issues)} issues):")
            for issue in issues[:3]:  # Show first 3 of each type
                print(f"   Line {issue['line']}: {issue['error']}")
            if len(issues) > 3:
                print(f"   ... and {len(issues) - 3} more")
    
    print("\n🎯 SPECIFIC FUNCTIONALITY ANALYSIS:")
    print("=" * 40)
    
    for feature, working in specific_issues.items():
        status = "✅ DETECTED" if working else "❌ NOT WORKING"
        print(f"{status} {feature.replace('_', ' ').title()}")
    
    # Extract specific error patterns
    print("\n🔍 SPECIFIC ERROR PATTERNS:")
    print("=" * 40)
    
    error_patterns = [
        ("Format String Errors", r"unsupported format string"),
        ("API Authentication", r"Invalid API Key|401 Unauthorized"),
        ("Missing Methods", r"has no attribute|method not found"),
        ("Database Issues", r"database.*error|sqlite.*error"),
        ("Import Failures", r"ImportError|ModuleNotFoundError"),
        ("Response Failures", r"No response|response.*failed"),
        ("Intent Mismatches", r"Intent mismatch|intent.*failed")
    ]
    
    for pattern_name, pattern in error_patterns:
        matches = re.findall(pattern, log_content, re.IGNORECASE)
        if matches:
            print(f"🔴 {pattern_name}: {len(matches)} occurrences")
            for match in matches[:2]:
                print(f"   - {match}")
    
    # Save detailed analysis
    with open("deep_log_analysis_report.txt", "w") as f:
        f.write("DEEP LOG ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Problems: {total_problems}\n\n")
        
        for category, issues in problems.items():
            if issues:
                f.write(f"{category.upper()}:\n")
                for issue in issues:
                    f.write(f"  Line {issue['line']}: {issue['error']}\n")
                    f.write(f"  Context: {issue['context']}\n\n")
        
        f.write("\nFULL LOG CONTENT:\n")
        f.write("=" * 30 + "\n")
        f.write(log_content)
    
    print(f"\n📄 Full analysis saved to: deep_log_analysis_report.txt")
    
    # Provide honest assessment
    if total_problems > 10:
        print("\n🚨 VERDICT: SYSTEM HAS SERIOUS ISSUES")
        print("   - Multiple critical errors detected")
        print("   - Core functionality not working properly")
        print("   - Requires comprehensive fixes")
    elif total_problems > 5:
        print("\n⚠️ VERDICT: SYSTEM NEEDS SIGNIFICANT WORK")
        print("   - Several important issues detected")
        print("   - Some functionality working but unreliable")
    else:
        print("\n✅ VERDICT: SYSTEM MOSTLY FUNCTIONAL")
        print("   - Minor issues detected")
        print("   - Core functionality appears to work")

if __name__ == "__main__":
    main()