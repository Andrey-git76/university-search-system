from elasticsearch import Elasticsearch

# Подключаемся к Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Проверяем подключение
print("Проверка подключения...")
info = es.info()
print(f"Версия Elasticsearch: {info['version']['number']}")

# Проверяем, существует ли индекс
if es.indices.exists(index="documents"):
    print("Удаляем существующий индекс...")
    es.indices.delete(index="documents")

# Создаём индекс
print("Создаём индекс 'documents'...")
mapping = {
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "chunk_id": {"type": "keyword"},
            "file_name": {"type": "text"},
            "page": {"type": "integer"},
            "text": {"type": "text"},
            "created_at": {"type": "date"}
        }
    }
}

es.indices.create(index="documents", body=mapping)
print("✅ Индекс 'documents' создан успешно!")

# Проверяем
print("Проверка индекса...")
print(es.indices.get(index="documents"))