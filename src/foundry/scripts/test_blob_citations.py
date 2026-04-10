"""
Test script to verify blob storage integration and document citations.

Usage:
    python test_blob_citations.py

This script will:
1. Check blob storage configuration
2. Verify documents are uploaded to blob storage
3. Test search index includes blob URLs
4. Validate knowledge base can access citations
"""

import os
import sys
import json
from pathlib import Path

# Load environment from azd + project .env
from foundry.scripts.load_env import load_all_env, get_data_folder
load_all_env()

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient

# ============================================================================
# Configuration
# ============================================================================

AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_STORAGE_BLOB_ENDPOINT = os.getenv("AZURE_STORAGE_BLOB_ENDPOINT") 
SOLUTION_NAME = os.getenv("SOLUTION_NAME") or os.getenv("AZURE_ENV_NAME", "demo")

INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX") or f"{SOLUTION_NAME}-documents"
BLOB_CONTAINER_NAME = f"{SOLUTION_NAME}-documents"

if not AZURE_AI_SEARCH_ENDPOINT:
    print("ERROR: AZURE_AI_SEARCH_ENDPOINT not set")
    sys.exit(1)

if not AZURE_STORAGE_BLOB_ENDPOINT:
    print("ERROR: AZURE_STORAGE_BLOB_ENDPOINT not set")
    sys.exit(1)

# Get data folder
try:
    data_dir = Path(get_data_folder())
    config_dir = data_dir / "config"
    if not config_dir.exists():
        config_dir = data_dir
except ValueError:
    print("ERROR: DATA_FOLDER not set")
    sys.exit(1)

print(f"\n{'='*60}")
print("Test Blob Storage Citations Integration")
print(f"{'='*60}")
print(f"Search Endpoint: {AZURE_AI_SEARCH_ENDPOINT}")
print(f"Storage Endpoint: {AZURE_STORAGE_BLOB_ENDPOINT}")
print(f"Index Name: {INDEX_NAME}")
print(f"Container Name: {BLOB_CONTAINER_NAME}")

# ============================================================================
# Test Functions
# ============================================================================

def test_blob_storage():
    """Test blob storage container and file access."""
    print("\n1. Testing Blob Storage Access...")
    
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(AZURE_STORAGE_BLOB_ENDPOINT, credential)
        
        # Check container exists
        container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
        container_props = container_client.get_container_properties()
        print(f"   [OK] Container '{BLOB_CONTAINER_NAME}' exists")
        
        # List blobs in container
        blob_list = list(container_client.list_blobs())
        print(f"   [OK] Found {len(blob_list)} blob(s) in container:")
        
        for blob in blob_list:
            blob_url = f"{AZURE_STORAGE_BLOB_ENDPOINT}/{BLOB_CONTAINER_NAME}/{blob.name}"
            print(f"        - {blob.name} ({blob.size} bytes)")
            print(f"          URL: {blob_url}")
        
        return len(blob_list) > 0
        
    except Exception as e:
        print(f"   [FAIL] Blob storage test failed: {e}")
        return False

def test_search_index():
    """Test search index includes blob URL fields."""
    print("\n2. Testing Search Index with Blob URLs...")
    
    try:
        credential = DefaultAzureCredential()
        search_client = SearchClient(AZURE_AI_SEARCH_ENDPOINT, INDEX_NAME, credential)
        
        # Search for documents and check blob URLs
        results = search_client.search("*", select="id,title,source,blob_url,page_url,page_number", top=5)
        
        doc_count = 0
        blob_url_count = 0
        
        print(f"   [OK] Sample documents in search index:")
        for result in results:
            doc_count += 1
            blob_url = result.get('blob_url', '')
            page_url = result.get('page_url', '')
            
            if blob_url:
                blob_url_count += 1
            
            print(f"        - ID: {result['id']}")
            print(f"          Title: {result.get('title', 'N/A')}")
            print(f"          Source: {result.get('source', 'N/A')}")
            print(f"          Page: {result.get('page_number', 'N/A')}")
            print(f"          Blob URL: {blob_url or 'Not set'}")
            print(f"          Page URL: {page_url or 'Not set'}")
            print()
        
        print(f"   [INFO] Documents with blob URLs: {blob_url_count}/{doc_count}")
        return blob_url_count > 0
        
    except Exception as e:
        print(f"   [FAIL] Search index test failed: {e}")
        return False

def test_knowledge_base_config():
    """Test knowledge base configuration."""
    print("\n3. Testing Knowledge Base Configuration...")
    
    try:
        # Load search configuration
        search_ids_path = config_dir / "search_ids.json"
        if not search_ids_path.exists():
            print(f"   [WARN] search_ids.json not found at {search_ids_path}")
            return False
        
        with open(search_ids_path) as f:
            search_info = json.load(f)
        
        kb_name = search_info.get("knowledge_base_name", "Not set")
        ks_name = search_info.get("knowledge_source_name", "Not set")
        blob_container = search_info.get("blob_container_name", "Not set")
        blob_urls = search_info.get("blob_urls", {})
        
        print(f"   [OK] Knowledge Base: {kb_name}")
        print(f"   [OK] Knowledge Source: {ks_name}")
        print(f"   [OK] Blob Container: {blob_container}")
        print(f"   [INFO] Tracked blob URLs: {len(blob_urls)}")
        
        for filename, url in blob_urls.items():
            print(f"        - {filename}: {url}")
        
        return True
        
    except Exception as e:
        print(f"   [FAIL] Knowledge base config test failed: {e}")
        return False

def run_citation_test():
    """Test a sample query to see if citations work."""
    print("\n4. Testing Citation Capabilities...")
    print("   [INFO] For full citation testing, use the Foundry agent portal")
    print("   [INFO] The agent should now be able to:")
    print("         - Provide source document names")
    print("         - Reference specific page numbers")
    print("         - Link to blob storage URLs for document access")
    print("         - Generate proper citations in responses")

# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    all_tests_passed = True
    
    # Run tests
    test_results = {
        "Blob Storage": test_blob_storage(),
        "Search Index": test_search_index(), 
        "Knowledge Base Config": test_knowledge_base_config()
    }
    
    # Run citation info
    run_citation_test()
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Results Summary")
    print(f"{'='*60}")
    
    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:.<25} {status}")
        if not passed:
            all_tests_passed = False
    
    if all_tests_passed:
        print(f"\n[SUCCESS] All tests passed! Citations should work in Foundry.")
        print(f"          Documents are stored in Azure Blob Storage.")
        print(f"          Search index includes blob URLs and metadata.")
        print(f"          Knowledge base is configured for citations.")
    else:
        print(f"\n[WARNING] Some tests failed. Check the configuration.")
        print(f"          Run 05_upload_to_search.py to fix any issues.")

if __name__ == "__main__":
    main()