"""
SHAP Explainer Caching System

Pre-computes and caches SHAP explainers for faster UI responses.
Implements lazy loading and background refresh for optimal performance.
"""

import os
import pickle
import threading
import time
from typing import Dict, Any, Optional
import joblib
from pathlib import Path
import numpy as np
import pandas as pd

# Global cache storage
_shap_cache = {}
_cache_lock = threading.Lock()
_cache_dir = Path("cache/shap")

class SHAPCache:
    """Manages SHAP explainer caching and lazy loading"""
    
    def __init__(self, cache_dir: str = "cache/shap"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache = {}
        self._cache_timestamps = {}
        self.cache_ttl = 3600  # 1 hour TTL for cache entries
        
    def _get_cache_key(self, model_type: str, feature_names: list) -> str:
        """Generate cache key based on model type and features"""
        features_hash = hash(tuple(sorted(feature_names)))
        return f"{model_type}_{features_hash}"
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cached explainer"""
        return self.cache_dir / f"{cache_key}_explainer.pkl"
    
    def save_explainer(self, explainer, model_type: str, feature_names: list):
        """Save SHAP explainer to disk and memory cache"""
        cache_key = self._get_cache_key(model_type, feature_names)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Save to disk
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'explainer': explainer,
                    'feature_names': feature_names,
                    'model_type': model_type,
                    'timestamp': time.time()
                }, f)
            
            # Save to memory cache
            with _cache_lock:
                self._memory_cache[cache_key] = explainer
                self._cache_timestamps[cache_key] = time.time()
                
            print(f" SHAP explainer cached for {model_type}")
            
        except Exception as e:
            print(f" Error caching SHAP explainer: {e}")
    
    def load_explainer(self, model_type: str, feature_names: list) -> Optional[Any]:
        """Load SHAP explainer from memory or disk cache"""
        cache_key = self._get_cache_key(model_type, feature_names)
        
        # Try memory cache first
        with _cache_lock:
            if cache_key in self._memory_cache:
                # Check if cache is still valid
                if time.time() - self._cache_timestamps.get(cache_key, 0) < self.cache_ttl:
                    return self._memory_cache[cache_key]
                else:
                    # Remove expired cache
                    del self._memory_cache[cache_key]
                    del self._cache_timestamps[cache_key]
        
        # Try disk cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Check if disk cache is still valid
                if time.time() - cached_data.get('timestamp', 0) < self.cache_ttl:
                    explainer = cached_data['explainer']
                    
                    # Load back into memory cache
                    with _cache_lock:
                        self._memory_cache[cache_key] = explainer
                        self._cache_timestamps[cache_key] = time.time()
                    
                    return explainer
                else:
                    # Remove expired disk cache
                    cache_path.unlink()
                    
            except Exception as e:
                print(f" Error loading cached explainer: {e}")
                
        return None
    
    def get_or_create_explainer(self, model, X_sample, model_type: str, feature_names: list):
        """Get explainer from cache or create new one"""
        # Try to load from cache first
        explainer = self.load_explainer(model_type, feature_names)
        
        if explainer is not None:
            return explainer
        
        # Create new explainer if not cached
        print(f" Creating new SHAP explainer for {model_type}...")
        try:
            import shap
            
            if model_type == "xgboost":
                explainer = shap.TreeExplainer(model)
            elif model_type == "logistic":
                explainer = shap.LinearExplainer(model, X_sample)
            else:
                # Default to KernelExplainer for unknown model types
                explainer = shap.KernelExplainer(model.predict_proba, X_sample[:100])
            
            # Cache the new explainer
            self.save_explainer(explainer, model_type, feature_names)
            return explainer
            
        except Exception as e:
            print(f" Error creating SHAP explainer: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached explainers"""
        with _cache_lock:
            self._memory_cache.clear()
            self._cache_timestamps.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*_explainer.pkl"):
            cache_file.unlink()
        
        print(" SHAP cache cleared")
    
    def precompute_explainers(self, models_dict: Dict[str, Any], sample_data: pd.DataFrame):
        """Pre-compute explainers for all models"""
        print(" Pre-computing SHAP explainers...")
        
        for model_name, model_info in models_dict.items():
            try:
                model = model_info['model']
                feature_names = list(sample_data.columns)
                
                # Create sample for explainer initialization
                X_sample = sample_data.values[:100] if len(sample_data) > 100 else sample_data.values
                
                # Pre-compute explainer
                explainer = self.get_or_create_explainer(
                    model, X_sample, model_name, feature_names
                )
                
                if explainer:
                    print(f" Pre-computed explainer for {model_name}")
                else:
                    print(f" Failed to pre-compute explainer for {model_name}")
                    
            except Exception as e:
                print(f" Error pre-computing explainer for {model_name}: {e}")

# Global cache instance
shap_cache = SHAPCache()

def cache_shap_explainers(credit_model):
    """
    Cache SHAP explainers for the credit model
    
    Args:
        credit_model: The trained credit risk model
    """
    try:
        # Create sample data for explainer initialization
        sample_features = {
            'age': [25, 30, 35, 40, 45],
            'income': [30000, 50000, 70000, 90000, 120000],
            'employment_length': [1, 2, 5, 8, 10],
            'debt_to_income': [0.1, 0.2, 0.3, 0.4, 0.5],
            'credit_utilization': [0.1, 0.2, 0.3, 0.4, 0.5],
            'payment_history_score': [60, 70, 80, 90, 95],
            'account_diversity': [1, 2, 3, 4, 5],
            'savings_rate': [0.05, 0.1, 0.15, 0.2, 0.25]
        }
        
        sample_df = pd.DataFrame(sample_features)
        
        # Dictionary of models to cache
        models_to_cache = {}
        
        if hasattr(credit_model, 'xgb_model') and credit_model.xgb_model:
            models_to_cache['xgboost'] = {'model': credit_model.xgb_model}
            
        if hasattr(credit_model, 'logistic_model') and credit_model.logistic_model:
            models_to_cache['logistic'] = {'model': credit_model.logistic_model}
        
        # Pre-compute explainers
        shap_cache.precompute_explainers(models_to_cache, sample_df)
        
        print(" SHAP explainer caching completed!")
        
    except Exception as e:
        print(f" Error in SHAP caching: {e}")

def get_cached_shap_values(model, X, model_type: str, feature_names: list):
    """
    Get SHAP values using cached explainer
    
    Args:
        model: The ML model
        X: Input features
        model_type: Type of model ('xgboost', 'logistic', etc.)
        feature_names: List of feature names
        
    Returns:
        SHAP values or None if explainer not available
    """
    try:
        explainer = shap_cache.get_or_create_explainer(
            model, X, model_type, feature_names
        )
        
        if explainer is None:
            return None
            
        # Calculate SHAP values
        if model_type == "xgboost":
            shap_values = explainer.shap_values(X)
        else:
            shap_values = explainer.shap_values(X)
            
        return shap_values
        
    except Exception as e:
        print(f" Error getting SHAP values: {e}")
        return None

# Background refresh functionality
def start_background_refresh(credit_model, refresh_interval: int = 3600):
    """Start background thread to refresh SHAP cache periodically"""
    def refresh_loop():
        while True:
            time.sleep(refresh_interval)
            try:
                print(" Refreshing SHAP cache...")
                cache_shap_explainers(credit_model)
            except Exception as e:
                print(f" Error in background refresh: {e}")
    
    refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
    refresh_thread.start()
    print(f" Background SHAP refresh started (interval: {refresh_interval}s)")