import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from rapidfuzz import fuzz, process
import json
import io
from typing import Dict, List, Tuple, Optional

st.set_page_config(
    page_title="CSV Reconciliation MVP",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CSV Reconciliation MVP")
st.markdown("*A local-only tool for reconciling small-business expense CSVs*")

COMMON_SCHEMA = [
    'date', 'amount', 'vendor_raw', 'vendor_normalized',
    'account', 'source', 'category_raw', 'memo', 'transaction_type'
]

DEFAULT_RULES = [
    {"rule_type": "vendor_contains", "pattern": "pax8", "category": "software_saas"},
    {"rule_type": "vendor_contains", "pattern": "dell", "category": "client_supplies"},
    {"rule_type": "description_contains", "pattern": "autopay", "transaction_type": "transfer_exclude"},
    {"rule_type": "vendor_contains", "pattern": "fred astaire", "category": "advertising_marketing"},
]

def init_session_state():
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = {}
    if 'column_mappings' not in st.session_state:
        st.session_state.column_mappings = {}
    if 'normalized_data' not in st.session_state:
        st.session_state.normalized_data = None
    if 'rules' not in st.session_state:
        st.session_state.rules = DEFAULT_RULES.copy()
    if 'matches' not in st.session_state:
        st.session_state.matches = []
    if 'category_totals' not in st.session_state:
        st.session_state.category_totals = {}

def parse_date(date_str):
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        return pd.to_datetime(date_str)
    except:
        return None

def normalize_to_common_schema(df: pd.DataFrame, mapping: Dict, source_name: str) -> pd.DataFrame:
    normalized = pd.DataFrame(columns=COMMON_SCHEMA)
    
    for idx, row in df.iterrows():
        normalized_row = {}
        
        date_col = mapping.get('date', '')
        normalized_row['date'] = parse_date(row.get(date_col))
        
        amount_col = mapping.get('amount', '')
        raw_amount = row.get(amount_col, 0)
        debit_col = mapping.get('debit', '')
        credit_col = mapping.get('credit', '')
        
        transaction_type = 'expense'
        amount = 0
        
        if debit_col and credit_col:
            debit = row.get(debit_col, 0)
            credit = row.get(credit_col, 0)
            if pd.notna(debit) and debit != 0:
                amount = float(debit)
                transaction_type = 'expense'
            elif pd.notna(credit) and credit != 0:
                amount = float(credit)
                transaction_type = 'income'
            else:
                amount = 0
        else:
            amount = float(raw_amount) if pd.notna(raw_amount) else 0
            transaction_type = 'expense'
        
        normalized_row['amount'] = abs(amount)
        normalized_row['transaction_type'] = transaction_type
        
        vendor_col = mapping.get('vendor', '')
        vendor_raw = str(row.get(vendor_col, '')).strip()
        normalized_row['vendor_raw'] = vendor_raw
        normalized_row['vendor_normalized'] = vendor_raw.lower().replace(' ', '_').replace(',', '').replace('.', '')
        
        account_col = mapping.get('account', '')
        normalized_row['account'] = str(row.get(account_col, '')).strip()
        
        normalized_row['source'] = source_name
        
        category_col = mapping.get('category', '')
        normalized_row['category_raw'] = str(row.get(category_col, '')).strip()
        
        memo_col = mapping.get('memo', '')
        desc_col = mapping.get('description', '')
        notes_col = mapping.get('notes', '')
        
        memo = ''
        if memo_col and pd.notna(row.get(memo_col)):
            memo = str(row.get(memo_col, ''))
        elif desc_col and pd.notna(row.get(desc_col)):
            memo = str(row.get(desc_col, ''))
        elif notes_col and pd.notna(row.get(notes_col)):
            memo = str(row.get(notes_col, ''))
        normalized_row['memo'] = memo
        
        normalized = pd.concat([normalized, pd.DataFrame([normalized_row])], ignore_index=True)
    
    return normalized

def apply_rules(df: pd.DataFrame, rules: List[Dict]) -> pd.DataFrame:
    df = df.copy()
    
    for rule in rules:
        if rule['rule_type'] == 'vendor_contains':
            pattern = rule['pattern'].lower()
            mask = df['vendor_raw'].str.lower().str.contains(pattern, na=False)
            df.loc[mask, 'category_raw'] = rule.get('category', df.loc[mask, 'category_raw'])
            df.loc[mask, 'category_mapped'] = rule.get('category', df.loc[mask, 'category_raw'])
        
        elif rule['rule_type'] == 'description_contains':
            pattern = rule['pattern'].lower()
            mask = df['memo'].str.lower().str.contains(pattern, na=False)
            df.loc[mask, 'transaction_type'] = rule.get('transaction_type', df.loc[mask, 'transaction_type'])
    
    if 'category_mapped' not in df.columns:
        df['category_mapped'] = df['category_raw']
    
    return df

def calculate_match_score(tx1: pd.Series, tx2: pd.Series) -> Tuple[float, str]:
    score = 0
    reasons = []
    
    amount_match = abs(tx1['amount'] - tx2['amount']) < 0.01
    if amount_match:
        score += 50
        reasons.append('Exact amount')
    
    if tx1['date'] and tx2['date']:
        date_diff = abs((tx1['date'] - tx2['date']).days)
        if date_diff == 0:
            score += 30
            reasons.append('Same date')
        elif date_diff <= 2:
            score += 20
            reasons.append(f'Close date ({date_diff} days)')
    
    vendor1 = tx1['vendor_raw'].lower()
    vendor2 = tx2['vendor_raw'].lower()
    vendor_score = fuzz.ratio(vendor1, vendor2)
    
    if vendor_score >= 90:
        score += 15
        reasons.append('Similar vendor')
    elif vendor_score >= 75:
        score += 10
        reasons.append('Vendor match')
    
    if tx1['account'] and tx2['account'] and tx1['account'] == tx2['account']:
        score += 10
        reasons.append('Same account')
    
    return score, ', '.join(reasons)

def is_card_payment(tx: pd.Series) -> bool:
    payment_keywords = ['autopay', 'payment', 'thank you', 'ach pmnt', 'credit card payment', 'auto payment']
    text_to_check = f"{tx.get('vendor_raw', '')} {tx.get('memo', '')}".lower()
    return any(keyword in text_to_check for keyword in payment_keywords)

def find_matches(df: pd.DataFrame, min_score: int = 60) -> List[Dict]:
    matches = []
    processed_pairs = set()
    
    sources = df['source'].unique()
    
    for i, source_a in enumerate(sources):
        for source_b in sources[i+1:]:
            df_a = df[df['source'] == source_a]
            df_b = df[df['source'] == source_b]
            
            for idx_a, tx_a in df_a.iterrows():
                for idx_b, tx_b in df_b.iterrows():
                    pair_id = tuple(sorted([idx_a, idx_b]))
                    if pair_id in processed_pairs:
                        continue
                    processed_pairs.add(pair_id)
                    
                    score, reason = calculate_match_score(tx_a, tx_b)
                    
                    if score >= min_score:
                        match_type = 'unknown'
                        if score >= 80:
                            match_type = 'likely_duplicate'
                        elif tx_a['transaction_type'] == 'transfer_exclude' or tx_b['transaction_type'] == 'transfer_exclude':
                            match_type = 'transfer'
                        elif is_card_payment(tx_a) or is_card_payment(tx_b):
                            match_type = 'card_payment'
                        else:
                            match_type = 'probable_match'
                        
                        matches.append({
                            'match_type': match_type,
                            'score': score,
                            'reason': reason,
                            'tx_a_idx': idx_a,
                            'tx_b_idx': idx_b,
                            'tx_a_source': tx_a['source'],
                            'tx_b_source': tx_b['source'],
                            'tx_a_vendor': tx_a['vendor_raw'],
                            'tx_b_vendor': tx_b['vendor_raw'],
                            'tx_a_amount': tx_a['amount'],
                            'tx_b_amount': tx_b['amount'],
                            'tx_a_date': tx_a['date'],
                            'tx_b_date': tx_b['date'],
                        })
    
    return sorted(matches, key=lambda x: x['score'], reverse=True)

def calculate_category_totals(df: pd.DataFrame) -> Dict:
    if df is None or df.empty:
        return {}
    
    df['category_final'] = df.get('category_mapped', df['category_raw'])
    df['category_final'] = df['category_final'].replace('', 'uncategorized')
    
    totals = df.groupby(['source', 'category_final'])['amount'].sum().reset_index()
    pivot = totals.pivot(index='category_final', columns='source', values='amount').fillna(0)
    
    result = {}
    for category in pivot.index:
        sources = pivot.loc[category].to_dict()
        values = [v for v in sources.values() if v > 0]
        
        result[category] = {
            'sources': sources,
            'low': min(values) if values else 0,
            'high': max(values) if values else 0,
            'midpoint': sum(values) / len(values) if values else 0,
            'manual_override': sum(values) / len(values) if values else 0,
        }
    
    return result

init_session_state()

tabs = st.tabs([
    "📤 Upload Sources",
    "🗂️ Map Columns",
    "✨ Normalize",
    "⚙️ Rules",
    "🔗 Matches",
    "📋 Review",
    "💰 Category Reconciliation",
    "📥 Export"
])

with tabs[0]:
    st.header("Upload CSV Files")
    st.markdown("Upload 2-4 CSV files from different financial sources (bank, credit card, accounting software, etc.)")
    
    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type=['csv'],
        accept_multiple_files=True,
        key="csv_uploader"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.uploaded_files:
                df = pd.read_csv(file)
                st.session_state.uploaded_files[file.name] = {
                    'data': df,
                    'filename': file.name
                }
        
        if st.session_state.uploaded_files:
            st.success(f"Loaded {len(st.session_state.uploaded_files)} file(s)")
            
            for name, file_info in st.session_state.uploaded_files.items():
                st.subheader(f"📄 {name}")
                st.dataframe(file_info['data'].head())

with tabs[1]:
    st.header("Map Columns")
    st.markdown("Map columns from each source to the common schema")
    
    if not st.session_state.uploaded_files:
        st.warning("Please upload CSV files first")
    else:
        for source_name, file_info in st.session_state.uploaded_files.items():
            st.subheader(f"📄 {source_name}")
            df = file_info['data']
            columns = list(df.columns)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_col = st.selectbox(
                    f"{source_name} - Date Column",
                    options=[''] + columns,
                    key=f"{source_name}_date"
                )
                amount_col = st.selectbox(
                    f"{source_name} - Amount Column",
                    options=[''] + columns,
                    key=f"{source_name}_amount"
                )
            
            with col2:
                vendor_col = st.selectbox(
                    f"{source_name} - Vendor Column",
                    options=[''] + columns,
                    key=f"{source_name}_vendor"
                )
                category_col = st.selectbox(
                    f"{source_name} - Category Column",
                    options=[''] + columns,
                    key=f"{source_name}_category"
                )
            
            with col3:
                account_col = st.selectbox(
                    f"{source_name} - Account Column",
                    options=[''] + columns,
                    key=f"{source_name}_account"
                )
                memo_col = st.selectbox(
                    f"{source_name} - Memo/Description Column",
                    options=[''] + columns,
                    key=f"{source_name}_memo"
                )
            
            st.session_state.column_mappings[source_name] = {
                'date': date_col,
                'amount': amount_col,
                'vendor': vendor_col,
                'category': category_col,
                'account': account_col,
                'memo': memo_col,
                'description': memo_col,
                'notes': memo_col,
            }
            
            with st.expander("Show debit/credit columns (if applicable)"):
                col4, col5 = st.columns(2)
                with col4:
                    debit_col = st.selectbox(
                        f"{source_name} - Debit Column",
                        options=[''] + columns,
                        key=f"{source_name}_debit"
                    )
                with col5:
                    credit_col = st.selectbox(
                        f"{source_name} - Credit Column",
                        options=[''] + columns,
                        key=f"{source_name}_credit"
                    )
                
                if debit_col and credit_col:
                    st.session_state.column_mappings[source_name]['debit'] = debit_col
                    st.session_state.column_mappings[source_name]['credit'] = credit_col
        
        if st.button("Save Column Mappings"):
            st.success("Column mappings saved!")

with tabs[2]:
    st.header("Normalize Transactions")
    st.markdown("Preview transactions normalized to the common schema")
    
    if not st.session_state.column_mappings:
        st.warning("Please map columns first")
    else:
        if st.button("Normalize Data"):
            all_normalized = []
            
            for source_name, file_info in st.session_state.uploaded_files.items():
                mapping = st.session_state.column_mappings.get(source_name, {})
                if mapping and any(mapping.values()):
                    df_normalized = normalize_to_common_schema(file_info['data'], mapping, source_name)
                    all_normalized.append(df_normalized)
            
            if all_normalized:
                st.session_state.normalized_data = pd.concat(all_normalized, ignore_index=True)
                st.session_state.normalized_data = apply_rules(
                    st.session_state.normalized_data,
                    st.session_state.rules
                )
                st.success(f"Normalized {len(st.session_state.normalized_data)} transactions")
            else:
                st.warning("No valid mappings found")
        
        if st.session_state.normalized_data is not None:
            st.subheader("Normalized Data Preview")
            display_df = st.session_state.normalized_data.copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_df.head(20), use_container_width=True)
            
            st.download_button(
                "Download Normalized Data",
                data=display_df.to_csv(index=False).encode('utf-8'),
                file_name='normalized_transactions.csv',
                mime='text/csv'
            )

with tabs[3]:
    st.header("Rules Configuration")
    st.markdown("Define rules for vendor normalization and category mapping")
    
    st.subheader("Current Rules")
    for i, rule in enumerate(st.session_state.rules):
        with st.expander(f"Rule {i+1}: {rule['rule_type']} = '{rule.get('pattern', '')}'"):
            col1, col2 = st.columns(2)
            with col1:
                rule_type = st.selectbox(
                    "Rule Type",
                    options=['vendor_contains', 'description_contains'],
                    index=['vendor_contains', 'description_contains'].index(rule['rule_type']),
                    key=f"rule_type_{i}"
                )
                pattern = st.text_input(
                    "Pattern",
                    value=rule.get('pattern', ''),
                    key=f"pattern_{i}"
                )
            with col2:
                if rule_type == 'vendor_contains':
                    category = st.text_input(
                        "Category",
                        value=rule.get('category', ''),
                        key=f"category_{i}"
                    )
                else:
                    transaction_type = st.selectbox(
                        "Transaction Type",
                        options=['expense', 'income', 'transfer_exclude'],
                        index=['expense', 'income', 'transfer_exclude'].index(rule.get('transaction_type', 'expense')),
                        key=f"tx_type_{i}"
                    )
            
            if st.button(f"Update Rule {i+1}", key=f"update_{i}"):
                st.session_state.rules[i]['rule_type'] = rule_type
                st.session_state.rules[i]['pattern'] = pattern
                if rule_type == 'vendor_contains':
                    st.session_state.rules[i]['category'] = category
                else:
                    st.session_state.rules[i]['transaction_type'] = transaction_type
                st.success("Rule updated!")
            
            if st.button(f"Delete Rule {i+1}", key=f"delete_{i}"):
                st.session_state.rules.pop(i)
                st.rerun()
    
    st.subheader("Add New Rule")
    with st.form("add_rule_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_rule_type = st.selectbox("Rule Type", options=['vendor_contains', 'description_contains'])
            new_pattern = st.text_input("Pattern")
        with col2:
            if new_rule_type == 'vendor_contains':
                new_category = st.text_input("Category")
            else:
                new_tx_type = st.selectbox("Transaction Type", options=['expense', 'income', 'transfer_exclude'])
        
        if st.form_submit_button("Add Rule"):
            new_rule = {'rule_type': new_rule_type, 'pattern': new_pattern}
            if new_rule_type == 'vendor_contains':
                new_rule['category'] = new_category
            else:
                new_rule['transaction_type'] = new_tx_type
            st.session_state.rules.append(new_rule)
            st.success("Rule added!")
            st.rerun()

with tabs[4]:
    st.header("Match Detection")
    st.markdown("View probable matches, duplicates, transfers, and card payments")
    
    if st.session_state.normalized_data is None:
        st.warning("Please normalize data first")
    else:
        min_score = st.slider("Minimum Match Score", 0, 100, 60)
        
        if st.button("Find Matches"):
            st.session_state.matches = find_matches(st.session_state.normalized_data, min_score)
            st.success(f"Found {len(st.session_state.matches)} potential matches")
        
        if st.session_state.matches:
            st.subheader(f"Match Results ({len(st.session_state.matches)})")
            
            for i, match in enumerate(st.session_state.matches[:50]):
                match_type_emoji = {
                    'likely_duplicate': '🔴',
                    'transfer': '🔄',
                    'card_payment': '💳',
                    'probable_match': '🟡',
                    'unknown': '❓'
                }.get(match['match_type'], '❓')
                
                with st.expander(f"{match_type_emoji} Match {i+1}: {match['match_type'].replace('_', ' ').title()} (Score: {match['score']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Source A:** {match['tx_a_source']}")
                        st.write(f"Vendor: {match['tx_a_vendor']}")
                        st.write(f"Amount: ${match['tx_a_amount']:.2f}")
                        if match['tx_a_date']:
                            st.write(f"Date: {match['tx_a_date'].strftime('%Y-%m-%d')}")
                    
                    with col2:
                        st.markdown(f"**Source B:** {match['tx_b_source']}")
                        st.write(f"Vendor: {match['tx_b_vendor']}")
                        st.write(f"Amount: ${match['tx_b_amount']:.2f}")
                        if match['tx_b_date']:
                            st.write(f"Date: {match['tx_b_date'].strftime('%Y-%m-%d')}")
                    
                    st.info(f"Reason: {match['reason']}")

with tabs[5]:
    st.header("Review Transactions")
    st.markdown("Review unmatched transactions, conflicts, and uncategorized items")
    
    if st.session_state.normalized_data is None:
        st.warning("Please normalize data first")
    else:
        df = st.session_state.normalized_data
        matched_indices = set()
        
        for match in st.session_state.matches:
            matched_indices.add(match['tx_a_idx'])
            matched_indices.add(match['tx_b_idx'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Unmatched Transactions")
            unmatched = df[~df.index.isin(matched_indices)]
            if not unmatched.empty:
                display_df = unmatched.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df.head(10), use_container_width=True)
            else:
                st.info("All transactions matched")
        
        with col2:
            st.subheader("Uncategorized Transactions")
            uncategorized = df[
                (df['category_raw'].isna() | (df['category_raw'] == '')) &
                (~df.index.isin(matched_indices))
            ]
            if not uncategorized.empty:
                display_df = uncategorized.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df.head(10), use_container_width=True)
            else:
                st.info("No uncategorized transactions")
        
        with col3:
            st.subheader("Blank Vendors")
            blank_vendors = df[
                (df['vendor_raw'].isna() | (df['vendor_raw'] == '')) &
                (~df.index.isin(matched_indices))
            ]
            if not blank_vendors.empty:
                display_df = blank_vendors.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df.head(10), use_container_width=True)
            else:
                st.info("No blank vendors")

with tabs[6]:
    st.header("Category Reconciliation")
    st.markdown("Reconcile category totals across sources and set agreed values")
    
    if st.session_state.normalized_data is None:
        st.warning("Please normalize data first")
    else:
        if st.button("Calculate Category Totals"):
            st.session_state.category_totals = calculate_category_totals(st.session_state.normalized_data)
            st.success("Category totals calculated!")
        
        if st.session_state.category_totals:
            for category, data in st.session_state.category_totals.items():
                with st.expander(f"📊 {category}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.subheader("By Source")
                        for source, amount in data['sources'].items():
                            st.write(f"{source}: ${amount:,.2f}")
                    
                    with col2:
                        st.subheader("Range")
                        st.write(f"Low: ${data['low']:,.2f}")
                        st.write(f"High: ${data['high']:,.2f}")
                        st.write(f"Midpoint: ${data['midpoint']:,.2f}")
                    
                    with col3:
                        st.subheader("Agreed Value")
                        override = st.number_input(
                            "Manual Override",
                            value=data['manual_override'],
                            key=f"override_{category}",
                            step=0.01
                        )
                        if st.button("Save Override", key=f"save_{category}"):
                            st.session_state.category_totals[category]['manual_override'] = override
                    
                    with col4:
                        st.subheader("Actions")
                        if st.button(f"Use Low", key=f"use_low_{category}"):
                            st.session_state.category_totals[category]['manual_override'] = data['low']
                        if st.button(f"Use High", key=f"use_high_{category}"):
                            st.session_state.category_totals[category]['manual_override'] = data['high']
                        if st.button(f"Use Midpoint", key=f"use_mid_{category}"):
                            st.session_state.category_totals[category]['manual_override'] = data['midpoint']
                    
                    st.success(f"Agreed Total: ${data['manual_override']:,.2f}")

with tabs[7]:
    st.header("Export Results")
    st.markdown("Export reconciliation summary and results")
    
    if st.session_state.normalized_data is None:
        st.warning("Please normalize data first")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export as CSV")
            
            export_options = st.multiselect(
                "Select data to export",
                options=['Normalized Transactions', 'Matches', 'Category Totals'],
                default=['Normalized Transactions']
            )
            
            if st.button("Generate CSV Export"):
                output = io.StringIO()
                
                if 'Normalized Transactions' in export_options:
                    df_export = st.session_state.normalized_data.copy()
                    df_export['date'] = df_export['date'].dt.strftime('%Y-%m-%d')
                    output.write("=== NORMALIZED TRANSACTIONS ===\n")
                    output.write(df_export.to_csv(index=False))
                    output.write("\n\n")
                
                if 'Matches' in export_options and st.session_state.matches:
                    output.write("=== MATCHES ===\n")
                    pd.DataFrame(st.session_state.matches).to_csv(output, index=False)
                    output.write("\n\n")
                
                if 'Category Totals' in export_options and st.session_state.category_totals:
                    output.write("=== CATEGORY TOTALS ===\n")
                    for category, data in st.session_state.category_totals.items():
                        output.write(f"{category}: ${data['manual_override']:,.2f}\n")
                
                st.download_button(
                    "Download CSV",
                    data=output.getvalue().encode('utf-8'),
                    file_name='reconciliation_export.csv',
                    mime='text/csv'
                )
        
        with col2:
            st.subheader("Export as JSON")
            
            if st.button("Generate JSON Export"):
                export_data = {
                    'normalized_transactions': st.session_state.normalized_data.to_dict('records'),
                    'matches': st.session_state.matches,
                    'category_totals': st.session_state.category_totals,
                    'export_date': datetime.now().isoformat()
                }
                
                json_output = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    "Download JSON",
                    data=json_output.encode('utf-8'),
                    file_name='reconciliation_export.json',
                    mime='application/json'
                )
        
        st.subheader("Summary Statistics")
        if st.session_state.normalized_data is not None:
            df = st.session_state.normalized_data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transactions", len(df))
            
            with col2:
                st.metric("Total Amount", f"${df['amount'].sum():,.2f}")
            
            with col3:
                st.metric("Sources", df['source'].nunique())
            
            with col4:
                st.metric("Matches Found", len(st.session_state.matches))
            
            if st.session_state.category_totals:
                st.subheader("Agreed Category Totals")
                for category, data in st.session_state.category_totals.items():
                    st.write(f"**{category}:** ${data['manual_override']:,.2f}")

st.markdown("---")
st.caption("CSV Reconciliation MVP - Local-only processing, no data leaves your computer")
