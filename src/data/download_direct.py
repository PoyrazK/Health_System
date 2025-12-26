import os
import requests
from pathlib import Path

# Updated raw URLs with active mirrors found via search
DATASETS = {
    "diabetes": "https://raw.githubusercontent.com/Helmy2/Diabetes-Health-Indicators/main/diabetes_binary_health_indicators_BRFSS2015.csv",
    "heart": "https://raw.githubusercontent.com/FarzadNekouee/Heart_Disease_Prediction/main/heart.csv",
    "stroke": "https://raw.githubusercontent.com/saxenamansi/Healthcare_dataset_pandas_preprocessing/main/healthcare-dataset-stroke-data.csv",
    "kidney": "https://raw.githubusercontent.com/aiplanethub/Datasets/master/Chronic%20Kidney%20Disease%20(CKD)%20Dataset/ChronicKidneyDisease.csv"
}

DATA_DIR = Path("data/raw")

def download_file(url, destination):
    print(f"⬇️ Downloading {url}...")
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Saved to {destination}")
        else:
            print(f"❌ Failed to download {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in DATASETS.items():
        dest = DATA_DIR / f"{name}.csv"
        # Check if file exists and is not empty description
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"⏩ {name}.csv already exists, skipping.")
            continue
        download_file(url, dest)
    print("\n📦 Processing complete.")

if __name__ == "__main__":
    main()
