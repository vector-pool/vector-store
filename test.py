import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def evaluate_similarity(original_content_embedding, content_embedding):
    # Calculate cosine similarity
    similarity_score = cosine_similarity(original_content_embedding, content_embedding)[0][0]
    return similarity_score

if __name__ == '__main__':
    # Example embeddings (2D arrays)
    original_content_embedding = np.array([[1, 2, 3]])  # shape (1, 3)
    content_embedding = np.array([[4, 5, 6]])           # shape (1, 3)
    print(original_content_embedding, content_embedding)
    # Compute similarity
    similarity = evaluate_similarity(original_content_embedding, content_embedding)
    print(f"Similarity Score: {similarity}")
