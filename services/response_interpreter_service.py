# services/response_interpreter_service.py (Nihai ve Doğru Hali)

import os
import pandas as pd
import requests
import json

def interpret_data_with_llm(df: pd.DataFrame, user_query: str, entities: dict) -> str:
    """
    Veri setini analiz eder ve lokal LLM (Ollama) kullanarak bir yorum üretir.
    Hangi sütunu analiz edeceğini 'entities' sözlüğünden öğrenir.
    """
    if df.empty:
        return "Yorumlanacak veri bulunamadı."

    # 1. Analiz edilecek sütun adını NLP'den gelen varlıklardan alalım.
    field_to_analyze = entities.get('field')

    # Eğer DataFrame'de bu isimde bir sütun yoksa veya field bulunamadıysa, hata ver.
    if not field_to_analyze or field_to_analyze not in df.columns:
        return f"Veri içinde beklenen '{field_to_analyze}' sütunu bulunamadı. Yorumlama yapılamıyor."

    # 2. Doğru sütun üzerinden istatistikleri çıkaralım.
    numeric_stats = df[field_to_analyze].describe().to_dict()
    
    start_time = pd.to_datetime(df['_time'].min()).isoformat()
    end_time = pd.to_datetime(df['_time'].max()).isoformat()
    trend_start_value = df[field_to_analyze].iloc[0]
    trend_end_value = df[field_to_analyze].iloc[-1]
    
    # 3. LLM için prompt'u hazırlayalım
    prompt = f"""
    Sen bir Kıdemli Veri Analistisin. Kullanıcı, "{user_query}" diye sordu.
    Aşağıda bu sorgunun sonuçlarının bir özeti bulunmaktadır:
    - Analiz Edilen Metrik: {field_to_analyze}
    - Ortalama Değer: {numeric_stats['mean']:.2f}
    - Maksimum Değer: {numeric_stats['max']:.2f}
    - Minimum Değer: {numeric_stats['min']:.2f}
    - Trend: Veri, {trend_start_value:.2f} değeriyle başlayıp {trend_end_value:.2f} değeriyle bitti.
    GÖREV: Bu özeti kullanarak, kullanıcıya bulguları özetleyen, 1-2 cümlelik kısa ve profesyonel bir metin yaz.
    """

    # 4. Ollama API'sine istek gönderelim
    ollama_api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434") + "/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(ollama_api_url, json=payload, timeout=300)
        response.raise_for_status()
        return json.loads(response.text).get("response", "LLM'den geçerli bir yanıt alınamadı.").strip()
    except requests.exceptions.RequestException as e:
        print(f"Ollama API'sine ulaşılamadı: {e}")
        return "Yapay zeka yorumlama servisine ulaşılamadı."