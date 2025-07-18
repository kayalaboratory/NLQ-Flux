# services/nlp_parser_service.py

import spacy
from spacy.matcher import Matcher

# SpaCy'nin küçük İngilizce modelini yüklüyoruz
# Komut satırından 'python -m spacy download en_core_web_sm' ile indirmiştik.
nlp = spacy.load("en_core_web_sm")

# Ölçüm isimlerini (cpu, memory vb.) bulmak için basit bir kural oluşturacağız.
# 'Matcher' belirli kalıpları bulmak için çok etkilidir.
matcher = Matcher(nlp.vocab)

# Kuralımızı tanımlayalım:
# Metin içinde küçük harfle "cpu" veya "memory" kelimelerini bul.
measurement_pattern = [
    {"LOWER": {"IN": ["cpu", "memory", "disk", "network", "boltdb_reads_total, "]}}
]
matcher.add("MEASUREMENT", [measurement_pattern])


field_pattern = [
    {"LOWER": {"IN": ["counter", "usage_idle", "value"]}}
]
matcher.add("FIELD", [field_pattern])

def parse_query_entities(text: str) -> dict:
    """
    Verilen metinden hem ölçüm hem de alan gibi varlıkları çıkarır
    ve bir sözlük olarak döndürür.
    """
    doc = nlp(text)
    matches = matcher(doc)
    
    entities = {}
    
    for match_id, start, end in matches:
        # Kuralın adını (MEASUREMENT, FIELD) alıyoruz
        rule_id = nlp.vocab.strings[match_id]
        # Eşleşen metni alıyoruz
        matched_text = doc[start:end].text.lower()
        
        # Kural adına göre sözlüğe ekliyoruz
        if rule_id == "MEASUREMENT":
            entities['measurement'] = matched_text
        elif rule_id == "FIELD":
            entities['field'] = matched_text
            
    return entities