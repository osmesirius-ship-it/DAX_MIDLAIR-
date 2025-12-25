"""
Extended Detection & Integration (EDI) v1
Computes salience, coherence, and anomaly phase signatures for DAX governance system
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Utilities
# -----------------------------
def zscore(x, eps=1e-9):
    """Standardize signal to zero mean, unit variance"""
    x = np.asarray(x)
    return (x - x.mean()) / (x.std() + eps)

def moving_mean(x, w):
    """Moving average filter"""
    x = np.asarray(x)
    if w <= 1:
        return x.copy()
    k = np.ones(w) / w
    return np.convolve(x, k, mode="same")

def spectral_entropy(x, fs, nfft=256, eps=1e-12):
    """
    Shannon entropy of normalized power spectrum in [0,1].
    Higher = flatter/noisier. Lower = structured/tonal.
    """
    x = np.asarray(x)
    if len(x) < nfft:
        # pad
        pad = np.zeros(nfft - len(x))
        x = np.concatenate([x, pad])
    X = np.fft.rfft(x[:nfft] * np.hanning(nfft))
    P = (np.abs(X) ** 2)
    P = P / (P.sum() + eps)
    H = -(P * np.log(P + eps)).sum()
    H_norm = H / np.log(len(P) + eps)
    return float(np.clip(H_norm, 0.0, 1.0))

def phase_drift_metric(x, y, fs, nfft=256, eps=1e-12):
    """
    Lightweight phase drift proxy:
    compute cross-spectrum phase at dominant frequency of x.
    Return absolute phase difference in [0, pi].
    """
    x = np.asarray(x); y = np.asarray(y)
    if len(x) < nfft:
        x = np.pad(x, (0, nfft-len(x)))
        y = np.pad(y, (0, nfft-len(y)))
    wx = x[:nfft] * np.hanning(nfft)
    wy = y[:nfft] * np.hanning(nfft)
    X = np.fft.rfft(wx)
    Y = np.fft.rfft(wy)
    Pxx = np.abs(X)**2
    k = int(np.argmax(Pxx[1:]) + 1)  # ignore DC
    cross = X[k] * np.conj(Y[k])
    phase = np.angle(cross)
    return float(np.abs(((phase + np.pi) % (2*np.pi)) - np.pi))  # wrap to [-pi,pi], abs

def xcorr_peak(x, y, max_lag=50):
    """
    Normalized cross-correlation peak magnitude in [0,1].
    """
    x = zscore(x); y = zscore(y)
    n = len(x)
    lags = range(-max_lag, max_lag+1)
    peaks = []
    for lag in lags:
        if lag < 0:
            a = x[:lag]
            b = y[-lag:]
        elif lag > 0:
            a = x[lag:]
            b = y[:-lag]
        else:
            a = x
            b = y
        if len(a) < 10:
            continue
        peaks.append(np.abs(np.corrcoef(a, b)[0,1]))
    return float(np.clip(np.max(peaks) if peaks else 0.0, 0.0, 1.0))

# -----------------------------
# EDI v1 Core Implementation
# -----------------------------
class EDIv1:
    """
    Extended Detection & Integration (v1)
    Computes:
      - salience S_k(t) for each channel
      - coherence C(t)
      - anomaly phase signature Phi(t) (feature vector)
    """
    def __init__(self, fs, window_s=2.0, channel_names=None):
        self.fs = fs
        self.w = max(32, int(window_s * fs))  # analysis window
        self.eps = 1e-9
        self.channel_names = channel_names or [f"ch_{i}" for i in range(4)]
        
        # Internal state tracking
        self._history_length = 1000
        self._coherence_history = []
        self._salience_history = []
        
        logger.info(f"EDI v1 initialized: fs={fs}Hz, window={window_s}s, channels={len(self.channel_names)}")

    def step(self, X, R, key_pairs=None):
        """
        Process new sensor data and return EDI outputs
        
        Args:
            X: (T, K) sensor streams
            R: (T, K) residual streams  
            key_pairs: list of (i,j) indices for phase/correlation tracking
            
        Returns:
            S: (K,) salience per channel [0,1]
            C: coherence scalar [0,1]
            Phi: dict with anomaly phase signature features
        """
        T, K = X.shape
        w = min(self.w, T)
        xw = X[-w:, :]
        rw = R[-w:, :]

        # Per-channel features
        ent = np.array([spectral_entropy(xw[:,k], fs=self.fs) for k in range(K)])
        res = np.array([np.mean(np.abs(zscore(rw[:,k]))) for k in range(K)])  # residual surprise proxy

        # Pairwise features (phase drift + correlation spikes)
        if key_pairs is None:
            key_pairs = [(0,1), (2,3)]  # Default pairs
        ph = []
        cc = []
        for (i,j) in key_pairs:
            if i < K and j < K:  # Ensure valid indices
                ph.append(phase_drift_metric(xw[:,i], xw[:,j], fs=self.fs))
                cc.append(xcorr_peak(xw[:,i], xw[:,j], max_lag=int(0.2*self.fs)))
        ph = np.array(ph)  # radians in [0,pi]
        cc = np.array(cc)  # [0,1]

        # Normalize phase drift into [0,1] (0 good, 1 bad)
        ph_norm = np.clip(ph / np.pi, 0.0, 1.0)

        # Salience: weighted combo of "noisier" + "residual surprise"
        S_raw = 0.55*ent + 0.45*np.clip(res / (np.max(res)+self.eps), 0, 1)
        S = np.clip(S_raw, 0.0, 1.0)

        # Coherence: high when entropy low, residual low, phase drift low, correlation stable
        C = 1.0 - np.clip(
            0.35*np.mean(ent) +
            0.35*np.clip(np.mean(res)/(np.max(res)+self.eps), 0, 1) +
            0.20*np.mean(ph_norm) +
            0.10*np.mean(cc),
            0.0, 1.0
        )

        Phi = {
            "entropy_mean": float(np.mean(ent)),
            "residual_mean": float(np.mean(res)),
            "phase_drift_mean": float(np.mean(ph_norm)),
            "xcorr_peak_mean": float(np.mean(cc)),
            "phase_drift_pairs": ph_norm.tolist(),
            "xcorr_pairs": cc.tolist(),
            "channel_entropies": ent.tolist(),
            "channel_residuals": res.tolist(),
            "timestamp": np.datetime64('now').astype('int64')
        }
        
        # Update internal history
        self._coherence_history.append(C)
        self._salience_history.append(S.copy())
        if len(self._coherence_history) > self._history_length:
            self._coherence_history.pop(0)
            self._salience_history.pop(0)
        
        return S, float(np.clip(C, 0.0, 1.0)), Phi

    def get_coherence_trend(self, window=50):
        """Get recent coherence trend for anomaly detection"""
        if len(self._coherence_history) < window:
            return 0.0
        recent = self._coherence_history[-window:]
        return np.mean(recent) - np.mean(self._coherence_history[-2*window:-window]) if len(self._coherence_history) >= 2*window else 0.0

    def get_salience_trends(self, window=50):
        """Get per-channel salience trends"""
        if len(self._salience_history) < window:
            return np.zeros(len(self.channel_names))
        
        recent = np.array(self._salience_history[-window:])
        if len(self._salience_history) >= 2*window:
            older = np.array(self._salience_history[-2*window:-window])
            return np.mean(recent, axis=0) - np.mean(older, axis=0)
        return np.mean(recent, axis=0)

    def get_system_health(self):
        """Overall system health assessment"""
        if not self._coherence_history:
            return {"health": 0.5, "trend": 0.0, "status": "initializing"}
        
        current_c = self._coherence_history[-1]
        trend = self.get_coherence_trend()
        
        if current_c > 0.8 and trend > -0.1:
            status = "healthy"
        elif current_c > 0.6:
            status = "degraded"
        elif current_c > 0.4:
            status = "critical"
        else:
            status = "emergency"
            
        return {
            "health": current_c,
            "trend": trend,
            "status": status,
            "coherence_history_len": len(self._coherence_history)
        }

# -----------------------------
# DAX Integration Layer
# -----------------------------
class DAXEDIPlanner:
    """
    DAX-style planner that uses EDI outputs to bias control decisions
    """
    def __init__(self, learning_rate=0.08, risk_threshold=0.4):
        self.lr = learning_rate
        self.risk_threshold = risk_threshold
        self.knobs = {
            "focus": 0.8,           # Attention stability
            "entanglement": 0.5,    # Coupling between decisions
            "interference": 0.3,    # Noise/risk tolerance
            "exploration": 0.4      # Novelty seeking
        }
        
    def step(self, S, C, Phi, channel_names=None):
        """
        Update DAX control knobs based on EDI outputs
        
        Args:
            S: salience per channel
            C: coherence scalar
            Phi: anomaly phase signature
            channel_names: optional channel name mapping
            
        Returns:
            Updated knobs dictionary
        """
        channel_names = channel_names or [f"ch_{i}" for i in range(len(S))]
        
        focus = self.knobs["focus"]
        ent = self.knobs["entanglement"]
        interf = self.knobs["interference"]
        expl = self.knobs["exploration"]

        # Coherence pressure: low C => reduce entanglement & interference, increase focus stability
        pressure = (1.0 - C)

        ent = np.clip(ent * (1.0 - 0.6*pressure), 0.0, 1.0)
        interf = np.clip(interf * (1.0 - 0.8*pressure), 0.0, 1.0)
        focus = np.clip(focus + self.lr*(0.15*C - 0.10*pressure), 0.0, 1.0)
        
        # Exploration: reduce in low coherence, increase in moderate coherence
        if C < self.risk_threshold:
            expl = np.clip(expl * (1.0 - 0.5*pressure), 0.0, 1.0)
        elif C > 0.7:
            expl = np.clip(expl + self.lr*0.1*(C - 0.7), 0.0, 1.0)

        # Salience rules (example policy):
        # if EM (channel 2) salient -> reduce interference more (treat as noise risk)
        if len(S) > 2 and S[2] > 0.7:
            interf = np.clip(interf * (1.0 - 0.25*S[2]), 0.0, 1.0)

        # if vibration (channel 1) salient -> reduce entanglement (avoid coupled decisions)
        if len(S) > 1 and S[1] > 0.7:
            ent = np.clip(ent * (1.0 - 0.25*S[1]), 0.0, 1.0)

        # Update knobs
        self.knobs.update({
            "focus": float(focus),
            "entanglement": float(ent),
            "interference": float(interf),
            "exploration": float(expl)
        })
        
        return self.knobs.copy()

    def get_risk_assessment(self, S, C):
        """Assess current risk level based on EDI outputs"""
        risk_score = (1.0 - C) * 0.6 + np.mean(S) * 0.4
        
        if risk_score < 0.3:
            return {"level": "low", "score": risk_score, "actions": ["normal_operations"]}
        elif risk_score < 0.6:
            return {"level": "moderate", "score": risk_score, "actions": ["increased_monitoring"]}
        elif risk_score < 0.8:
            return {"level": "high", "score": risk_score, "actions": ["risk_mitigation"]}
        else:
            return {"level": "critical", "score": risk_score, "actions": ["emergency_protocols"]}

# -----------------------------
# Simulation Utilities
# -----------------------------
def simulate_scenario(fs, T_s, scenario="solar_storm", K=4, seed=7):
    """
    Generate synthetic sensor data for testing EDI
    
    Args:
        fs: sampling frequency (Hz)
        T_s: duration (seconds)
        scenario: scenario type
        K: number of channels
        seed: random seed
        
    Returns:
        t: time vector
        X: sensor data (T, K)
        R: residual data (T, K)
    """
    rng = np.random.default_rng(seed)
    T = int(T_s * fs)
    t = np.arange(T) / fs

    # Baselines
    thermal = 0.2*np.sin(2*np.pi*0.08*t) + 0.05*rng.normal(size=T)
    vib     = 0.15*np.sin(2*np.pi*0.6*t) + 0.07*rng.normal(size=T)
    em      = 0.10*np.sin(2*np.pi*0.15*t) + 0.05*rng.normal(size=T)
    power   = 0.05*np.sin(2*np.pi*0.03*t) + 0.03*rng.normal(size=T)

    # Residuals: predicted-observed mismatch proxy
    r_thermal = 0.03*rng.normal(size=T)
    r_vib     = 0.03*rng.normal(size=T)
    r_em      = 0.03*rng.normal(size=T)
    r_power   = 0.03*rng.normal(size=T)

    # Inject scenario dynamics
    if scenario == "solar_storm":
        # EM noise rises + power residual increases + phase relations drift
        storm = (t > 0.4*T_s) & (t < 0.75*T_s)
        em[storm] += 0.25*rng.normal(size=storm.sum())
        power[storm] += 0.10*np.sin(2*np.pi*0.2*t[storm])
        r_em[storm] += 0.12*rng.normal(size=storm.sum())
        r_power[storm] += 0.10*rng.normal(size=storm.sum())

    elif scenario == "micrometeoroid":
        # sharp vibration impulse + thermal bump + short residual spike
        hit_t = int(0.55*T)
        width = int(0.05*T)
        impulse = np.exp(-((np.arange(T)-hit_t)**2)/(2*(width**2)))
        vib += 0.9*impulse
        thermal += 0.35*impulse
        r_vib += 0.25*impulse
        r_thermal += 0.18*impulse

    elif scenario == "sensor_spoof":
        # correlated fake EM & power signals + residual mismatch pattern
        spoof = (t > 0.35*T_s) & (t < 0.65*T_s)
        fake = 0.35*np.sin(2*np.pi*0.9*t[spoof])
        em[spoof] += fake
        power[spoof] += 0.8*fake
        # residuals show "model doesn't believe it"
        r_em[spoof] += 0.20*rng.normal(size=spoof.sum())
        r_power[spoof] += 0.20*rng.normal(size=spoof.sum())

    X = np.stack([thermal, vib, em, power], axis=1)
    R = np.stack([r_thermal, r_vib, r_em, r_power], axis=1)
    return t, X, R

# -----------------------------
# Integration with DAX Core
# -----------------------------
class DAXEDIIntegration:
    """
    Integration layer between EDI and DAX governance core
    """
    def __init__(self, fs=200, window_s=2.0):
        self.edi = EDIv1(fs=fs, window_s=window_s)
        self.planner = DAXEDIPlanner()
        self.channel_names = ["thermal", "vibration", "EM", "power"]
        self.key_pairs = [(2,3), (0,2)]  # (EM,power), (thermal,EM)
        
    def process_sensor_data(self, sensor_data, residual_data):
        """
        Process new sensor data through EDI and update DAX knobs
        
        Args:
            sensor_data: (T, K) sensor streams
            residual_data: (T, K) residual streams
            
        Returns:
            dict with EDI outputs and updated DAX knobs
        """
        S, C, Phi = self.edi.step(sensor_data, residual_data, self.key_pairs)
        knobs = self.planner.step(S, C, Phi, self.channel_names)
        risk = self.planner.get_risk_assessment(S, C)
        health = self.edi.get_system_health()
        
        return {
            "salience": S.tolist(),
            "coherence": C,
            "phase_signature": Phi,
            "knobs": knobs,
            "risk_assessment": risk,
            "system_health": health,
            "channel_names": self.channel_names
        }
    
    def get_governance_bias(self):
        """
        Get current governance bias parameters for DAX core
        
        Returns:
            dict with bias parameters
        """
        knobs = self.planner.knobs
        health = self.edi.get_system_health()
        
        # Convert knobs to DAX governance parameters
        bias = {
            "risk_multiplier": 1.0 + (1.0 - health["health"]) * 2.0,
            "attention_focus": knobs["focus"],
            "decision_coupling": knobs["entanglement"],
            "noise_tolerance": knobs["interference"],
            "exploration_factor": knobs["exploration"],
            "coherence_weight": health["health"],
            "salience_weights": self.edi._salience_history[-1].tolist() if self.edi._salience_history else [0.25, 0.25, 0.25, 0.25]
        }
        
        return bias

if __name__ == "__main__":
    # Quick test run
    print("Testing EDI integration...")
    
    # Create integration
    edi_integration = DAXEDIIntegration(fs=200, window_s=2.0)
    
    # Generate test data
    t, X, R = simulate_scenario(200, 20, scenario="solar_storm")
    
    # Process data
    result = edi_integration.process_sensor_data(X, R)
    
    print(f"Coherence: {result['coherence']:.3f}")
    print(f"Risk Level: {result['risk_assessment']['level']}")
    print(f"System Health: {result['system_health']['status']}")
    print(f"Knobs: {result['knobs']}")
    
    print("EDI integration test complete!")
