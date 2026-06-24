#!/usr/bin/env python3
"""
Fabric Database Setup Module

This module provides database setup functionality for Microsoft Fabric operations.
It creates and manages database tables and schemas for manufacturing data.

Usage:
    python fabric_database.py --cluster-uri "https://cluster.kusto.windows.net" --database "database_name"

Requirements:
    - Azure CLI authentication or other Azure credentials configured
    - Kusto client libraries installed
    - Access to the specified Fabric cluster and database
"""

import sys
from pathlib import Path

# Add the parent scripts directory to Python path for imports
script_dir = Path(__file__).parent
scripts_dir = script_dir.parent
sys.path.insert(0, str(scripts_dir))

from azure.identity import AzureCliCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError

def create_kusto_client(cluster_uri) -> KustoClient:
    """
    Create a Kusto client for Microsoft Fabric.
    
    Parameters:
    -----------
    cluster_uri : str
        The URI of the Fabric cluster (e.g., "https://<cluster>.kusto.windows.net")
    
    Returns:
    --------
    KustoClient
        Connected Kusto client instance
    """
    try:
        
        print(f"Connecting to Fabric cluster: {cluster_uri}")
        credential = AzureCliCredential()
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster_uri, credential)
        client = KustoClient(kcsb)
        print(f"✅ Connected to Fabric cluster")
        return client
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def check_database_exists(client: KustoClient, database_name: str):
    """
    Check if a database exists in the Fabric cluster.
    
    Parameters:
    -----------
    client : KustoClient
        Connected Kusto client
    database_name : str
        Name of the database to check
    
    Returns:
    --------
    bool
        True if database exists
        
    Raises:
    -------
    Exception
        If database does not exist or error checking database existence
    """
    try:
        query = ".show databases"
        response = client.execute("NetDefaultDB", query)
        
        databases = [row.to_dict()["PrettyName"] for row in response.primary_results[0]]
        database_exists = database_name in databases
        
        if not database_exists:
            raise Exception(f"Database '{database_name}' does not exist in the Fabric cluster. Please ensure the database exists before running this script.")
        
        return True
    
    except Exception as e:
        if "does not exist" in str(e):
            raise  # Re-raise our custom error message
        print(f"Error checking database existence: {e}")
        raise

def check_table_exists(client: KustoClient, database_name: str, table_name: str):
    """
    Check if a table exists in the database.
    
    Parameters:
    -----------
    client : KustoClient
        Connected Kusto client
    database_name : str
        Name of the database
    table_name : str
        Name of the table to check
    
    Returns:
    --------
    bool
        True if table exists
    """
    try:
        query = ".show tables"
        response = client.execute(database_name, query)
        
        tables = [row["TableName"] for row in response.primary_results[0]]
        return table_name in tables
    
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return False


def create_table(client: KustoClient, database_name: str, table_name: str, schema: str):
    """
    Create a table in the database with the specified schema.
    
    Parameters:
    -----------
    client : KustoClient
        Connected Kusto client
    database_name : str
        Name of the database
    table_name : str
        Name of the table to create
    schema : str
        KQL schema definition for the table
    
    Returns:
    --------
    bool
        True if successful
    """
    try:
        print(f"Creating table: {database_name}.{table_name}")
        query = f".create table ['{table_name}'] {schema}"
        client.execute(database_name, query)
        print(f"✅ Table '{table_name}' created successfully")
        return True
    
    except KustoServiceError as e:
        if "already exists" in str(e).lower():
            print(f"✅ Table '{table_name}' already exists")
            return True
        else:
            print(f"Error creating table: {e}")
            raise
    except Exception as e:
        print(f"Error creating table: {e}")
        raise


def get_table_schemas():
    """
    Define the schemas for the manufacturing data tables.
    
    Returns:
    --------
    dict
        Dictionary containing table schemas
    """
    return {
        "locations": """(
            Id: int,
            City: string,
            Country: string
        )""",

        "sites": """(
            Id: int,
            Name: string,
            LocationId: int,
            PlantType: string
        )""",

        # NOTE: schema here matches against entity Asset class in src/entities/asset.py
        "assets": """(
            Id: string,
            Name: string,
            SiteId: int,
            Type: string,
            SerialNumber: string,
            MaintenanceStatus: string
        )""",
        
        "products": """(
            Id: string,
            CategoryId: int,
            CategoryName: string,
            Name: string,
            Description: string,
            BrandName: string,
            Number: string,
            Status: string,
            Color: string,
            ListPrice: real,
            UnitCost: real,
            IsoCurrencyCode: string
        )""",

        # NOTE: schema here matches against entity Event class in src/entities/event.py
        "events": """(
            Id: string,
            AssetId: string,
            ProductId: string,
            Timestamp: datetime,
            BatchId: string,
            Vibration: real,
            Temperature: real,
            Humidity: real,
            Speed: real,
            DefectProbability: real
        )"""
    }


def setup_fabric_database(
    cluster_uri,
    database_name
):
    """
    Set up the Microsoft Fabric database tables for manufacturing data.
    Assumes the database already exists and will raise an error if not found.
    
    Parameters:
    -----------
    cluster_uri : str
        The URI of the Fabric cluster
    database_name : str
        Name of the existing database
    
    Returns:
    --------
    dict
        Summary of setup results
        
    Raises:
    -------
    Exception
        If database does not exist
    """
    try:
        print(f"Setting up Fabric database tables in: {database_name}")
        
        # Create Kusto client
        client = create_kusto_client(cluster_uri)
        
        # Check database exists (will raise error if not found)
        print(f"\nVerifying database: {database_name}")
        check_database_exists(client, database_name)
        print(f"✅ Database '{database_name}' verified and exists")
        
        # Get table schemas
        schemas = get_table_schemas()
        
        # Check and create tables
        print(f"\nChecking tables...")
        table_results = {}
        for table_name, schema in schemas.items():
            try:
                if not check_table_exists(client, database_name, table_name):
                    success = create_table(client, database_name, table_name, schema)
                    table_results[table_name] = {"created": True, "success": success}
                else:
                    print(f"✅ Table '{table_name}' already exists")
                    table_results[table_name] = {"created": False, "success": True}
            except Exception as e:
                table_results[table_name] = {"created": False, "success": False, "error": str(e)}
                print(f"Failed to create table {table_name}: {e}")
        
        # Summary
        successful_tables = sum(1 for r in table_results.values() if r.get("success", False))
        created_tables = sum(1 for r in table_results.values() if r.get("created", False))
        
        print(f"\n✅ Database table setup complete!")
        print(f"   Database: {database_name}")
        print(f"   Tables: {successful_tables}/{len(schemas)} ready")
        print(f"   Created: {created_tables} new tables")
        
        return {
            "database": database_name,
            "database_verified": True,
            "tables": table_results,
            "summary": {
                "total_tables": len(schemas),
                "successful_tables": successful_tables,
                "created_tables": created_tables
            }
        }
    
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":    
    try:
        results = setup_fabric_database(
            cluster_uri="https://<your-cluster-uri>",
            database_name="<your-database-name>"
        )
        print(f"\nSetup results: {results['summary']}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
