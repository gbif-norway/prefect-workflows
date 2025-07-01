"""
Example Prefect flow demonstrating secret usage.
"""

from prefect import flow, task
from prefect.blocks.system import Secret
import os


@task
def get_database_url():
    """Retrieve database URL from Prefect secrets."""
    try:
        secret = Secret.load("database-url")
        return secret.get()
    except Exception as e:
        print(f"Warning: Could not load database-url secret: {e}")
        return os.getenv("DATABASE_URL", "default-database-url")


@task
def get_api_keys():
    """Retrieve external API keys from Prefect secrets."""
    try:
        secret = Secret.load("external-api-keys")
        return secret.get().split(",")
    except Exception as e:
        print(f"Warning: Could not load external-api-keys secret: {e}")
        return []


@task
def connect_to_database(db_url: str):
    """Simulate database connection."""
    print(f"Connecting to database: {db_url}")
    # In a real flow, you would use the db_url to establish a connection
    return {"status": "connected", "url": db_url}


@task
def call_external_api(api_keys: list):
    """Simulate calling external APIs."""
    results = []
    for i, key in enumerate(api_keys):
        print(f"Calling API {i+1} with key: {key[:8]}...")
        results.append({"api": f"api-{i+1}", "status": "success"})
    return results


@flow(name="example-secret-flow")
def example_secret_flow():
    """Example flow that demonstrates using Prefect secrets."""
    print("Starting example flow with secret management...")
    
    # Get secrets
    db_url = get_database_url()
    api_keys = get_api_keys()
    
    # Use secrets in tasks
    db_result = connect_to_database(db_url)
    api_results = call_external_api(api_keys)
    
    print(f"Database connection: {db_result}")
    print(f"API calls completed: {len(api_results)}")
    
    return {
        "database": db_result,
        "apis": api_results,
        "secrets_used": {
            "database_url": bool(db_url),
            "api_keys": len(api_keys)
        }
    }


if __name__ == "__main__":
    example_secret_flow() 