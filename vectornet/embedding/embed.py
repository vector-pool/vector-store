from transformers import LongformerTokenizer, LongformerModel
import torch

class TextToEmbedding:
    def __init__(self):
        self.max_token_size = 8191  # Maximum token size for the model
        self.tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
        self.model = LongformerModel.from_pretrained("allenai/longformer-base-4096")

    def embed(self, text):
        embeded_data = []
        embeddings = []
        original_data = []

        inputs = self.tokenizer(text, return_tensors="pt", max_length=self.max_token_size, truncation=True)
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)

        pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])

        embeded_data.append(text)
        embeddings.append(pooled_embedding)
        original_data.append(text)

        return embeded_data, embeddings, original_data

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

if __name__ == '__main__':
    text = 'ladfajkslfal;dsfjal;sdfja;ldskfj'
    emb = TextToEmbedding()
    embedding = emb.embed(text)
    print(embedding)
