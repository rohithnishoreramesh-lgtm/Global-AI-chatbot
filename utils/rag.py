class SimpleRAG:
    def __init__(self):
        self.chunks = []

    def add_text(self, text, chunk_size=1000):
        if not text:
            return
        self.chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

    def retrieve(self, query, top_k=4):
        if not self.chunks:
            return []

        query_words = set(query.lower().split())
        scored = []

        for chunk in self.chunks:
            chunk_words = set(chunk.lower().split())
            score = len(query_words & chunk_words)
            scored.append((score, chunk))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored[:top_k] if score > 0]