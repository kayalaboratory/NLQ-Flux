# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.nlp_parser_service import parse_query_entities
from services.query_generator_service import generate_aggregated_query
from services.data_access_service import execute_flux_query
from services.response_interpreter_service import interpret_data_with_llm

class UserQuery(BaseModel):
    query: str

app = FastAPI(title="Akıllı InfluxDB Sorgulama Servisi", version="1.3.1 (Robust)")

@app.post("/query", tags=["Core"])
def process_natural_language_query(user_query: UserQuery):
    entities = parse_query_entities(user_query.query)
    if not entities or 'measurement' not in entities or 'field' not in entities:
        raise HTTPException(status_code=400, detail="Sorgunuzdan hem ölçüm hem de alan adı çıkarılamadı.")
    
    flux_query = generate_aggregated_query(entities)
    data_frame = execute_flux_query(flux_query)
    
    if data_frame is None or data_frame.empty:
        return {"response": "Belirtilen kriterlerde veri bulunamadı."}

    # YORUMLAMA FONKSİYONUNA 'ENTITIES' SÖZLÜĞÜNÜ DE GÖNDERİYORUZ
    interpreted_text = interpret_data_with_llm(data_frame, user_query.query, entities)

    influxdb_raw_data = data_frame.to_dict(orient='records')

    return {
        "user_query": user_query.query,
        "recognized_entities": entities,
        "generated_flux_query": flux_query,
        "influxdb_data": influxdb_raw_data,
        "interpreted_response": interpreted_text
    }
# main.py içindeki @app.post("/query") fonksiyonunun sonu

    # ... (diğer kodlar aynı kalıyor) ...

    # --- Katman 4: Yanıt Yorumlama (LLM ile) ---
    interpreted_text = interpret_data_with_llm(data_frame, user_query.query, entities)

    # DataFrame'i yanıt için JSON formatına çevirelim
    influxdb_raw_data = data_frame.to_dict(orient='records')

    return {
        "user_query": user_query.query,
        "recognized_entities": entities,
        "generated_flux_query": flux_query,
        "influxdb_data": influxdb_raw_data,  # <-- BU SATIRI GERİ EKLEDİK
        "interpreted_response": interpreted_text
    }