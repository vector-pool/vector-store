# This script assists in converting text length to the storage size in Python bytes per character.

def text_length_to_storage_size(length):
    """
    Convert text length to storage size in GB.
    Assumes each character is 4 bytes.

    Parameters:
    - length (int): The number of characters in the text.

    Returns:
    - float: The storage size in GB.
    """
    bytes_per_character = 4

    total_bytes = length * bytes_per_character

    gb_size = total_bytes / (1024 ** 3)

    return gb_size

if __name__ == "__main__":
    text_length = int(input("Enter the text length (number of characters): "))
    
    storage_size_gb = text_length_to_storage_size(text_length)
    print(f"Storage size: {storage_size_gb:.6f} GB")