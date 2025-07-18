# services/query_generator_service.py
import os

def generate_aggregated_query(entities: dict) -> str | None:
    """
    Verilen varlıklara göre aggregateWindow ve pivot içeren bir Flux sorgusu oluşturur.
    """
    if 'measurement' not in entities or 'field' not in entities:
        return None

    bucket = os.getenv("INFLUXDB_BUCKET", "host1")
    measurement = entities['measurement']
    field = entities['field']
    window_period = "1m" 

    flux_query = f'''
from(bucket: "{bucket}")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
  |> filter(fn: (r) => r["_field"] == "{field}")
  |> aggregateWindow(every: {window_period}, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    # UYARIYI GİDERMEK İÇİN YUKARIDAKİ |> PIVOT(...) SATIRINI EKLEDİK.
    
    return flux_query