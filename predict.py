# from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
# from sklearn.base import BaseEstimator, TransformerMixin
# from sklearn.preprocessing import LabelEncoder
# from text_extraction import extract_text_from_file
# import argparse
# import re
# import pandas as pd
# import string

# # Custom text cleaning and preprocessing class
# class TextPreprocessor(BaseEstimator, TransformerMixin):
#     def __init__(self):
#         pass
    
#     def fit(self, X, y=None):
#         return self
    
#     def transform(self, X):
#         def clean_text(text):
#             text = text.lower()
#             text = re.sub(r'http\S+|www\S+|https\S+', '', text)
#             text = re.sub(r'\S+@\S+', '', text)
#             text = re.sub(r'\b\d{1,3}[-./]?\d{1,3}[-./]?\d{1,4}\b', '', text)
#             text = re.sub(r'\[.*?\]', ' ', text)
#             text = re.sub("\\W", " ", text)
#             text = re.sub('<.*?>+', ' ', text)
#             text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
#             text = re.sub('\n', ' ', text)
#             text = re.sub(r'\w*\d\w*', ' ', text)
#             text = re.sub(r'[^a-zA-Z]', ' ', text)
#             text = re.sub(r'\s+', ' ', text)
#             tokens = text.split()
#             tokens = [word for word in tokens if word not in ENGLISH_STOP_WORDS]
#             return ' '.join(tokens).strip()

#         return [clean_text(text) for text in X]
    
# # Define file paths
# label_encoder_path = "models/label_encoder.pkl"
# tfidf = "models/tfidf.pkl"
# clf = "models/clf.pkl"

# # Apply preprocessing
# preprocessor = TextPreprocessor()
# # Encode labels
# le = LabelEncoder()

# def predict_label_from_file(filepath):
#     #Extract text from resume
#     resume_text = extract_text_from_file(filepath)
    
#     #Clean the data
#     cleaned_resume = preprocessor.transform([resume_text])[0]
    
#     input_features = tfidf.transform([cleaned_resume])
#     prediction_id = clf.predict(input_features)[0]
    
#     #Predict label
#     predicted_label = le.inverse_transform([prediction_id])[0]
#     return predicted_label

# # Parse command line arguments
# def main():
#     parser = argparse.ArgumentParser(description='Predict the label for a resume based on the provided file path.')
#     parser.add_argument('filepath', type=str, help='Path to the resume file')
#     args = parser.parse_args()
    
#     predicted_label = predict_label_from_file(args.filepath)
#     print(f"Predicted Label: {predicted_label}")

# if __name__ == "__main__":
#     main()