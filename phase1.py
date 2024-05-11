import os
import pandas as pd
import librosa
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pymongo import MongoClient

# Function to extract audio features
def extract_features(audio_file):
    # Load audio file
    y, sr = librosa.load(audio_file, sr=None)
    
    # Extract MFCC (Mel-Frequency Cepstral Coefficients) features
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Calculate spectral centroid
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    
    # Calculate zero-crossing rate
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    
    return mfccs, spectral_centroid, zero_crossing_rate

# Function for normalization
def normalize_features(features):
    return (features - features.min()) / (features.max() - features.min())

# Function for standardization
def standardize_features(features):
    scaler = StandardScaler()
    return scaler.fit_transform(features)

# Function for dimensionality reduction using PCA
def reduce_dimensionality(features, n_components=100):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(features)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['music_recommendation']
collection = db['audio_features']

# Paths to dataset and metadata
dataset_path = 'path_to_fma_small_zip'
metadata_path = 'path_to_fma_metadata_csv'  # Assuming metadata is in CSV format

# Check if dataset directory exists
if not os.path.exists(dataset_path):
    print("FMA dataset directory not found. Please download and extract the dataset.")
    # Add instructions for downloading the dataset
    # Exit or handle the absence of the dataset directory accordingly
    exit()

# Load metadata
metadata = pd.read_csv(metadata_path, index_col=0)

# Iterate over audio files
for root, dirs, files in os.walk(dataset_path):
    for file in files:
        audio_file = os.path.join(root, file)
        track_id = int(os.path.splitext(file)[0])  # Extract track ID from file name
        
        # Extract features from audio file
        mfccs, spectral_centroid, zero_crossing_rate = extract_features(audio_file)
        
        # Normalize or standardize features
        normalized_mfccs = normalize_features(mfccs)
        standardized_spectral_centroid = standardize_features(spectral_centroid)
        
        # Apply dimensionality reduction
        reduced_mfccs = reduce_dimensionality(normalized_mfccs)
        
        # Load metadata for the current audio file
        metadata_row = metadata.loc[track_id]
        
        # Insert audio features and metadata into MongoDB collection
        collection.insert_one({
            'track_id': track_id,
            'audio_file': audio_file,
            'mfccs': normalized_mfccs.tolist(),
            'spectral_centroid': standardized_spectral_centroid.tolist(),
            'zero_crossing_rate': zero_crossing_rate.tolist(),
            'artist': metadata_row['artist'],
            'title': metadata_row['title'],
            'genres': metadata_row['genres'].split('|'),
            'tags': metadata_row['tags'].split('|'),
            'play_count': metadata_row['play_count']
        })

client.close()  # Close MongoDB connection
