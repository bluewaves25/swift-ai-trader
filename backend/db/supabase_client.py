from supabase import create_client, Client
from python_dotenv import load_dotenv
import os

load_dotenv()

def get_supabase_client() -> Client:
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))