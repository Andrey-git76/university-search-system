from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Проверяем подключение
print("Подключение к Elasticsearch...")
print(es.info()["version"]["number"])

# Удаляем старый индекс
if es.indices.exists(index="documents"):
    print("Удаляем старый индекс...")
    es.indices.delete(index="documents")

# Создаём индекс с русским анализатором
print("Создаём новый индекс...")
mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "russian",
                    "stopwords": "_russian_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "file_name": {"type": "text"},
            "page": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "russian_analyzer",
                "search_analyzer": "russian_analyzer"
            },
            "created_at": {"type": "date"}
        }
    }
}

es.indices.create(index="documents", body=mapping)
print("✅ Индекс создан с русским анализатором!")

# Проверяем
print(es.indices.get(index="documents"))