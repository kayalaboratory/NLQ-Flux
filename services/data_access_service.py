# services/data_access_service.py
import os
import pandas as pd
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

load_dotenv()

url = os.getenv("INFLUXDB_URL")
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")
print(f"URL ->: {url}")
print(f"Token ->: {token}")
print(f"Org Name: {org}")
def execute_flux_query(flux_query: str) -> pd.DataFrame:
    """Verilen Flux sorgusunu InfluxDB'de çalıştırır ve sonucu DataFrame olarak döndürür."""
    with InfluxDBClient(url=url, token=token, org=org) as client:
        try:
            query_api = client.query_api()
            df = query_api.query_data_frame(query=flux_query, org=org)
            return df
        except Exception as e:
            print(f"Sorgu hatası: {e}")
            return pd.DataFrame() # Hata durumunda boş DataFrame döndür