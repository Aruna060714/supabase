from supabase import create_client, Client
from fastmcp import FastMCP
from opensearchpy import OpenSearch
from datetime import datetime
SUPABASE_URL = "https://uylzwlzgnkxcwcafahmn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5bHp3bHpnbmt4Y3djYWZhaG1uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwMzMwMTYsImV4cCI6MjA2OTYwOTAxNn0.X9oJIxvc6Q-QgiUc2BPkrlDsL_3ZJyfcu0I0dI8KNfE" 
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing.")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
opensearch = OpenSearch(
    hosts=[{"host": "superbotics-search-8731633774.eu-central-1.bonsaisearch.net", "port": 443}],
    http_auth=("JC8YvqRN74", "T8JEbusxGFN5VXZ"),
    use_ssl=True,
    verify_certs=True
)
mcp = FastMCP("product-search")
def log_to_opensearch(code: str, status: str, result: dict):
    log_doc = {
            "date": datetime.now().isoformat(),
            "query": code,
            "service": "fetch_product_by_code"
        }
    opensearch.index(index="logs_mcp", body=log_doc)
@mcp.tool()
async def fetch_product_by_code(code: str) -> str:
    """
    Fetch a product from the Supabase 'products_new2' table using its barcode or ref.
    Log the request to OpenSearch.
    """
    response = supabase.table("products_new2").select("*").eq("barcode", code).execute()
    if not response.data:
        response = supabase.table("products_new2").select("*").eq("ref", code).execute()
    if not response.data:
        log_to_opensearch(code, "not_found", {})
        return f"No product found for code: {code}"
    product = response.data[0]
    log_to_opensearch(code, "found", product)
    result = f"""
    **Product Found:**
    - **Title:** {product.get('title')}
    - **Ref:** {product.get('ref')}
    - **Barcode:** {product.get('barcode')}
    - **Type:** {product.get('type')}
    - **Brand:** {product.get('brand')}
    - **Price:** {product.get('price') or "N/A"}
    - **Image URL:** {product.get('image')}
    """
    return result
if __name__ == "__main__":
    mcp.run()