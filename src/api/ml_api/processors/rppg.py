import numpy as np
from scipy import signal
import time

class RPPGProcessor:
    def __init__(self, fps=30, buffer_size=300):
        self.fps = fps
        self.buffer_size = buffer_size # 300 frames = 10 seconds approx
        self.raw_signal = []
        self.timestamps = []
        self.filtered_signal = []
        self.last_snr = 0.0
        
        # Filter Design (0.75Hz to 3.0Hz = 45 to 180 BPM)
        self.low_cut = 0.75
        self.high_cut = 3.0
        
    def add_sample(self, val, timestamp):
        """Adds a new raw green channel average and timestamp."""
        self.raw_signal.append(val)
        self.timestamps.append(timestamp)
        
        if len(self.raw_signal) > self.buffer_size:
            self.raw_signal.pop(0)
            self.timestamps.pop(0)

    def process(self):
        """
        Calculates Heart Rate using FFT.
        Returns: BPM (float) or None if insufficient data
        """
        if len(self.raw_signal) < self.fps * 3: # Need at least 3 seconds
            return None
        
        # 1. Interpolation (Jitter Correction)
        # Create a perfect time grid
        t = np.array(self.timestamps)
        y = np.array(self.raw_signal)
        
        # Normalize time to start at 0
        t = (t - t[0]) / 1000.0 # Convert ms to seconds
        
        # Create even sampling
        num_samples = int(t[-1] * self.fps)
        if num_samples < 10: 
            return None
            
        even_times = np.linspace(0, t[-1], num_samples)
        
        # Interpolate
        try:
            resampled_signal = np.interp(even_times, t, y)
        except Exception as e:
            print(f"Interpolation error: {e}")
            return None
        
        # 2. Detrending (Remove non-stationary trend)
        detrended = signal.detrend(resampled_signal)
        
        # 3. Normalization
        mean_val = np.mean(detrended)
        std_val = np.std(detrended)
        if std_val == 0:
            return None
        normalized = (detrended - mean_val) / std_val
        
        # 4. Butterworth Bandpass Filter
        nyquist = 0.5 * self.fps
        low = self.low_cut / nyquist
        high = self.high_cut / nyquist
        b, a = signal.butter(2, [low, high], btype='band')
        filtered = signal.filtfilt(b, a, normalized)
        
        # Store for Visualization
        self.latest_filtered_samples = filtered
        self.last_snr = 0.0
        
        # 5. FFT
        n = len(filtered)
        freqs = np.fft.rfftfreq(n, d=1/self.fps)
        magnitude = np.abs(np.fft.rfft(filtered))
        
        # 6. Peak Frequency
        # Mask out frequencies outside human range (already filtered but safe to mask)
        mask = (freqs >= self.low_cut) & (freqs <= self.high_cut)
        valid_freqs = freqs[mask]
        valid_mags = magnitude[mask]
        
        if len(valid_mags) == 0:
            return None
            
        peak_idx = np.argmax(valid_mags)
        peak_freq = valid_freqs[peak_idx]
        
        # 7. SNR Calculation (Signal power at peak vs Rest)
        # Power is magnitude squared
        power = magnitude ** 2
        total_power = np.sum(power)
        
        # Signal power (Peak + 2 neighbors on each side for robustness)
        full_peak_idx = np.where(freqs == peak_freq)[0][0]
        start = max(0, full_peak_idx - 2)
        end = min(len(power), full_peak_idx + 3)
        signal_power = np.sum(power[start:end])
        
        self.last_snr = signal_power / (total_power - signal_power) if (total_power - signal_power) > 0 else 0.0
        
        bpm = peak_freq * 60.0
        return bpm
