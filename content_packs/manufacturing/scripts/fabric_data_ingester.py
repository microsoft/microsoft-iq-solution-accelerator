from datetime import datetime, timezone
import os
import sys
from azure.identity import AzureCliCredential
from azure.kusto.data import KustoConnectionStringBuilder, KustoClient
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties
from azure.kusto.data.data_format import DataFormat
import shutil
import pandas as pd

def create_kusto_client(cluster_uri: str):
    try:
        credential = AzureCliCredential()
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster_uri, credential)
        client = KustoClient(kcsb)
        return client
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def create_ingestion_client(cluster_uri: str):
    try:
        print(f"Connecting to Fabric cluster: {cluster_uri}")
        credential = AzureCliCredential()
        
        # Create ingestion client using the ingestion endpoint
        # The ingestion URI is typically the cluster URI with 'ingest-' prefix
        ingest_uri = cluster_uri if "ingest-" in cluster_uri else cluster_uri.replace("https://", "https://ingest-")
        kcsb = KustoConnectionStringBuilder.with_azure_token_credential(ingest_uri, credential)
        ingest_client = QueuedIngestClient(kcsb)
        
        print(f"✅ Connected to ingestion endpoint")
        return ingest_client
    
    except Exception as e:
        print(f"Error creating ingestion client: {e}")
        raise


def check_table_empty(kusto_client: KustoClient, database_name: str, table_name: str):
    try:
        query = f"['{table_name}'] | count"
        response = kusto_client.execute(database_name, query)
        
        # Get the count from the response
        count = response.primary_results[0][0]["Count"]
        return count == 0
    
    except Exception as e:
        print(f"Warning: Could not check if table {table_name} is empty: {e}")
        # assume it's empty to allow ingestion
        return True
    
def clear_table_data(kusto_client: KustoClient, database_name: str, table_name: str):
    try:
        command = f".clear table ['{table_name}'] data"
        kusto_client.execute_mgmt(database_name, command)
        
        print(f"✓ Cleared all data from table {table_name}")
        return True
    
    except Exception as e:
        print(f"Error clearing data from table {table_name}: {e}")
        raise


def ingest_data_to_fabric(ingest_client: QueuedIngestClient, database_name: str, table_name: str, csv_file_path: str):
    try:
        print(f"Ingesting {csv_file_path} into {database_name}.{table_name}...")
        
        # Set up ingestion properties for CSV format
        ingestion_props = IngestionProperties(
            database=database_name,
            table=table_name,
            data_format=DataFormat.CSV,
            ingestion_mapping_reference=None,  # Use table's default mapping or none
            additional_properties={
                'ignoreFirstRecord': 'true'  # Skip CSV header row
            }
        )
        
        # Ingest from file
        ingest_client.ingest_from_file(csv_file_path, ingestion_properties=ingestion_props)
        
        print(f"  ✓ Ingestion queued for {table_name}")
        return True
    
    except KustoServiceError as e:
        print(f"Kusto service error: {e}")
        raise
    except Exception as e:
        print(f"Error ingesting data to {table_name}: {e}")
        raise


def refresh_event_csv_timestamps(data_path: str, start_date: datetime) -> str:
    original_events_file = os.path.join(data_path, "events.csv")
    if not os.path.exists(original_events_file):
        raise FileNotFoundError(f"CSV not found at path: {original_events_file}")

    temp_dir = os.path.join(data_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_events_file = os.path.join(temp_dir, "events.csv")
    if os.path.exists(temp_events_file):
        os.remove(temp_events_file)
        print(f"  ✓ Removed existing temp events.csv")

    shutil.copy2(original_events_file, temp_events_file)
    print(f"  ✓ Copied events.csv to temp folder")

    print(f'Updating event timestamps in events.csv to be relative to {start_date.strftime("%Y-%m-%d")}...')

    df = pd.read_csv(temp_events_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Find the most recent timestamp in the data and get the time difference to start_date
    most_recent_timestamp = df['Timestamp'].max()
    time_diff = start_date - most_recent_timestamp

    # Adjust all timestamps by adding the time difference
    df['Timestamp'] = df['Timestamp'] + time_diff

    df.to_csv(temp_events_file, index=False)

    print(f"  ✓ Updated event timestamps - most recent is now: {df['Timestamp'].max()}")

    return temp_events_file


def load_data_to_fabric(
    cluster_uri: str,
    database_name: str,
    data_path: str,
    refresh_event_dates: bool,
    overwrite_existing: bool
):
    """
    Load CSV data into Microsoft Fabric database.
    
    Parameters:
    -----------
    cluster_uri : str
        The URI of the Fabric cluster
    database_name : str
        The name of the target database
    data_path : str
        Path to directory containing CSV files (relative to script location)
    refresh_event_dates : bool
        Whether to refresh event timestamps to be recent
    overwrite_existing : bool
        Whether to overwrite existing data in tables
    
    Returns:
    --------
    dict
        Summary of ingestion results
    """
    try:
        # Convert relative path to absolute
        if not os.path.isabs(data_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(script_dir, data_path)
        
        print(f"Data path: {os.path.abspath(data_path)}")

        if refresh_event_dates:
            event_file_path = refresh_event_csv_timestamps(data_path, datetime.now(timezone.utc))
        else:
            event_file_path = os.path.join(data_path, "events.csv")

        # Define CSV files to ingest
        csv_files = {
            "locations": os.path.join(data_path, "locations.csv"),
            "sites": os.path.join(data_path, "sites.csv"),
            "assets": os.path.join(data_path, "assets.csv"),
            "products": os.path.join(data_path, "products.csv"),
            "events": event_file_path,
        }
        
        # Verify files exist
        existing_files = {}
        for table_name, file_path in csv_files.items():
            if os.path.exists(file_path):
                existing_files[table_name] = file_path
                print(f"  ✓ Found {table_name}.csv")
            else:
                print(f"  Warning: {table_name}.csv not found, skipping...")
        
        if not existing_files:
            raise FileNotFoundError(f"No CSV files found in {data_path}")

        # Connect to Fabric and create clients
        kusto_client = create_kusto_client(cluster_uri)
        ingest_client = create_ingestion_client(cluster_uri)
        
        # Check table status and ingest data
        print(f"\nChecking tables and ingesting data...")
        results = {}
        for table_name, file_path in existing_files.items():
            try:
                if table_name == "events" and (refresh_event_dates or overwrite_existing):
                    print('Clearing data from "events" table...')
                    clear_table_data(kusto_client, database_name, table_name)

                # Check if table is empty
                is_empty = check_table_empty(kusto_client, database_name, table_name)

                if not is_empty and overwrite_existing:
                    print(f"Table {table_name} already has data, clearing before ingestion...")
                    clear_table_data(kusto_client, database_name, table_name)
                    is_empty = True  # now it's empty after clearing
                
                if is_empty:
                    print(f"Table {table_name} is empty, proceeding with ingestion...")
                    success = ingest_data_to_fabric(ingest_client, database_name, table_name, file_path)
                    results[table_name] = {
                        "success": success,
                        "file": file_path,
                        "action": "ingested"
                    }
                else:
                    print(f"Table {table_name} already has data, skipping ingestion...")
                    results[table_name] = {
                        "success": True,
                        "file": file_path,
                        "action": "skipped"
                    }
                    
            except Exception as e:
                results[table_name] = {
                    "success": False,
                    "error": str(e),
                    "action": "failed"
                }
                print(f"Failed to process {table_name}: {e}")
        
        # Clean up temporary files if they were created
        if refresh_event_dates:
            if os.path.exists(event_file_path):
                os.remove(event_file_path)
                print(f"  ✓ Cleaned up temporary event.csv")

        # Summary
        successful = sum(1 for r in results.values() if r.get("success", False))
        ingested = sum(1 for r in results.values() if r.get("action") == "ingested")
        skipped = sum(1 for r in results.values() if r.get("action") == "skipped")
        
        print(f"\n✅ Data processing complete!")
        print(f"   Successfully processed {successful}/{len(results)} tables")
        print(f"   Ingested: {ingested} tables")
        print(f"   Skipped (already has data): {skipped} tables")
        if ingested > 0:
            print(f"   Note: Ingestion is asynchronous. Check Fabric for ingestion status.")
        
        return results
    
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__": 
    import argparse
    
    parser = argparse.ArgumentParser(description='Load CSV data into Microsoft Fabric database')
    parser.add_argument('--cluster-uri', required=True, help='Fabric cluster URI')
    parser.add_argument('--database', required=True, help='Target database name')
    parser.add_argument('--data-path', default='../../data', help='Path to CSV files directory (default: ../../data)')
    parser.add_argument('--refresh-dates', action='store_true', help='Refresh event timestamps to current date')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing data in tables')
    
    args = parser.parse_args()

    try:
        load_data_to_fabric(
            cluster_uri=args.cluster_uri,
            database_name=args.database,
            data_path=args.data_path,
            refresh_event_dates=args.refresh_dates,
            overwrite_existing=args.overwrite
        )
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
