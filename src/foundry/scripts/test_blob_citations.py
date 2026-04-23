"""
Test script to verify search index and document upload.

Usage:
    python test_blob_citations.py

This script will:
1. Check search index configuration
2. Verify documents are uploaded to search index
3. Test search functionality
4. Validate knowledge base access
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent
sys.path.insert(0, str(src_dir))

# Load environment from azd + project .env
from foundry.scripts.load_env import load_all_env, get_data_folder
load_all_env()

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

# ============================================================================
# Configuration
# ============================================================================

AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
SOLUTION_NAME = os.getenv("SOLUTION_NAME") or os.getenv("AZURE_ENV_NAME", "demo")

INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX") or f"{SOLUTION_NAME}-documents"

if not AZURE_AI_SEARCH_ENDPOINT:
    print("ERROR: AZURE_AI_SEARCH_ENDPOINT not set")
    sys.exit(1)

# Get data folder - always use src/foundry/data
try:
    data_dir = Path(get_data_folder())
    config_dir = data_dir / "config"
    if not config_dir.exists():
        config_dir = data_dir
except Exception as e:
    print(f"ERROR: Could not access data folder: {e}")
    sys.exit(1)

print(f"\n{'='*60}")
print("Test Search Index and Document Upload")
print(f"{'='*60}")
print(f"Search Endpoint: {AZURE_AI_SEARCH_ENDPOINT}")
print(f"Index Name: {INDEX_NAME}")

# ============================================================================
# Test Functions
# ============================================================================

def test_search_index():
    """Test search index and document access."""
    print("\n1. Testing Search Index Access...")
    
    try:
        credential = DefaultAzureCredential()
        search_client = SearchClient(AZURE_AI_SEARCH_ENDPOINT, INDEX_NAME, credential)
        
        # Test basic search
        results = search_client.search("*", top=5)
        documents = list(results)
        
        print(f"   [OK] Search index '{INDEX_NAME}' accessible")
        print(f"   [OK] Found {len(documents)} document(s) in index")
        
        # Show sample documents
        for i, doc in enumerate(documents[:3]):
            print(f"        Document {i+1}:")
            print(f"          ID: {doc.get('id', 'N/A')}")
            print(f"          Source: {doc.get('source', 'N/A')}")
            print(f"          Page: {doc.get('page_number', 'N/A')}")
            print(f"          Content: {doc.get('content', '')[:100]}...")
        
        return len(documents) > 0
        
    except Exception as e:
        print(f"   [FAIL] Search index test failed: {e}")
        return False

def test_search_functionality():
    """Test search functionality with a simple query."""
    print("\n2. Testing Search Functionality...")
    
    try:
        credential = DefaultAzureCredential()
        search_client = SearchClient(AZURE_AI_SEARCH_ENDPOINT, INDEX_NAME, credential)
        
        # Test semantic search
        results = search_client.search(
            "policy",
            query_type="semantic",
            semantic_configuration_name="default-semantic",
            top=3
        )
        documents = list(results)
        
        print(f"   [OK] Semantic search returned {len(documents)} results")
        
        # Test filter by page number
        results = search_client.search(
            "*",
            filter="page_number eq 1",
            top=3
        )
        filtered_docs = list(results)
        
        print(f"   [OK] Filtered search (page 1) returned {len(filtered_docs)} results")
        
        return True
        
    except Exception as e:
        print(f"   [FAIL] Search functionality test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration files exist."""
    print("\n3. Testing Configuration Files...")
    
    success = True
    
    # Check search_ids.json
    search_ids_path = config_dir / "search_ids.json"
    if search_ids_path.exists():
        print(f"   [OK] Found search_ids.json")
        with open(search_ids_path) as f:
            search_data = json.load(f)
            print(f"        Index: {search_data.get('index_name', 'N/A')}")
            print(f"        KB Name: {search_data.get('knowledge_base_name', 'N/A')}")
            print(f"        Documents: {search_data.get('total_documents', 'N/A')}")
    else:
        print(f"   [WARN] search_ids.json not found at {search_ids_path}")
        success = False
    
    # Check other config files
    config_files = ["agent_ids.json", "ontology_config.json"]
    for file in config_files:
        file_path = config_dir / file
        if file_path.exists():
            print(f"   [OK] Found {file}")
        else:
            print(f"   [WARN] {file} not found")
    
    return success

# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """Run all tests."""
    
    tests = [
        ("Search Index", test_search_index),
        ("Search Functionality", test_search_functionality),
        ("Configuration Files", test_configuration_files),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   [ERROR] {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Search index is working correctly.")
        print("\nNext steps:")
        print("  - Run 06_create_agent_no_sql.py to create your agent")
        print("  - Test your agent in the Azure AI Foundry portal")
    else:
        print("\n❌ Some tests failed. Check the configuration:")
        print("  - Ensure 05_upload_to_search.py completed successfully")
        print("  - Verify Azure AI Search endpoint is accessible")
        print("  - Check that documents were uploaded to the search index")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)