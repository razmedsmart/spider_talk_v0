import json
import difflib
import random

def calculate_similarity(string1, string2):
    # Calculate the similarity ratio between the two strings
    similarity_ratio = difflib.SequenceMatcher(None, string1, string2).ratio()
    return similarity_ratio

class JsonResponseLoader:
    def __init__(self, file_path):
        # Open and load JSON data from the specified file
        with open(file_path, 'r') as file:
            self.data = json.load(file)

    def keys(self):
        return self.data.keys()


    def get_response_list(self, key_word, text_list):
        if key_word == text_list:
            if key_word in self.data:
                return self.data[key_word][f"response0"], self.data[key_word][f"response1"]
            else:
                print(f"{key_word} missing")
        # Check if key_word is directly a key
        if key_word in self.data:
            same_words = self.data[key_word]["same"]
            for w in text_list:
                for word in same_words:
                    similarity = calculate_similarity(w, word)
                    if similarity > 0.8:
                        print(f"found {word}")
                        return self.data[key_word][f"response0"], self.data[key_word][f"response1"]
        return None, None

    def is_key_found(self, key_word, text_list):
        if key_word in self.data:
            same_words = self.data[key_word]["same"]
            for w in text_list:
                for word in same_words:
                    similarity = calculate_similarity(w, word)
                    if similarity > 0.8:
                        print(f"found {word}")
                        return True
        return False
    # def get_response(self, key_word, text_list):
    #     # Check if key_word is directly a key
    #     response_list, response_list1 = self.get_response_list(key_word, text_list)
    #     if response_list is None:
    #         return None
    #     else:
    #         print(f"{response_list}\n {response_list1}")
    #         a = random.choice(response_list)
    #         b = random.choice(response_list1)
    #         return [a, b]

    def get_same(self, key_word):
        # Check if key_word is directly a key
        if key_word in self.data:
            return self.data[key_word]["same"]
        # Return None if key_word is not found
        print(f"{key_word}  not found")
        return None

# Example usage
if __name__ == "__main__":
    # Assuming 'response.json' is in the same directory as this script
    file_path = 'response.json'
    loader = JsonResponseLoader(file_path)

    # Test the function with different keywords
    print(loader.get_response("hello"))  # Should return 'hi.wav'
    print(loader.get_response("hi"))     # Should also return 'hi.wav'
    print(loader.get_response("שמח"))    # Should also return
    print(loader.get_response("עצוב"))    # Should also return
