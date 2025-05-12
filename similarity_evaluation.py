from rapidfuzz import fuzz
import re

base_path = "sample_data_evaluation_spring_news" # Path of folder that you want to evaluation similarity score

def normalize(text):
    # Remove leading/trailing whitespace, collapse all whitespace to a single space
    return re.sub(r'\s+', ' ', text).strip()

# Test 10 samples
for index in range(1,7):

# Test some samples
# for index in range(5,6):
    # Read the two text files
    with open(f"{base_path}/original_content/file{index}.txt", "r", encoding="utf-8") as original, open(f"{base_path}/scraped_content/file{index}.txt", "r", encoding="utf-8") as scraped:
        # Remove "Content:" at the beginning (if present)
        text1 = normalize(original.read())
        text2 = normalize(scraped.read())
        cleaned_content_text2 = text2.replace("Content:", "", 1).lstrip()
        # print(text1)
        # print(cleaned_content_text2)

    # Compare similarity (ratio returns a percentage similarity)
    similarity_score = fuzz.ratio(text1, cleaned_content_text2)
    # similarity_score = fuzz.ratio(text1, text2)

    print(f"Similarity sample {index}: {similarity_score:.2f}%")