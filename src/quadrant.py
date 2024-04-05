ids = p.df_original.index.tolist()
vectors = p.embeddings.tolist()
texts = p.df_original['text'].tolist()
topics = p.df_original['topic'].tolist()
probs = p.df_original['topic_prob'].tolist()

points = [
    models.PointStruct(
        id = int(idx),
        vector = vector,
        payload = {"text": text, "topic": topic, "prob": prob}

    )
    for idx, vector, text, topic, prob in zip(ids, vectors, texts, topics, probs)
]

client.create_collection(
    collection_name='cop',
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)

client.upload_points(
    collection_name='cop',
    points = points,
)