import chromadb

chroma_client = chromadb.PersistentClient(path="../db/chroma")

collection = chroma_client.create_collection(name="car_collection")

collection.add(documents=["Ford", "Honda"], ids=["id1", "id2"])

results = collection.query(
    query_texts=["Give me a car made in America"],  # Chroma embeds this automatically
    n_results=1,
)

print(results)
