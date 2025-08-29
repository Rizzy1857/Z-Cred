"""
Unit and Integration Tests for Unified Trust Scoring System

Tests ensure that trust score calculations in trust_score_utils.py
match the values displayed in the UI across all components.
"""

import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trust_score_utils import get_unified_trust_scores
from model_pipeline import calculate_trust_score
from model_integration import ModelIntegrator


class TestUnifiedTrustScoring(unittest.TestCase):
    """Test unified trust scoring system consistency"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_applicant_data = {
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
        
        self.expected_score_range = (0.0, 1.0)
        self.expected_percentage_range = (0.0, 100.0)
    
    def test_unified_scores_structure(self):
        """Test that unified scores return expected structure"""
        scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Check that all required keys are present
        required_keys = [
            'behavioral_score',
            'social_score', 
            'digital_score',
            'overall_trust_score',
            'trust_percentage',
            'behavioral_percentage',
            'social_percentage',
            'digital_percentage'
        ]
        
        for key in required_keys:
            self.assertIn(key, scores, f"Missing required key: {key}")
    
    def test_score_value_ranges(self):
        """Test that all scores are within expected ranges"""
        scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Test score ranges (0.0 to 1.0)
        score_keys = ['behavioral_score', 'social_score', 'digital_score', 'overall_trust_score']
        for key in score_keys:
            score = scores[key]
            self.assertGreaterEqual(score, 0.0, f"{key} should be >= 0.0")
            self.assertLessEqual(score, 1.0, f"{key} should be <= 1.0")
        
        # Test percentage ranges (0.0 to 100.0)
        percentage_keys = ['trust_percentage', 'behavioral_percentage', 'social_percentage', 'digital_percentage']
        for key in percentage_keys:
            percentage = scores[key]
            self.assertGreaterEqual(percentage, 0.0, f"{key} should be >= 0.0")
            self.assertLessEqual(percentage, 100.0, f"{key} should be <= 100.0")
    
    def test_score_percentage_consistency(self):
        """Test that scores and percentages are mathematically consistent"""
        scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Check that percentages match scores * 100
        score_percentage_pairs = [
            ('behavioral_score', 'behavioral_percentage'),
            ('social_score', 'social_percentage'),
            ('digital_score', 'digital_percentage')
        ]
        
        for score_key, percentage_key in score_percentage_pairs:
            expected_percentage = scores[score_key] * 100
            actual_percentage = scores[percentage_key]
            self.assertAlmostEqual(
                expected_percentage, 
                actual_percentage, 
                places=2,
                msg=f"Inconsistency between {score_key} and {percentage_key}"
            )
    
    def test_overall_trust_score_calculation(self):
        """Test that overall trust score is properly calculated"""
        scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Overall score should be reasonable relative to component scores
        behavioral = scores['behavioral_score']
        social = scores['social_score']
        digital = scores['digital_score']
        overall = scores['overall_trust_score']
        
        # Overall should be within range of component scores
        min_component = min(behavioral, social, digital)
        max_component = max(behavioral, social, digital)
        
        self.assertGreaterEqual(overall, min_component * 0.5, "Overall score too low")
        self.assertLessEqual(overall, max_component * 1.5, "Overall score too high")
    
    def test_unified_scores_match_pipeline(self):
        """Test that unified scores match direct pipeline calculation"""
        # Get scores from unified system
        unified_scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Get scores directly from pipeline
        pipeline_scores = calculate_trust_score(self.test_applicant_data)
        
        # They should match (within floating point precision)
        score_keys = ['behavioral_score', 'social_score', 'digital_score', 'overall_trust_score']
        
        for key in score_keys:
            if key in pipeline_scores and key in unified_scores:
                self.assertAlmostEqual(
                    unified_scores[key],
                    pipeline_scores[key],
                    places=3,
                    msg=f"Unified and pipeline {key} don't match"
                )
    
    def test_trust_percentage_calculation(self):
        """Test that trust percentage is correctly calculated"""
        scores = get_unified_trust_scores(self.test_applicant_data)
        
        # Trust percentage should match overall score * 100
        expected_percentage = scores['overall_trust_score'] * 100
        actual_percentage = scores['trust_percentage']
        
        self.assertAlmostEqual(
            expected_percentage,
            actual_percentage,
            places=2,
            msg="Trust percentage calculation inconsistent"
        )
    
    def test_data_format_robustness(self):
        """Test that scoring handles various data formats correctly"""
        # Test with missing data
        incomplete_data = {
            'age': 25,
            'monthly_income': 30000
            # Missing other fields
        }
        
        scores = get_unified_trust_scores(incomplete_data)
        self.assertIsInstance(scores, dict, "Should handle incomplete data")
        
        # Test with string income (common from forms)
        string_data = self.test_applicant_data.copy()
        string_data['monthly_income'] = "50000"
        string_data['age'] = "30"
        
        scores = get_unified_trust_scores(string_data)
        self.assertIsInstance(scores, dict, "Should handle string inputs")
    
    def test_edge_case_values(self):
        """Test scoring with edge case values"""
        edge_cases = [
            # Very young applicant
            {'age': 18, 'monthly_income': 10000},
            # Very old applicant  
            {'age': 80, 'monthly_income': 100000},
            # Low income
            {'age': 30, 'monthly_income': 5000},
            # High income
            {'age': 30, 'monthly_income': 500000},
            # Zero debt ratio
            {'age': 30, 'monthly_income': 50000, 'debt_to_income': 0.0},
            # High debt ratio
            {'age': 30, 'monthly_income': 50000, 'debt_to_income': 0.8}
        ]
        
        for i, edge_data in enumerate(edge_cases):
            with self.subTest(case=i):
                scores = get_unified_trust_scores(edge_data)
                
                # All scores should still be valid
                self.assertGreaterEqual(scores['overall_trust_score'], 0.0)
                self.assertLessEqual(scores['overall_trust_score'], 1.0)
                self.assertGreaterEqual(scores['trust_percentage'], 0.0)
                self.assertLessEqual(scores['trust_percentage'], 100.0)


class TestIntegrationWithUI(unittest.TestCase):
    """Integration tests for UI display consistency"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.model_integrator = ModelIntegrator()
        
        self.sample_applicant = {
            'name': 'Test User',
            'age': 32,
            'monthly_income': 45000,
            'employment_length': 4,
            'debt_to_income': 0.2,
            'credit_utilization': 0.25,
            'payment_history_score': 88,
            'account_diversity': 2,
            'savings_rate': 0.18,
            'education_level': 'Bachelor',
            'location': 'Test City',
            'occupation': 'Test Job'
        }
    
    def test_model_integrator_consistency(self):
        """Test that model integrator produces consistent scores"""
        # Transform data through model integrator
        transformed_data = self.model_integrator.transform_applicant_data(self.sample_applicant)
        
        # Get unified scores
        unified_scores = get_unified_trust_scores(self.sample_applicant)
        
        # Both should produce valid scores
        self.assertIsInstance(transformed_data, dict)
        self.assertIsInstance(unified_scores, dict)
        
        # Check that trust percentages are reasonable
        trust_pct = unified_scores.get('trust_percentage', 0)
        self.assertGreater(trust_pct, 0, "Trust percentage should be positive")
        self.assertLess(trust_pct, 100, "Trust percentage should be less than 100")
    
    @patch('streamlit.session_state', {})
    def test_session_state_consistency(self):
        """Test that scores remain consistent across session state updates"""
        # This simulates how scores would be used in Streamlit
        
        # First calculation
        scores1 = get_unified_trust_scores(self.sample_applicant)
        
        # Simulate session state update
        import streamlit as st
        if hasattr(st, 'session_state'):
            st.session_state['user_data'] = self.sample_applicant.copy()
        
        # Second calculation with same data
        scores2 = get_unified_trust_scores(self.sample_applicant)
        
        # Should be identical
        self.assertEqual(scores1, scores2, "Scores should be consistent across calculations")
    
    def test_display_formatting(self):
        """Test that scores are properly formatted for display"""
        scores = get_unified_trust_scores(self.sample_applicant)
        
        # Test percentage formatting
        for key in ['trust_percentage', 'behavioral_percentage', 'social_percentage', 'digital_percentage']:
            percentage = scores[key]
            # Should be a number that can be formatted
            formatted = f"{percentage:.1f}%"
            self.assertIsInstance(formatted, str)
            self.assertIn('%', formatted)
        
        # Test score formatting
        for key in ['behavioral_score', 'social_score', 'digital_score', 'overall_trust_score']:
            score = scores[key]
            # Should be a number that can be formatted
            formatted = f"{score:.3f}"
            self.assertIsInstance(formatted, str)


class TestPerformance(unittest.TestCase):
    """Performance tests for scoring system"""
    
    def test_scoring_performance(self):
        """Test that scoring completes within reasonable time"""
        import time
        
        test_data = {
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
        
        start_time = time.time()
        scores = get_unified_trust_scores(test_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete within 1 second
        self.assertLess(execution_time, 1.0, "Trust score calculation too slow")
        self.assertIsInstance(scores, dict, "Should return valid results")
    
    def test_bulk_scoring_performance(self):
        """Test performance with multiple applicants"""
        import time
        
        # Create 100 test applicants
        test_applicants = []
        for i in range(100):
            applicant = {
                'age': 25 + (i % 30),
                'monthly_income': 30000 + (i * 500),
                'employment_length': 1 + (i % 10),
                'debt_to_income': 0.1 + (i % 50) * 0.01,
                'credit_utilization': 0.1 + (i % 40) * 0.01,
                'payment_history_score': 60 + (i % 40),
                'account_diversity': 1 + (i % 5),
                'savings_rate': 0.05 + (i % 20) * 0.01,
                'education_level': 'Bachelor'
            }
            test_applicants.append(applicant)
        
        start_time = time.time()
        
        results = []
        for applicant in test_applicants:
            scores = get_unified_trust_scores(applicant)
            results.append(scores)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should process 100 applicants within 10 seconds
        self.assertLess(execution_time, 10.0, "Bulk scoring too slow")
        self.assertEqual(len(results), 100, "Should process all applicants")
        
        # All results should be valid
        for scores in results:
            self.assertIn('overall_trust_score', scores)
            self.assertIn('trust_percentage', scores)


def run_unified_scoring_tests():
    """Run all unified scoring tests and return results"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestUnifiedTrustScoring,
        TestIntegrationWithUI,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return summary
    return {
        'tests_run': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful(),
        'details': {
            'failures': result.failures,
            'errors': result.errors
        }
    }


if __name__ == "__main__":
    print("🧪 Running Unified Trust Scoring Tests...")
    print("=" * 60)
    
    results = run_unified_scoring_tests()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Tests Run: {results['tests_run']}")
    print(f"❌ Failures: {results['failures']}")
    print(f"⚠️  Errors: {results['errors']}")
    print(f"🎯 Overall Success: {'✅ PASSED' if results['success'] else '❌ FAILED'}")
    
    if not results['success']:
        print("\n🔍 Issues Found:")
        for failure in results['details']['failures']:
            print(f"❌ {failure[0]}: {failure[1]}")
        for error in results['details']['errors']:
            print(f"⚠️  {error[0]}: {error[1]}")
    
    print("=" * 60)
