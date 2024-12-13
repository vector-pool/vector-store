# from transformers import LongformerTokenizer, LongformerModel
# import torch
# import transformers
# import bittensor as bt

# transformers.logging.set_verbosity_error()

# tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
# model = LongformerModel.from_pretrained("allenai/longformer-base-4096").to('cuda')
# bt.logging.debug("Successfully initialized embeddig model")

# class TextToEmbedding:
#     def __init__(self):
#         self.max_token_size = 4098  # Maximum token size for the model
#         self.tokenizer = tokenizer
#         self.model = model
    
#     def embed(self, texts):
#         embedded_data = []
#         embeddings = []
#         original_data = []

#         # Tokenize all texts at once
#         inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=self.max_token_size).to('cuda')
        
#         bt.logging.debug("All texts tokenized")
#         outputs = self.model(**inputs)
#         bt.logging.debug("Model output received")
        
#         embedding = outputs.last_hidden_state  # Shape: (batch_size, sequence_length, hidden_size)
#         pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
#         pooled_embedding_list = pooled_embedding.tolist()
        
#         bt.logging.debug("Embedding done")
#         embedded_data.extend(texts)  # Add all texts
#         embeddings.extend(pooled_embedding_list)  # Add all embeddings
#         original_data.extend(texts)  # Add all original texts

#         return embedded_data, embeddings, original_data

#     def mean_pooling(self, embedding, attention_mask):
#         token_embeddings = embedding  # (batch_size, sequence_length, hidden_size)
#         attention_mask = attention_mask.unsqueeze(-1)  # (batch_size, sequence_length, 1)

#         summed_embeddings = torch.sum(token_embeddings * attention_mask, 1)  # (batch_size, hidden_size)
#         summed_mask = torch.sum(attention_mask, 1)  # (batch_size, 1)

#         # Avoid division by zero
#         pooled_embedding = summed_embeddings / summed_mask.clamp(min=1e-9)
        
#         return pooled_embedding  # (batch_size, hidden_size)

# if __name__ == "__main__":
#     embedder = TextToEmbedding()

#     content = ["hello, how are you?", "This is another sentence for testing.", "Adding more text to see the performance."]
#     embedding = embedder.embed(content)
#     print(embedding)












# from transformers import LongformerTokenizer, LongformerModel
# import torch
# import transformers
# import bittensor as bt
# import os

# # Set CUDA debugging environment variables
# os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# # Suppress transformer warnings
# transformers.logging.set_verbosity_error()

# # Check CUDA availability
# if not torch.cuda.is_available():
#     raise RuntimeError("CUDA is not available. Please check your GPU setup.")

# # Clear CUDA cache
# torch.cuda.empty_cache()

# try:
#     # Initialize model and tokenizer globally
#     tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
#     model = LongformerModel.from_pretrained("allenai/longformer-base-4096").to('cuda')
#     model.eval()  # Set model to evaluation mode
#     bt.logging.debug(f"Successfully initialized embedding model on {torch.cuda.get_device_name(0)}")
# except Exception as e:
#     bt.logging.error(f"Error initializing model: {str(e)}")
#     raise

# class TextToEmbedding:
#     def __init__(self):
#         self.max_token_size = 4098  # Maximum token size for the model
#         self.tokenizer = tokenizer
#         self.model = model
    
#     def embed(self, texts):
#         try:
#             # Clear CUDA cache before processing
#             torch.cuda.empty_cache()
            
#             # Input validation
#             if not texts:
#                 raise ValueError("Input texts cannot be empty")
#             if isinstance(texts, str):
#                 texts = [texts]
            
#             embedded_data = []
#             embeddings = []
#             original_data = []

#             # Tokenize all texts at once with error handling
#             try:
#                 inputs = self.tokenizer(
#                     texts,
#                     return_tensors="pt",
#                     padding=True,
#                     truncation=True,
#                     max_length=self.max_token_size,
#                     return_attention_mask=True
#                 ).to('cuda')
#                 bt.logging.debug("All texts tokenized")
#             except Exception as e:
#                 bt.logging.error(f"Tokenization error: {str(e)}")
#                 raise

#             # Model inference with error handling
#             try:
#                 with torch.no_grad():  # Disable gradient calculation for inference
#                     outputs = self.model(**inputs)
#                 bt.logging.debug("Model output received")
#             except RuntimeError as e:
#                 if "out of memory" in str(e):
#                     torch.cuda.empty_cache()
#                     bt.logging.error("GPU out of memory error. Cleared cache.")
#                 raise
#             except Exception as e:
#                 bt.logging.error(f"Model inference error: {str(e)}")
#                 raise

#             # Process embeddings
#             try:
#                 embedding = outputs.last_hidden_state
#                 pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
#                 # Move to CPU before converting to list to prevent CUDA errors
#                 pooled_embedding = pooled_embedding.cpu()
#                 pooled_embedding_list = pooled_embedding.tolist()
#                 bt.logging.debug("Embedding done")
#             except Exception as e:
#                 bt.logging.error(f"Embedding processing error: {str(e)}")
#                 raise

#             embedded_data.extend(texts)
#             embeddings.extend(pooled_embedding_list)
#             original_data.extend(texts)

#             return embedded_data, embeddings, original_data
        
#         except Exception as e:
#             bt.logging.error(f"Error in embed method: {str(e)}")
#             raise

#     def mean_pooling(self, embedding, attention_mask):
#         try:
#             token_embeddings = embedding
#             attention_mask = attention_mask.unsqueeze(-1)

#             summed_embeddings = torch.sum(token_embeddings * attention_mask, 1)
#             summed_mask = torch.sum(attention_mask, 1)

#             # Avoid division by zero with more explicit error handling
#             if torch.any(summed_mask == 0):
#                 bt.logging.warning("Zero mask values detected in mean pooling")
            
#             pooled_embedding = summed_embeddings / summed_mask.clamp(min=1e-9)
            
#             return pooled_embedding

#         except Exception as e:
#             bt.logging.error(f"Error in mean_pooling: {str(e)}")
#             raise

# if __name__ == "__main__":
#     try:
#         embedder = TextToEmbedding()

#         # Test with a single short text first
#         bt.logging.debug("Testing with single text...")
#         single_test = embedder.embed(["hello, testing."])
#         bt.logging.debug("Single text test successful")

#         # Test with multiple texts
#         content = [
#             "hello, how are you?",
#             "This is another sentence for testing.",
#             "Adding more text to see the performance."
#         ]
#         bt.logging.debug("Processing multiple texts...")
#         embedding = embedder.embed(content)
#         bt.logging.debug("Multiple texts processing successful")
#         print(embedding)

#     except Exception as e:
#         bt.logging.error(f"Main execution error: {str(e)}")
#         raise





import os
# Set these environment variables before importing torch
os.environ['TORCH_USE_CUDA_DSA'] = '1'  # Enable device-side assertions
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

from transformers import LongformerTokenizer, LongformerModel
import torch
import transformers
import bittensor as bt

# Print debug information
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Initial CUDA memory allocated: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
    print(f"Initial CUDA memory cached: {torch.cuda.memory_reserved()/1024**2:.2f}MB")

# Suppress transformer warnings
transformers.logging.set_verbosity_error()

def initialize_model():
    try:
        # Initialize tokenizer and model
        tokenizer = LongformerTokenizer.from_pretrained("allenai/longformer-base-4096")
        model = LongformerModel.from_pretrained("allenai/longformer-base-4096")
        
        # Ensure model is in eval mode and properly moved to CUDA
        model.eval()
        if torch.cuda.is_available():
            model = model.cuda()
            torch.cuda.synchronize()  # Ensure CUDA operations are synchronized
        
        bt.logging.debug("Successfully initialized embedding model")
        return tokenizer, model
    except Exception as e:
        bt.logging.error(f"Model initialization error: {str(e)}")
        raise

# Initialize model and tokenizer globally
tokenizer, model = initialize_model()

class TextToEmbedding:
    def __init__(self):
        self.max_token_size = 4096  # Longformer's maximum token size
        self.tokenizer = tokenizer
        self.model = model
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        bt.logging.debug(f"TextToEmbedding initialized on device: {self.device}")
    
    def print_debug_info(self, inputs, global_attention_mask):
        """Print debug information about tensors and devices"""
        print("\n=== Debug Information ===")
        print(f"Input IDs shape: {inputs['input_ids'].shape}")
        print(f"Attention mask shape: {inputs['attention_mask'].shape}")
        print(f"Global attention mask shape: {global_attention_mask.shape}")
        print(f"Input IDs device: {inputs['input_ids'].device}")
        print(f"Model device: {next(self.model.parameters()).device}")
        print(f"CUDA memory allocated: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
        print("========================\n")

    def embed(self, texts):
        try:
            # Input validation
            if not texts:
                raise ValueError("Input texts cannot be empty")
            if isinstance(texts, str):
                texts = [texts]
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()

            bt.logging.debug(f"Processing {len(texts)} texts")
            
            # Tokenize with explicit settings
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_token_size
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Create global attention mask
            global_attention_mask = torch.zeros_like(inputs['input_ids'])
            global_attention_mask[:, 0] = 1  # Set global attention on [CLS] token
            
            # Print debug information
            # self.print_debug_info(inputs, global_attention_mask)
            
            with torch.no_grad():
                try:
                    outputs = self.model(
                        input_ids=inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        global_attention_mask=global_attention_mask
                    )
                except RuntimeError as e:
                    if "out of memory" in str(e):
                        torch.cuda.empty_cache()
                        bt.logging.error("GPU out of memory error")
                    raise

            # Process embeddings
            embedding = outputs.last_hidden_state
            pooled_embedding = self.mean_pooling(embedding, inputs['attention_mask'])
            
            # Move to CPU and convert to list
            pooled_embedding = pooled_embedding.cpu()
            pooled_embedding_list = pooled_embedding.tolist()
            
            return texts, pooled_embedding_list, texts

        except Exception as e:
            bt.logging.error(f"Error in embed method: {str(e)}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            raise

    def mean_pooling(self, embedding, attention_mask):
        try:
            attention_mask = attention_mask.unsqueeze(-1)
            summed_embeddings = torch.sum(embedding * attention_mask, 1)
            summed_mask = torch.sum(attention_mask, 1)
            
            # Add small epsilon to avoid division by zero
            epsilon = 1e-9
            summed_mask = summed_mask.clamp(min=epsilon)
            
            return summed_embeddings / summed_mask
            
        except Exception as e:
            bt.logging.error(f"Error in mean_pooling: {str(e)}")
            raise

def test_embedder():
    try:
        embedder = TextToEmbedding()
        
        # Test 1: Single short text
        bt.logging.debug("Test 1: Single short text")
        test_text = ["Hello world"]
        result = embedder.embed(test_text)
        print("Test 1 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        # Test 2: Multiple short texts
        bt.logging.debug("Test 2: Multiple short texts")
        test_texts = [
            "Hello world",
            "This is a test",
            "Multiple sentences"
        ]
        result = embedder.embed(test_texts)
        print("Test 2 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        # Test 3: Longer text
        bt.logging.debug("Test 3: Longer text")
        long_text = ["This is a longer text that contains multiple sentences. " * 10]
        result = embedder.embed(long_text)
        print("Test 3 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        return "All tests completed successfully!"
        
    except Exception as e:
        bt.logging.error(f"Test execution error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("\n=== Starting Tests ===")
        result = test_embedder()
        print(result)
        print("=== Tests Complete ===\n")
        
    except Exception as e:
        bt.logging.error(f"Main execution error: {str(e)}")
        raise
