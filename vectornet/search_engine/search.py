import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self):
        pass
    
    def cosine_similarity_search(self, query_embedding, vectors, size):
        """
        Finds the most similar embeddings in the vectors based on the query_embedding.
        
        Args:
            query_embedding (list): The embedding list representing the query text.
            vectors (list): A list of dictionaries, each containing 'original_text', 'text', and 'embedding'.
            size(int): A number of return values
            
        Returns:
            list: A number of top vectors in sorted list of dictionaries with the most similar texts and their similarity scores.
        """
        similarities = []

        # Convert query_embedding to a numpy array
        query_embedding_array = np.array(query_embedding).reshape(1, -1)

        for vector in vectors:
            # Extract the embedding from the vector
            vector_embedding = np.array(vector['embedding']).reshape(1, -1)  # Convert to numpy array

            # Calculate cosine similarity
            similarity_score = cosine_similarity(query_embedding_array, vector_embedding)[0][0]

            # Store the similarity score along with the associated text
            similarities.append({
                'original_text': vector['original_text'],
                'text': vector['text'],
                'embedding': vector['embedding'],
                'vector_id': vector['vector_id'],
                'similarity': similarity_score,
            })

        # Sort by similarity score in descending order and return the results
        results = sorted(similarities, key=lambda x: x['similarity'], reverse=True)

        return results[:size]
