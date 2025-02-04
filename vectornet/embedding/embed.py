import os
from transformers import LongformerTokenizer, LongformerModel
import torch
import transformers
import bittensor as bt

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Initial CUDA memory allocated: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
    print(f"Initial CUDA memory cached: {torch.cuda.memory_reserved()/1024**2:.2f}MB")

transformers.logging.set_verbosity_error()

os.environ['TORCH_USE_CUDA_DSA'] = '1'  # Enable device-side assertions
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

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
            # Input validation data
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
