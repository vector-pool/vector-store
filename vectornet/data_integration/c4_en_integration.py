from datasets import load_dataset
import os

# Load the dataset with streaming enabled
dataset = load_dataset(
    "allenai/c4",  # Updated to use allenai/c4 as per the warning
    "en",
    split="train",
    streaming=True,
    trust_remote_code=True
)

# Function to save a specific number of examples with length filter
def save_subset(dataset, num_examples, min_length, output_file):
    count = 0
    data = []
    total_checked = 0
    
    print("Collecting examples...")
    for example in dataset:
        total_checked += 1
        if len(example['text']) >= min_length:
            data.append(example)
            count += 1
            if count % 1000 == 0:
                print(f"Collected {count} examples...")
        if count >= num_examples:
            break
        if total_checked % 10000 == 0:
            print(f"Checked {total_checked} articles, found {count} matching examples...")
    
    print(f"\nTotal articles checked: {total_checked}")
    print(f"Articles collected: {count}")
    print(f"Filter rate: {(count/total_checked)*100:.2f}%")
    
    # Convert to regular dataset and save
    from datasets import Dataset
    subset = Dataset.from_list(data)
    subset.save_to_disk(output_file)
    return subset

# Start with a small number of examples
output_dir = "c4_en_subset"
subset = save_subset(
    dataset, 
    num_examples=50000, 
    min_length=10000,  # Only keep articles with 10000+ characters
    output_file=output_dir
)

# Check the size
def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert to MB

size_mb = get_directory_size(output_dir)
print(f"\nDownloaded dataset size: {size_mb:.2f} MB")
print(f"Number of examples: {len(subset)}")

# Quick verification of lengths
lengths = [len(example['text']) for example in subset]
print(f"\nLength verification:")
print(f"Min length: {min(lengths)}")
print(f"Max length: {max(lengths)}")
print(f"Average length: {sum(lengths)/len(lengths):.2f}")


from datasets import load_from_disk

dataset = load_from_disk("allenai/c4", "en", streaming=True)
random_sample = dataset["train"].shuffle(seed=42).take(1)



from datasets import load_dataset
import os

# Load the dataset with streaming enabled
dataset = load_dataset(
    "c4",
    "en",
    split="train",
    streaming=True,
    trust_remote_code=True
)

# Function to save a specific number of examples
def save_subset(dataset, num_examples, min_length, output_file):
    count = 0
    data = []
    total_checked = 0
    print("Collecting examples...")
    for example in dataset:
        total_checked += 1
        if len(example['text']) >= min_length:
            data.append(example)
            count += 1
            if count % 1000 == 0:
                print(f"Collected {count} examples...")
        if count >= num_examples:
            break
        if total_checked % 10000 == 0:
            print(f"Checked {total_checked} articles, found {count} matching examples...")

    # print("Collecting examples...")
    # for example in dataset:
    #     data.append(example)
    #     count += 1
    #     if count >= num_examples:
    #         break
    #     if count % 1000 == 0:
    #         print(f"Collected {count} examples...")
    
    # Convert to regular dataset and save
    from datasets import Dataset
    subset = Dataset.from_list(data)
    subset.save_to_disk(output_file)
    return subset

# Start with a small number of examples (adjust this number to get closer to 300MB)
output_dir = "c4_10000_dataset"
subset = save_subset(dataset, num_examples=3000, min_length = 10000, output_file=output_dir)

# Check the size
def get_directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert to MB

size_mb = get_directory_size(output_dir)
print(f"Downloaded dataset size: {size_mb:.2f} MB")
print(f"Number of examples: {len(subset)}")




