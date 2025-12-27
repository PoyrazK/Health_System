"""
EKG Image to Signal Converter
OpenCV ile EKG görselinden sinyal çıkarma

Pipeline:
1. Görsel yükleme
2. Gri tonlama
3. Eşikleme (threshold)
4. Grid/arka plan temizleme
5. Sinyal çizgisi tespiti
6. Piksel → Sinyal
7. Feature extraction
8. Model prediction
"""

import cv2
import numpy as np
from scipy import signal as sig
from scipy.ndimage import gaussian_filter1d
from typing import Tuple, List, Dict, Optional
import os

class EKGImageProcessor:
    """EKG görselinden sinyal çıkarma sınıfı"""
    
    def __init__(self, target_length: int = 256):
        """
        Args:
            target_length: Çıkarılacak sinyal uzunluğu
        """
        self.target_length = target_length
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Görsel yükle"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {image_path}")
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Görsel okunamadı: {image_path}")
        
        return img
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Görsel ön işleme"""
        # Gri tonlama
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Gürültü azaltma
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Kontrast artırma (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        return enhanced
    
    def remove_grid(self, img: np.ndarray) -> np.ndarray:
        """Grid çizgilerini temizle (EKG kağıdı arka planı)"""
        # Yatay çizgileri temizle
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Dikey çizgileri temizle
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, vertical_kernel)
        
        # Grid'i çıkar
        grid = cv2.add(horizontal_lines, vertical_lines)
        cleaned = cv2.subtract(img, grid)
        
        return cleaned
    
    def extract_signal_line(self, img: np.ndarray) -> np.ndarray:
        """Sinyal çizgisini çıkar"""
        # Binary threshold
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphology ile temizle
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def trace_signal(self, binary_img: np.ndarray) -> np.ndarray:
        """Binary görüntüden sinyal değerlerini çıkar"""
        height, width = binary_img.shape
        signal = np.zeros(width)
        
        for x in range(width):
            column = binary_img[:, x]
            # Beyaz piksellerin y koordinatlarını bul
            white_pixels = np.where(column > 0)[0]
            
            if len(white_pixels) > 0:
                # Orta noktayı al (veya ağırlıklı ortalama)
                y_center = np.mean(white_pixels)
                # Normalize et (0-1 arası, üst = 1, alt = 0)
                signal[x] = 1 - (y_center / height)
            else:
                # Boş sütun - önceki değeri kullan
                signal[x] = signal[x-1] if x > 0 else 0.5
        
        return signal
    
    def smooth_signal(self, signal: np.ndarray) -> np.ndarray:
        """Sinyali düzleştir"""
        # Gaussian smoothing
        smoothed = gaussian_filter1d(signal, sigma=2)
        return smoothed
    
    def resample_signal(self, signal: np.ndarray) -> np.ndarray:
        """Sinyali hedef uzunluğa yeniden örnekle"""
        if len(signal) == self.target_length:
            return signal
        
        # Resample
        resampled = sig.resample(signal, self.target_length)
        return resampled
    
    def normalize_signal(self, signal: np.ndarray) -> np.ndarray:
        """Z-score normalizasyon"""
        mean = np.mean(signal)
        std = np.std(signal)
        if std == 0:
            return signal - mean
        return (signal - mean) / std
    
    def extract_signal(self, image_path: str) -> np.ndarray:
        """
        Tam pipeline: Görsel → Sinyal
        
        Args:
            image_path: EKG görsel dosya yolu
            
        Returns:
            Normalize edilmiş sinyal array'i
        """
        # 1. Yükle
        img = self.load_image(image_path)
        
        # 2. Ön işleme
        preprocessed = self.preprocess_image(img)
        
        # 3. Grid temizle
        cleaned = self.remove_grid(preprocessed)
        
        # 4. Sinyal çizgisini çıkar
        binary = self.extract_signal_line(cleaned)
        
        # 5. Sinyal değerlerini oku
        raw_signal = self.trace_signal(binary)
        
        # 6. Düzleştir
        smoothed = self.smooth_signal(raw_signal)
        
        # 7. Yeniden örnekle
        resampled = self.resample_signal(smoothed)
        
        # 8. Normalize et
        normalized = self.normalize_signal(resampled)
        
        return normalized
    
    def extract_signal_from_array(self, img_array: np.ndarray) -> np.ndarray:
        """Numpy array'den sinyal çıkar (API için)"""
        preprocessed = self.preprocess_image(img_array)
        cleaned = self.remove_grid(preprocessed)
        binary = self.extract_signal_line(cleaned)
        raw_signal = self.trace_signal(binary)
        smoothed = self.smooth_signal(raw_signal)
        resampled = self.resample_signal(smoothed)
        normalized = self.normalize_signal(resampled)
        return normalized


class EKGFeatureExtractor:
    """Sinyal özelliklerini çıkar"""
    
    def __init__(self, sampling_rate: int = 360):
        self.sampling_rate = sampling_rate
    
    def extract_features(self, signal: np.ndarray) -> Dict[str, float]:
        """Sinyal özelliklerini çıkar"""
        features = {}
        
        # Temel istatistikler
        features['mean'] = np.mean(signal)
        features['std'] = np.std(signal)
        features['min'] = np.min(signal)
        features['max'] = np.max(signal)
        features['rms'] = np.sqrt(np.mean(signal**2))
        
        # R-peak tespiti
        from scipy.signal import find_peaks
        peaks, properties = find_peaks(signal, distance=20, height=0.3)
        
        if len(peaks) > 1:
            # RR intervals
            rr_intervals = np.diff(peaks) / self.sampling_rate * 1000
            features['rr_mean'] = np.mean(rr_intervals)
            features['rr_std'] = np.std(rr_intervals)
            features['heart_rate'] = 60000 / features['rr_mean'] if features['rr_mean'] > 0 else 0
        else:
            features['rr_mean'] = 0
            features['rr_std'] = 0
            features['heart_rate'] = 0
        
        # Peak özellikleri
        features['peak_count'] = len(peaks)
        if len(peaks) > 0:
            features['avg_peak_height'] = np.mean(signal[peaks])
        else:
            features['avg_peak_height'] = 0
        
        return features


# ==========================================
# DEMO / TEST
# ==========================================

def demo_extract_signal(image_path: str = None):
    """Demo: Görüntüden sinyal çıkar"""
    print("=" * 60)
    print("EKG IMAGE TO SIGNAL CONVERTER - DEMO")
    print("=" * 60)
    
    processor = EKGImageProcessor(target_length=256)
    extractor = EKGFeatureExtractor()
    
    if image_path and os.path.exists(image_path):
        print(f"\nProcessing: {image_path}")
        
        try:
            # Sinyal çıkar
            signal = processor.extract_signal(image_path)
            print(f"Signal extracted: {len(signal)} samples")
            print(f"Signal range: [{signal.min():.2f}, {signal.max():.2f}]")
            
            # Özellik çıkar
            features = extractor.extract_features(signal)
            print(f"\nFeatures:")
            for name, value in features.items():
                print(f"  {name}: {value:.3f}")
            
            return signal, features
            
        except Exception as e:
            print(f"Error: {e}")
            return None, None
    else:
        print("\nNo image provided. Creating synthetic demo...")
        
        # Sentetik EKG görüntüsü oluştur
        height, width = 200, 800
        img = np.ones((height, width), dtype=np.uint8) * 255
        
        # Sentetik sinyal çiz
        x = np.linspace(0, 4*np.pi, width)
        y = np.sin(x) * 50 + np.sin(3*x) * 20 + height//2
        
        for i in range(width-1):
            cv2.line(img, 
                    (i, int(y[i])), 
                    (i+1, int(y[i+1])), 
                    (0, 0, 0), 2)
        
        # Test
        signal = processor.extract_signal_from_array(img)
        features = extractor.extract_features(signal)
        
        print(f"Synthetic signal: {len(signal)} samples")
        print(f"\nFeatures:")
        for name, value in features.items():
            print(f"  {name}: {value:.3f}")
        
        return signal, features


if __name__ == "__main__":
    demo_extract_signal()
