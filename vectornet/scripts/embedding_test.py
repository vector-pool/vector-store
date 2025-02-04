from embedding.embed import TextToEmbedding


def test_embedder():
    try:
        embedder = TextToEmbedding()
        
        # Test 1: Single short text
        print("Test 1: Single short text")
        test_text = ["Hello world"]
        result = embedder.embed(test_text)
        print("Test 1 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        # Test 2: Multiple short texts
        print("Test 2: Multiple short texts")
        test_texts = [
            "Hello world",
            "This is a test",
            "Multiple sentences"
        ]
        result = embedder.embed(test_texts)
        print("Test 2 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        # Test 3: Longer text
        print("Test 3: Longer text")
        long_text = ["This is a longer text that contains multiple sentences. " * 10]
        result = embedder.embed(long_text)
        print("Test 3 successful. Embedding shape:", len(result[1]), len(result[1][0]))
        
        return "All tests completed successfully!"
        
    except Exception as e:
        print(f"Test execution error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("\n=== Starting Tests ===")
        result = test_embedder()
        print(result)
        print("=== Tests Complete ===\n")
        
    except Exception as e:
        print(f"Main execution error: {str(e)}")
        raise
