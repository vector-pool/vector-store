# from transformers import LongformerTokenizer, LongformerModel
# import torch

# class TextToEmbedding:
#     def __init__(self):
#         self.max_token_size = 4098  # Maximum token size for the model
#         self.tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
#         self.model = LongformerModel.from_pretrained("allenai/longformer-base-4096")
#         print("Successfully initialized")

#     def embed(self, texts):
#         embedded_data = []
#         embeddings = []
#         original_data = []

#         for text in texts:
#             print("Processing text...")
#             inputs = self.tokenizer(text, return_tensors="pt", max_length=self.max_token_size, truncation=True)
#             print(text, "tokenized")
#             outputs = self.model(**inputs)
#             print("Model output received")
#             embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
#             pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
#             pooled_embedding_list = pooled_embedding.tolist()
#             print("Embedding done")
#             embedded_data.append(text)
#             embeddings.append(pooled_embedding_list)
#             original_data.append(text)

#         return embedded_data, embeddings, original_data

#     def mean_pooling(self, embedding, attention_mask):
#         token_embeddings = embedding  # (batch_size, sequence_length, hidden_size)
#         attention_mask = attention_mask.unsqueeze(-1)  # (batch_size, sequence_length, 1)

#         summed_embeddings = torch.sum(token_embeddings * attention_mask, 1)  # (batch_size, hidden_size)
#         summed_mask = torch.sum(attention_mask, 1)  # (batch_size, 1)

#         # Avoid division by zero
#         pooled_embedding = summed_embeddings / summed_mask.clamp(min=1e-9)
        
#         return pooled_embedding  # (batch_size, hidden_size)

#     def chunk_text(self, text):

#         words = text.split()
#         chunks = []
#         current_chunk = []

#         for word in words:
#             current_chunk.append(word)
#             if len(current_chunk) >= self.max_token_size:
#                 chunks.append(' '.join(current_chunk))
#                 current_chunk = []

#         if current_chunk:
#             chunks.append(' '.join(current_chunk))

#         return chunks

# if __name__ == "__main__":
#     embedder = TextToEmbedding()

#     content = ["hello, how are you?",]
#     embedding = embedder.embed(content)

#     print(embedding)

from transformers import LongformerTokenizer, LongformerModel
import torch

class TextToEmbedding:
    def __init__(self):
        self.max_token_size = 4098  # Maximum token size for the model
        self.tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
        self.model = LongformerModel.from_pretrained("allenai/longformer-base-4096").to('cuda')  # Move model to GPU
        print("Successfully initialized")

    # def embed(self, texts):
    #     embedded_data = []
    #     embeddings = []
    #     original_data = []

    #     # Tokenize all texts at once
    #     inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_token_size).to('cuda')
        
    #     print("All texts tokenized")
    #     outputs = self.model(**inputs)
    #     print("Model output received")
        
    #     embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
    #     pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
    #     pooled_embedding_list = pooled_embedding.tolist()
        
    #     print("Embedding done")
    #     embedded_data.extend(texts)  # Add all texts
    #     embeddings.extend(pooled_embedding_list)  # Add all embeddings
    #     original_data.extend(texts)  # Add all original texts

    #     return embedded_data, embeddings, original_data
    
    def embed(self, texts):
        embedded_data = []
        embeddings = []
        original_data = []

        # Tokenize all texts at once
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_token_size).to('cuda')
        
        print("All texts tokenized")
        outputs = self.model(**inputs)
        print("Model output received")
        
        embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
        pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
        pooled_embedding_list = pooled_embedding.tolist()
        
        print("Embedding done")
        embedded_data.extend(texts)  # Add all texts
        embeddings.extend(pooled_embedding_list)  # Add all embeddings
        original_data.extend(texts)  # Add all original texts

        return embedded_data, embeddings, original_data

    def mean_pooling(self, embedding, attention_mask):
        token_embeddings = embedding  # (batch_size, sequence_length, hidden_size)
        attention_mask = attention_mask.unsqueeze(-1)  # (batch_size, sequence_length, 1)

        summed_embeddings = torch.sum(token_embeddings * attention_mask, 1)  # (batch_size, hidden_size)
        summed_mask = torch.sum(attention_mask, 1)  # (batch_size, 1)

        # Avoid division by zero
        pooled_embedding = summed_embeddings / summed_mask.clamp(min=1e-9)
        
        return pooled_embedding  # (batch_size, hidden_size)

if __name__ == "__main__":
    embedder = TextToEmbedding()

    content = ["hello, how are you?", "This is another sentence for testing.", "Adding more text to see the performance."]
    embedding = embedder.embed(content)

    print(embedding)
