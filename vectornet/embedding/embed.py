from transformers import LongformerTokenizer, LongformerModel
import torch
import transformers
import bittensor as bt

transformers.logging.set_verbosity_error()

tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
model = LongformerModel.from_pretrained("allenai/longformer-base-4096").to('cuda')

class TextToEmbedding:
    def __init__(self):
        self.max_token_size = 4098  # Maximum token size for the model
        self.tokenizer = tokenizer
        self.model = model
        bt.logging.debug("Successfully initialized embeddig model")
    
    def embed(self, texts):
        embedded_data = []
        embeddings = []
        original_data = []

        # Tokenize all texts at once
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_token_size).to('cuda')
        
        bt.logging.debug("All texts tokenized")
        outputs = self.model(**inputs)
        bt.logging.debug("Model output received")
        
        embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
        pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
        pooled_embedding_list = pooled_embedding.tolist()
        
        bt.logging.debug("Embedding done")
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
