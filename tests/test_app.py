import unittest
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import parse_date, normalize_to_common_schema, apply_rules, calculate_match_score, find_matches, calculate_category_totals, is_card_payment


class TestDateParsing(unittest.TestCase):
    def test_parse_date_standard_format(self):
        result = parse_date('2024-01-15')
        self.assertEqual(result, pd.Timestamp('2024-01-15'))
    
    def test_parse_date_slash_format(self):
        result = parse_date('01/15/2024')
        self.assertEqual(result, pd.Timestamp('2024-01-15'))
    
    def test_parse_date_invalid(self):
        result = parse_date('invalid-date')
        self.assertIsNone(result)
    
    def test_parse_date_empty(self):
        result = parse_date('')
        self.assertIsNone(result)


class TestNormalization(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-18'],
            'Description': ['Starbucks', 'Amazon'],
            'Amount': [-4.50, -89.00],
            'Account': ['Checking', 'Checking']
        })
        self.mapping = {
            'date': 'Date',
            'amount': 'Amount',
            'vendor': 'Description',
            'category': '',
            'account': 'Account',
            'memo': '',
            'description': '',
            'notes': ''
        }
    
    def test_normalize_creates_common_schema(self):
        result = normalize_to_common_schema(self.sample_df, self.mapping, 'test_source')
        self.assertIn('date', result.columns)
        self.assertIn('amount', result.columns)
        self.assertIn('vendor_raw', result.columns)
        self.assertIn('source', result.columns)
        self.assertEqual(len(result), 2)
    
    def test_normalize_amount_absolute(self):
        result = normalize_to_common_schema(self.sample_df, self.mapping, 'test_source')
        self.assertEqual(result['amount'].iloc[0], 4.50)
        self.assertEqual(result['amount'].iloc[1], 89.00)
    
    def test_normalize_source_name(self):
        result = normalize_to_common_schema(self.sample_df, self.mapping, 'test_source')
        self.assertEqual(result['source'].iloc[0], 'test_source')
    
    def test_negative_amount_defaults_to_expense(self):
        result = normalize_to_common_schema(self.sample_df, self.mapping, 'test_source')
        self.assertEqual(result['transaction_type'].iloc[0], 'expense')
        self.assertEqual(result['transaction_type'].iloc[1], 'expense')
    
    def test_debit_credit_mapping_transaction_types(self):
        df_debit_credit = pd.DataFrame({
            'Date': ['2024-01-15', '2024-01-18'],
            'Description': ['Expense', 'Income'],
            'Debit': [100.0, 0.0],
            'Credit': [0.0, 200.0],
            'Account': ['Checking', 'Checking']
        })
        mapping_dc = {
            'date': 'Date',
            'amount': '',
            'vendor': 'Description',
            'category': '',
            'account': 'Account',
            'memo': '',
            'description': '',
            'notes': '',
            'debit': 'Debit',
            'credit': 'Credit'
        }
        result = normalize_to_common_schema(df_debit_credit, mapping_dc, 'test_source')
        self.assertEqual(result['transaction_type'].iloc[0], 'expense')
        self.assertEqual(result['transaction_type'].iloc[1], 'income')


class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.sample_df = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-15')] * 3,
            'amount': [100.0, 200.0, 300.0],
            'vendor_raw': ['PAX8 INC', 'Amazon', 'Fred Astaire Dance'],
            'account': ['Checking', 'Checking', 'Checking'],
            'source': ['test'] * 3,
            'category_raw': ['', 'software', 'marketing'],
            'memo': ['autopay', 'aws subscription', 'dance class'],
            'transaction_type': ['expense'] * 3
        })
        
        self.rules = [
            {'rule_type': 'vendor_contains', 'pattern': 'pax8', 'category': 'software_saas'},
            {'rule_type': 'vendor_contains', 'pattern': 'fred astaire', 'category': 'advertising_marketing'},
            {'rule_type': 'description_contains', 'pattern': 'autopay', 'transaction_type': 'transfer_exclude'}
        ]
    
    def test_vendor_contains_rule(self):
        result = apply_rules(self.sample_df, self.rules)
        self.assertEqual(result['category_mapped'].iloc[0], 'software_saas')
        self.assertEqual(result['category_mapped'].iloc[2], 'advertising_marketing')
    
    def test_description_contains_rule(self):
        result = apply_rules(self.sample_df, self.rules)
        self.assertEqual(result['transaction_type'].iloc[0], 'transfer_exclude')
    
    def test_rules_create_category_mapped_column(self):
        result = apply_rules(self.sample_df, self.rules)
        self.assertIn('category_mapped', result.columns)


class TestMatching(unittest.TestCase):
    def setUp(self):
        self.tx1 = pd.Series({
            'date': pd.Timestamp('2024-01-15'),
            'amount': 100.0,
            'vendor_raw': 'Starbucks Coffee',
            'account': 'Checking',
            'source': 'bank',
            'category_raw': 'food',
            'memo': 'coffee',
            'transaction_type': 'expense'
        })
        
        self.tx2_same = pd.Series({
            'date': pd.Timestamp('2024-01-15'),
            'amount': 100.0,
            'vendor_raw': 'Starbucks Coffee',
            'account': 'Credit Card',
            'source': 'card',
            'category_raw': 'food',
            'memo': 'coffee',
            'transaction_type': 'expense'
        })
        
        self.tx3_different = pd.Series({
            'date': pd.Timestamp('2024-01-20'),
            'amount': 200.0,
            'vendor_raw': 'Amazon',
            'account': 'Checking',
            'source': 'bank',
            'category_raw': 'software',
            'memo': 'aws',
            'transaction_type': 'expense'
        })
    
    def test_exact_match_score(self):
        score, reason = calculate_match_score(self.tx1, self.tx2_same)
        self.assertGreaterEqual(score, 80)
        self.assertIn('Exact amount', reason)
    
    def test_different_amount_low_score(self):
        score, reason = calculate_match_score(self.tx1, self.tx3_different)
        self.assertLess(score, 50)
    
    def test_same_day_bonus(self):
        score, reason = calculate_match_score(self.tx1, self.tx2_same)
        self.assertIn('Same date', reason)
    
    def test_find_matches_integration(self):
        df = pd.DataFrame([self.tx1, self.tx2_same, self.tx3_different])
        matches = find_matches(df, min_score=60)
        self.assertGreater(len(matches), 0)
    
    def test_match_score_includes_vendor_account_no_early_return(self):
        tx_close_date_diff_vendor = pd.Series({
            'date': pd.Timestamp('2024-01-16'),
            'amount': 100.0,
            'vendor_raw': 'Different Vendor',
            'account': 'Checking',
            'source': 'bank',
            'category_raw': 'food',
            'memo': 'coffee',
            'transaction_type': 'expense'
        })
        score, reason = calculate_match_score(self.tx1, tx_close_date_diff_vendor)
        self.assertIn('Exact amount', reason)
        self.assertGreater(score, 50)
        self.assertNotEqual(score, 70)
    
    def test_match_score_considers_account_same(self):
        tx_same_amount_date_vendor = pd.Series({
            'date': pd.Timestamp('2024-01-15'),
            'amount': 100.0,
            'vendor_raw': 'Starbucks Coffee',
            'account': 'Checking',
            'source': 'bank2',
            'category_raw': 'food',
            'memo': 'coffee',
            'transaction_type': 'expense'
        })
        score, reason = calculate_match_score(self.tx1, tx_same_amount_date_vendor)
        self.assertIn('Same account', reason)
    
    def test_card_payment_detection_keywords(self):
        tx_autopay = pd.Series({
            'date': pd.Timestamp('2024-01-15'),
            'amount': 100.0,
            'vendor_raw': 'Credit Card Payment',
            'account': 'Checking',
            'source': 'bank',
            'category_raw': 'payment',
            'memo': 'autopay',
            'transaction_type': 'expense'
        })
        self.assertTrue(is_card_payment(tx_autopay))
    
    def test_card_payment_detection_no_keywords(self):
        tx_normal_purchase = pd.Series({
            'date': pd.Timestamp('2024-01-15'),
            'amount': 100.0,
            'vendor_raw': 'Starbucks Coffee',
            'account': 'Credit Card',
            'source': 'card',
            'category_raw': 'food',
            'memo': 'coffee',
            'transaction_type': 'expense'
        })
        self.assertFalse(is_card_payment(tx_normal_purchase))


class TestCategoryTotals(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-15')] * 4,
            'amount': [100.0, 200.0, 150.0, 300.0],
            'vendor_raw': ['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D'],
            'account': ['Checking'] * 4,
            'source': ['bank', 'card', 'bank', 'card'],
            'category_raw': ['software', 'software', 'office', 'office'],
            'memo': [''] * 4,
            'transaction_type': ['expense'] * 4,
            'category_mapped': ['software', 'software', 'office', 'office']
        })
    
    def test_calculate_category_totals(self):
        totals = calculate_category_totals(self.df)
        self.assertIn('software', totals)
        self.assertIn('office', totals)
    
    def test_category_totals_by_source(self):
        totals = calculate_category_totals(self.df)
        self.assertIn('sources', totals['software'])
        self.assertIn('low', totals['software'])
        self.assertIn('high', totals['software'])
        self.assertIn('midpoint', totals['software'])
    
    def test_category_totals_values(self):
        totals = calculate_category_totals(self.df)
        self.assertEqual(totals['software']['low'], 100.0)
        self.assertEqual(totals['software']['high'], 200.0)
        self.assertEqual(totals['software']['midpoint'], 150.0)


if __name__ == '__main__':
    unittest.main()
