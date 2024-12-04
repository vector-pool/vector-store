from transformers import LongformerTokenizer, LongformerModel
import torch

class TextToEmbedding:
    def __init__(self):
        self.max_token_size = 4098  # Maximum token size for the model
        self.tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
        self.model = LongformerModel.from_pretrained("allenai/longformer-base-4096")

    def embed(self, texts):
        embeded_datas = []
        embeddings = []
        original_datas = []

        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", max_length=self.max_token_size, truncation=True)
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)

            pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
            pooled_embedding_list = pooled_embedding.tolist()
            embeded_datas.append(text)
            embeddings.append(pooled_embedding_list)
            original_datas.append(text)

        return embeded_datas, embeddings, original_datas

    def mean_pooling(self, embedding, attention_mask):
        token_embeddings = embedding  # (batch_size, sequence_length, hidden_size)
        attention_mask = attention_mask.unsqueeze(-1)  # (batch_size, sequence_length, 1)

        summed_embeddings = torch.sum(token_embeddings * attention_mask, 1)  # (batch_size, hidden_size)
        summed_mask = torch.sum(attention_mask, 1)  # (batch_size, 1)

        pooled_embedding = summed_embeddings / summed_mask
        
        return pooled_embedding  # (batch_size, hidden_size)

    def chunk_text(self, text):

        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= self.max_token_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
