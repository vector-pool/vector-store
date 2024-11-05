from sentence_transformers import SentenceTransformer

embedding_model = 'all-MiniLM-L6-v2'

class TextToEmbedding:
    def __init__(self):
        self.model = SentenceTransformer(embedding_model)
        self.max_token_size = 768  # Maximum token size for the model

    def embed(self, original_texts):
        embeded_data = []
        embeddings = []
        original_data = []
        for text in original_texts:
            # Split the text into sentences or chunks based on the max token size
            chunks = self.chunk_text(text)

            for chunk in chunks:
                # Get the embedding for each chunk
                embedding = self.model.encode(chunk).tolist()  # Convert to list of floats
                
                # Create the result dictionary
                embeded_data.append(chunk)
                embeddings.append(embedding)
                original_data.append(text)

        return embeded_data, embeddings, original_data

    def chunk_text(self, text):
        # Simple chunking logic based on max token size
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.max_token_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []

        # Add any remaining words as a final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

# Example usage
text_to_embedding = TextToEmbedding()
texts = [
    "This is a long text that might exceed the maximum token size. " * 80,
    "This text is short."
]
embeddings = text_to_embedding.embed(texts)
for emb in embeddings:
    print(emb)

    
    