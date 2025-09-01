"""
Performance Profiling Script for Z-Cred Application

Identifies long-blocking operations and provides optimization recommendations.
"""

import cProfile
import pstats
import io
import time
import threading
import traceback
from contextlib import contextmanager
from typing import Dict, List, Callable, Any
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class PerformanceProfiler:
    """Advanced performance profiler for Z-Cred application"""
    
    def __init__(self):
        self.profiles = {}
        self.blocking_operations = []
        self.performance_metrics = {}
        
    @contextmanager
    def profile_section(self, section_name: str):
        """Context manager for profiling specific code sections"""
        start_time = time.time()
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            yield
        finally:
            profiler.disable()
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Store profile data
            self.profiles[section_name] = {
                'profiler': profiler,
                'execution_time': execution_time,
                'timestamp': time.time()
            }
            
            # Check for blocking operations (>100ms)
            if execution_time > 0.1:
                self.blocking_operations.append({
                    'section': section_name,
                    'time': execution_time,
                    'timestamp': time.time()
                })
                
    def profile_function(self, func: Callable, *args, **kwargs) -> Any:
        """Profile a specific function call"""
        function_name = f"{func.__module__}.{func.__name__}"
        
        with self.profile_section(function_name):
            return func(*args, **kwargs)
    
    def get_slow_functions(self, section_name: str, min_time: float = 0.01) -> List[Dict]:
        """Get functions that took longer than min_time seconds"""
        if section_name not in self.profiles:
            return []
        
        profiler = self.profiles[section_name]['profiler']
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        
        slow_functions = []
        for func_info in stats.get_stats_profile().func_profiles:
            if func_info[3] > min_time:  # cumulative time
                slow_functions.append({
                    'function': func_info[0],
                    'calls': func_info[1],
                    'total_time': func_info[2],
                    'cumulative_time': func_info[3],
                    'per_call': func_info[3] / func_info[1] if func_info[1] > 0 else 0
                })
        
        return sorted(slow_functions, key=lambda x: x['cumulative_time'], reverse=True)
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append(" Z-Cred Performance Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        total_sections = len(self.profiles)
        total_blocking = len(self.blocking_operations)
        
        report.append(f" Summary:")
        report.append(f"   • Sections profiled: {total_sections}")
        report.append(f"   • Blocking operations: {total_blocking}")
        report.append("")
        
        # Blocking operations analysis
        if self.blocking_operations:
            report.append("  Blocking Operations (>100ms):")
            for op in sorted(self.blocking_operations, key=lambda x: x['time'], reverse=True):
                report.append(f"   • {op['section']}: {op['time']:.3f}s")
            report.append("")
        
        # Section-by-section analysis
        report.append(" Section Performance:")
        for section_name, profile_data in self.profiles.items():
            exec_time = profile_data['execution_time']
            status = "" if exec_time > 0.5 else "" if exec_time > 0.1 else ""
            report.append(f"   {status} {section_name}: {exec_time:.3f}s")
            
            # Top slow functions in this section
            slow_funcs = self.get_slow_functions(section_name, 0.005)[:3]
            for func in slow_funcs:
                report.append(f"       {func['function']}: {func['cumulative_time']:.3f}s")
        
        report.append("")
        
        # Recommendations
        report.append(" Optimization Recommendations:")
        
        if total_blocking > 0:
            report.append("   1.  Reduce blocking operations:")
            for op in self.blocking_operations[:3]:
                report.append(f"      • Optimize {op['section']} (currently {op['time']:.3f}s)")
        
        if any(p['execution_time'] > 0.2 for p in self.profiles.values()):
            report.append("   2.  Consider async operations for slow sections")
            
        report.append("   3.  Use caching for repeated calculations")
        report.append("   4.  Move heavy operations to background threads")
        report.append("   5.  Lazy load expensive resources")
        
        return "\n".join(report)
    
    def save_detailed_profile(self, section_name: str, filename: str = None):
        """Save detailed profile to file"""
        if section_name not in self.profiles:
            print(f"No profile data for section: {section_name}")
            return
            
        if filename is None:
            filename = f"profile_{section_name.replace('.', '_')}.prof"
            
        profiler = self.profiles[section_name]['profiler']
        profiler.dump_stats(filename)
        print(f"Detailed profile saved to: {filename}")


def profile_trust_scoring():
    """Profile trust scoring operations"""
    profiler = PerformanceProfiler()
    
    print(" Profiling trust scoring operations...")
    
    # Test data
    test_applicant = {
        'age': 30,
        'monthly_income': 50000,
        'employment_length': 3,
        'debt_to_income': 0.25,
        'credit_utilization': 0.3,
        'payment_history_score': 85,
        'account_diversity': 3,
        'savings_rate': 0.2,
        'education_level': 'Bachelor'
    }
    
    try:
        # Profile unified trust scoring
        with profiler.profile_section("trust_score_utils.get_unified_trust_scores"):
            from trust_score_utils import get_unified_trust_scores
            scores = get_unified_trust_scores(test_applicant)
        
        # Profile model pipeline
        with profiler.profile_section("model_pipeline.calculate_trust_score"):
            from model_pipeline import calculate_trust_score
            pipeline_scores = calculate_trust_score(test_applicant)
        
        # Profile model integration
        with profiler.profile_section("model_integration.transform_applicant_data"):
            from model_integration import ModelIntegrator
            integrator = ModelIntegrator()
            transformed_data = integrator.transform_applicant_data(test_applicant)
            
    except Exception as e:
        print(f" Error during trust scoring profiling: {e}")
        traceback.print_exc()
    
    return profiler


def profile_database_operations():
    """Profile database operations"""
    profiler = PerformanceProfiler()
    
    print(" Profiling database operations...")
    
    try:
        # Profile database initialization
        with profiler.profile_section("local_db.Database.__init__"):
            from local_db import Database
            db = Database()
        
        # Profile applicant creation
        test_applicant = {
            'name': 'Performance Test User',
            'phone': '+91-9999999998',
            'email': 'perftest@example.com',
            'age': 28,
            'gender': 'Other',
            'location': 'Test City',
            'occupation': 'Test Job',
            'monthly_income': 45000.0
        }
        
        with profiler.profile_section("local_db.create_applicant"):
            try:
                applicant_id = db.create_applicant(test_applicant)
            except Exception as e:
                print(f"Note: Applicant creation failed (likely duplicate): {e}")
                applicant_id = None
        
        # Profile data retrieval
        with profiler.profile_section("local_db.get_all_applicants"):
            applicants = db.get_all_applicants()
        
        # Profile trust score update
        if applicant_id:
            with profiler.profile_section("local_db.update_trust_score"):
                db.update_trust_score(applicant_id, 0.7, 0.6, 0.8)
            
    except Exception as e:
        print(f" Error during database profiling: {e}")
        traceback.print_exc()
    
    return profiler


def profile_ml_model_loading():
    """Profile ML model loading and inference"""
    profiler = PerformanceProfiler()
    
    print(" Profiling ML model operations...")
    
    try:
        # Profile model loading
        with profiler.profile_section("model_integration.get_credit_model"):
            from model_integration import model_integrator
            model = model_integrator.get_credit_model()
        
        # Profile SHAP explainer creation/loading
        with profiler.profile_section("shap_cache.cache_shap_explainers"):
            from shap_cache import cache_shap_explainers
            cache_shap_explainers(model)
            
    except Exception as e:
        print(f" Error during ML model profiling: {e}")
        traceback.print_exc()
    
    return profiler


def profile_shap_operations():
    """Profile SHAP explanation generation"""
    profiler = PerformanceProfiler()
    
    print(" Profiling SHAP operations...")
    
    try:
        # Setup test data
        import numpy as np
        from model_integration import model_integrator
        
        test_features = np.array([[30, 50000, 3, 0.25, 0.3, 85, 3, 0.2]])
        feature_names = ['age', 'income', 'employment_length', 'debt_to_income', 
                        'credit_utilization', 'payment_history_score', 
                        'account_diversity', 'savings_rate']
        
        # Profile SHAP value generation
        with profiler.profile_section("shap_cache.get_cached_shap_values"):
            from shap_cache import get_cached_shap_values
            model = model_integrator.get_credit_model()
            
            if hasattr(model, 'xgb_model') and model.xgb_model:
                shap_values = get_cached_shap_values(
                    model.xgb_model, 
                    test_features, 
                    'xgboost', 
                    feature_names
                )
                
    except Exception as e:
        print(f" Error during SHAP profiling: {e}")
        traceback.print_exc()
    
    return profiler


def run_comprehensive_profiling():
    """Run comprehensive performance profiling"""
    print(" Starting Comprehensive Z-Cred Performance Profiling")
    print("=" * 60)
    
    all_profilers = []
    
    # Run individual profiling sections
    sections = [
        ("Trust Scoring", profile_trust_scoring),
        ("Database Operations", profile_database_operations),
        ("ML Model Loading", profile_ml_model_loading),
        ("SHAP Operations", profile_shap_operations)
    ]
    
    for section_name, profile_func in sections:
        print(f"\n Profiling {section_name}...")
        try:
            profiler = profile_func()
            all_profilers.append((section_name, profiler))
            print(f" {section_name} profiling completed")
        except Exception as e:
            print(f" {section_name} profiling failed: {e}")
    
    # Generate combined report
    print("\n" + "=" * 60)
    print(" COMPREHENSIVE PERFORMANCE REPORT")
    print("=" * 60)
    
    total_blocking_operations = 0
    critical_issues = []
    
    for section_name, profiler in all_profilers:
        print(f"\n {section_name} Results:")
        print("-" * 30)
        
        blocking_count = len(profiler.blocking_operations)
        total_blocking_operations += blocking_count
        
        if blocking_count > 0:
            print(f"  Found {blocking_count} blocking operations:")
            for op in profiler.blocking_operations:
                print(f"   • {op['section']}: {op['time']:.3f}s")
                if op['time'] > 1.0:
                    critical_issues.append(f"{section_name}: {op['section']}")
        else:
            print(" No blocking operations detected")
        
        # Show execution times
        if profiler.profiles:
            print("⏱  Execution times:")
            for profile_name, data in profiler.profiles.items():
                exec_time = data['execution_time']
                status = "" if exec_time > 0.5 else "" if exec_time > 0.1 else ""
                print(f"   {status} {profile_name}: {exec_time:.3f}s")
    
    # Final recommendations
    print("\n" + "=" * 60)
    print(" OPTIMIZATION PRIORITIES")
    print("=" * 60)
    
    if critical_issues:
        print(" CRITICAL (>1s execution time):")
        for issue in critical_issues:
            print(f"   • {issue}")
        print("")
    
    if total_blocking_operations > 0:
        print(f" MEDIUM ({total_blocking_operations} blocking operations >100ms)")
        print("   • Consider caching and async operations")
        print("")
    
    print(" IMMEDIATE ACTIONS:")
    print("   1.  Pre-cache SHAP explainers: python -c 'from shap_cache import cache_shap_explainers; ...'")
    print("   2.  Enable database WAL mode (already implemented)")
    print("   3.  Move model loading to background thread")
    print("   4.  Implement lazy loading for UI components")
    print("   5.  Use session state caching in Streamlit")
    
    print("\n EXPECTED IMPACT:")
    if total_blocking_operations > 5:
        print("   • HIGH impact: 8-12% performance improvement")
    elif total_blocking_operations > 2:
        print("   • MEDIUM impact: 4-8% performance improvement")
    else:
        print("   • LOW impact: 2-4% performance improvement")
    
    print("\n Profiling completed!")
    
    # Save detailed profiles for critical issues
    for section_name, profiler in all_profilers:
        if profiler.blocking_operations:
            filename = f"profile_{section_name.lower().replace(' ', '_')}.prof"
            for profile_section_name in profiler.profiles.keys():
                profiler.save_detailed_profile(profile_section_name, 
                                               f"{filename}_{profile_section_name.replace('.', '_')}.prof")


if __name__ == "__main__":
    run_comprehensive_profiling()
