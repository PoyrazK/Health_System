import os
import sys
from pathlib import Path

try:
    import kaggle
except ImportError:
    print("❌ 'kaggle' library not found. Run: pip install kaggle")
    sys.exit(1)

# Target Datasets
DATASETS = {
    # 1. Diabetes (Primary Metabolic)
    "diabetes": "alexteboul/diabetes-health-indicators-dataset",
    
    # 2. Heart Attack (Primary Cardiovascular)
    "heart": "rashikrahmanpritom/heart-attack-analysis-prediction-dataset",
    
    # 3. Stroke (Neurological - High Overlap)
    "stroke": "fedesoriano/stroke-prediction-dataset",
    
    # 4. Kidney (Renal - Complication)
    "kidney": "mansoordaku/ckdisease" 
}

DATA_DIR = Path("data/raw")

def download_all():
    print(f"🚀 Starting download to {DATA_DIR}...")
    
    for name, slug in DATASETS.items():
        target_dir = DATA_DIR / name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n⬇️ Downloading {name.upper()} dataset ({slug})...")
        try:
            kaggle.api.dataset_download_files(
                slug,
                path=target_dir,
                unzip=True
            )
            print(f"✅ {name} downloaded successfully.")
        except Exception as e:
            print(f"⚠️ Failed to download {name}: {e}")

    print("\n📦 All downloads processed.")

if __name__ == "__main__":
    # Ensure kaggle.json exists
    if not (Path.home() / ".kaggle/kaggle.json").exists():
        print("⚠️ Warning: ~/.kaggle/kaggle.json not found. API calls may fail.")
    else:
        download_all()
