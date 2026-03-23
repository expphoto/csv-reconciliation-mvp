# CSV Reconciliation MVP - Architecture

## Overview

This is a local-only web application built with Python and Streamlit that helps small-business owners reconcile expense CSVs from multiple financial sources.

## Technology Stack

- **Frontend**: Streamlit 1.28+
- **Data Processing**: pandas 2.0+
- **Fuzzy Matching**: rapidfuzz 3.0+
- **Language**: Python 3.8+

## Project Structure

```
reconcile-mvp/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── sample-data/              # Synthetic CSV files for testing
│   ├── bank_statement.csv
│   ├── credit_card_statement.csv
│   └── accounting_export.csv
├── tests/                    # Unit tests
│   └── test_app.py
├── docs/
│   └── ARCHITECTURE.md       # This file
└── README.md                 # User documentation
```

## Core Components

### 1. Data Upload & Storage (`st.session_state`)

- **uploaded_files**: Dictionary mapping filenames to DataFrames
- **column_mappings**: Dictionary mapping source names to column configurations
- **normalized_data**: Single DataFrame with all transactions in common schema
- **rules**: List of rule dictionaries for vendor/category normalization
- **matches**: List of detected matches between transactions
- **category_totals**: Dictionary of reconciled category totals

### 2. Common Schema

All transactions are normalized to this schema:

| Field | Type | Description |
|-------|------|-------------|
| date | datetime | Transaction date |
| amount | float | Absolute transaction amount |
| vendor_raw | string | Original vendor name from source |
| vendor_normalized | string | Lowercase, cleaned vendor identifier |
| account | string | Account/card number or name |
| source | string | Source file name |
| category_raw | string | Original category from source |
| memo | string | Description/notes field |
| transaction_type | string | 'expense', 'income', or 'transfer_exclude' |

### 3. Key Functions

#### `parse_date(date_str)`

Parses dates from various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)

**Returns**: pandas Timestamp or None

#### `normalize_to_common_schema(df, mapping, source_name)`

Transforms a source DataFrame to the common schema.

**Parameters**:
- `df`: Source DataFrame
- `mapping`: Dictionary of column mappings (date, amount, vendor, category, account, memo)
- `source_name`: Identifier for the data source

**Returns**: Normalized DataFrame

**Logic**:
- Parses dates using `parse_date()`
- Handles single amount column OR debit/credit columns
- Converts amounts to absolute values
- Creates vendor_normalized by lowercasing and removing spaces/punctuation
- Infers transaction_type from amount sign (if using single amount column)

#### `apply_rules(df, rules)`

Applies user-defined rules to normalize vendors and categories.

**Rule Types**:
- `vendor_contains`: Matches vendor field and sets category
- `description_contains`: Matches memo field and sets transaction_type

**Returns**: DataFrame with `category_mapped` column added

#### `calculate_match_score(tx1, tx2)`

Computes similarity score between two transactions.

**Scoring Model**:
- Same amount: +50 points
- Same date: +30 points
- Date within 2 days: +20 points
- Vendor similarity (>=90%): +15 points
- Vendor similarity (>=75%): +10 points
- Same account: +10 points

**Returns**: Tuple of (score, reason_string)

#### `find_matches(df, min_score)`

Finds all matches between transactions from different sources.

**Match Types**:
- `likely_duplicate`: Score >= 80
- `transfer`: Transaction type is 'transfer_exclude'
- `card_payment`: Account name contains 'card'
- `probable_match`: Score >= min_score but < 80

**Returns**: List of match dictionaries with transaction details

#### `calculate_category_totals(df)`

Aggregates transaction amounts by category and source.

**Calculates per category**:
- Totals by source
- Low value (minimum across sources)
- High value (maximum across sources)
- Midpoint (average across sources)

**Returns**: Dictionary with category reconciliation data

### 4. UI Flow

The application follows an 8-tab workflow:

1. **Upload Sources**: User uploads 2-4 CSV files
2. **Map Columns**: User maps source columns to common schema fields
3. **Normalize**: Data is normalized and previewed
4. **Rules**: User adds/edits vendor and category rules
5. **Matches**: View detected matches, duplicates, transfers
6. **Review**: View unmatched, uncategorized, blank-vendor transactions
7. **Category Reconciliation**: Set agreed category totals
8. **Export**: Download results as CSV or JSON

### 5. Data Flow Diagram

```
CSV Files → Upload → Column Mapping → Normalization
                                              ↓
                                          Apply Rules
                                              ↓
                                          Find Matches
                                              ↓
                                 ┌─────────┴─────────┐
                                 ↓                   ↓
                            Review View        Category Totals
                                 ↓                   ↓
                             Export Results ←─────────┘
```

## Matching Algorithm Details

### Phase 1: Pairwise Comparison

For each pair of transactions from different sources:
1. Calculate match score using `calculate_match_score()`
2. Filter by minimum score threshold (default 60)
3. Determine match type based on score and metadata

### Phase 2: Match Classification

Matches are classified by these rules (in order):

1. If score >= 80: `likely_duplicate`
2. If either transaction has type `transfer_exclude`: `transfer`
3. If either account name contains 'card': `card_payment`
4. Otherwise: `probable_match`

### Phase 3: Deduplication

Transaction pairs are tracked to prevent duplicate match entries.

## Security & Privacy

- **No network calls**: All processing happens locally
- **No telemetry**: No data is sent to any server
- **No cloud dependencies**: Uses only local Python packages
- **No persistence**: Data exists only in session state (cleared on refresh)

## Performance Considerations

- **Time complexity**: O(n²) for matching (n = total transactions)
- **Recommended dataset size**: < 10,000 transactions per session
- **Memory usage**: All data loaded into memory as pandas DataFrames

## Limitations

1. **Matching scope**: Only matches between 2 sources at a time (not multi-way)
2. **Rule complexity**: Only supports simple "contains" pattern matching
3. **Date parsing**: Limited to common date formats
4. **Vendor normalization**: Basic string normalization only (no entity resolution)
5. **Scalability**: Not optimized for large datasets (>10K transactions)

## Extension Ideas

1. **Advanced matching**: Use ML models for better vendor/entity matching
2. **Rule engine**: Support regex, multi-condition rules
3. **Persistence**: Save/load reconciliation sessions
4. **Reports**: Generate PDF summary reports
5. **Bulk operations**: Accept/reject multiple matches at once
6. **Auto-reconciliation**: Suggest category totals based on confidence
7. **Import templates**: Save column mappings as templates for reuse
8. **Data validation**: Flag suspicious transactions (outliers, duplicates within source)

## Testing

Unit tests cover:
- Date parsing from various formats
- Normalization to common schema
- Rules engine application
- Match score calculation
- Category total calculation

Run tests with:
```bash
python -m unittest tests/test_app.py
```
