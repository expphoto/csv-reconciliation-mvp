# CSV Reconciliation Tool

A simple, safe tool to help you match up expenses from different financial sources.

## What This Tool Helps You Do

Do you have expenses spread across bank statements, credit cards, and accounting software? Trying to figure out which transactions match across all those sources?

This tool helps you:

- **Upload multiple CSV files** from your bank, credit card, or accounting software
- **Match transactions** across different sources to see what's duplicated or missing
- **Find problems** like uncategorized expenses, blank vendors, or weird transfers
- **Set category totals** and export a clean reconciliation report

You use it entirely on your own computer. Nothing gets sent anywhere online.

## What This Tool Does NOT Do

This is important: this tool is **not** full accounting software or tax software.

- ❌ It does not file taxes for you
- ❌ It does not connect to your bank accounts automatically
- ❌ It does not store your data permanently (it clears when you refresh)
- ❌ It does not replace professional bookkeeping judgment
- ❌ It is not an official accounting authority

Think of it as a helpful assistant that makes the messy job of reconciliation a bit easier.

---

## Quick Start (Try It in 5 Minutes)

If you just want to see how it works with fake data:

1. **Check if you have Python installed**: Open your terminal and type `python3 --version` (Mac) or `python --version` (Windows). If you see a version number like 3.8 or higher, you're good. If not, see the setup instructions below.

2. **Install the app**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. **Try the sample data**: Once the app opens in your browser (it opens automatically), go to the "Upload Sources" tab and upload the 3 CSV files from the `sample-data/` folder. Follow the suggested column mappings to see everything work end-to-end.

---

## Setup Instructions

Choose your operating system below.

### Setting Up on Mac

**Step 1: Check for Python**

Open the Terminal app (you can find it by pressing Command+Space and typing "Terminal"). Then type:

```bash
python3 --version
```

If you see something like `Python 3.8.0` or higher, you're ready! If you see "command not found," you'll need to install Python first from [python.org](https://www.python.org/downloads/).

**Step 2: Download or clone this folder**

Save the `reconcile-mvp` folder somewhere easy to find, like your Desktop or Documents.

**Step 3: Open a terminal in the project folder**

In Terminal, type `cd ` (with a space after it), then drag the `reconcile-mvp` folder into the Terminal window and press Enter. Your line should look something like:

```bash
cd /Users/yourname/Desktop/reconcile-mvp
```

**Step 4: Create a virtual environment** (optional but recommended)

This keeps the app's requirements separate from your other Python projects. Type:

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line.

**Step 5: Install requirements**

```bash
pip install -r requirements.txt
```

**Step 6: Run the app**

```bash
streamlit run app.py
```

Your browser will automatically open to the app. If it doesn't, look for a message in your terminal that says something like `You can now view your Streamlit app in your browser` and open that URL.

---

### Setting Up on Windows

**Step 1: Check for Python**

Open Command Prompt or PowerShell (search for "cmd" or "PowerShell" in your Start menu). Type:

```bash
python --version
```

If you see something like `Python 3.8.0` or higher, you're ready! If you see "is not recognized," you'll need to install Python first from [python.org](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH."

**Step 2: Download or clone this folder**

Save the `reconcile-mvp` folder somewhere easy to find, like your Desktop.

**Step 3: Open Command Prompt in the project folder**

Open Command Prompt, type:

```bash
cd Desktop\reconcile-mvp
```

(Adjust the path if you saved the folder somewhere else.)

**Step 4: Create a virtual environment** (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your command line.

**Step 5: Install requirements**

```bash
pip install -r requirements.txt
```

**Step 6: Run the app**

```bash
streamlit run app.py
```

Your browser will automatically open to the app. If it doesn't, look for the URL shown in your terminal and paste it into your browser.

---

## Using Open Code to Help You

If you're not comfortable with terminals and commands, you can ask an AI coding assistant (like Open Code, GitHub Copilot, or Claude) to do the setup for you.

Open your AI assistant and paste something like this:

> Please set up this local Python project for me. Create a virtual environment, install the requirements from requirements.txt, and run the Streamlit app. If anything fails, fix the setup and tell me what URL to open in my browser.

**Important note about privacy:** Be careful before pasting sensitive financial data into any AI tool. This app runs locally and doesn't send data anywhere, but AI assistants operate differently. Use AI for setup help, not for analyzing your actual financial CSVs unless you're comfortable with that workflow.

---

## How to Use the App

The app has 8 tabs. Work through them in order.

### Tab 1: 📤 Upload Sources

Click "Browse files" and select 2-4 CSV files from different sources:
- Bank statement
- Credit card statement
- Accounting software export
- Any other financial CSV

You can upload up to 4 files at once.

### Tab 2: 🗂️ Map Columns

Each CSV file has different column names. Tell the app what each column means:

- **Date**: Which column has the transaction date?
- **Amount**: Which column has the dollar amount?
- **Vendor**: Which column has the payee/store name?
- **Account**: Which column has the account/card number?
- **Category**: Which column has the category (if your CSV has one)?
- **Memo/Description**: Which column has notes or details?

**Pro tip:** If your CSV has separate "Debit" and "Credit" columns instead of one Amount column, click the "Show debit/credit columns" dropdown and map those instead.

Click "Save Column Mappings" when done.

### Tab 3: ✨ Normalize

Click "Normalize Data" to combine all your CSVs into one standard format.

You'll see a preview of all your transactions with consistent column names. This is your chance to check that everything parsed correctly.

### Tab 4: ⚙️ Rules

You can create simple rules to automatically categorize vendors:

- **Vendor contains "pax8"** → set category to "software_saas"
- **Vendor contains "fred astaire"** → set category to "advertising_marketing"
- **Description contains "autopay"** → mark as transfer (don't match as regular expense)

Rules are optional, but they save time if you have recurring vendors with messy names.

### Tab 5: 🔗 Matches

Click "Find Matches" to see which transactions look like duplicates across sources.

**Match types you'll see:**

- 🔴 **Likely Duplicate** (score 80+): These are almost certainly the same charge appearing in two different sources
- 🔄 **Transfer**: Automatic payments between accounts (marked if description has words like "autopay" or "payment")
- 💳 **Card Payment**: A payment to pay off a credit card bill
- 🟡 **Probable Match** (score 60-79): Might be a match, but needs your review

The app shows you why it thinks two transactions match (same amount, same date, similar vendor name, etc.). Use your judgment!

### Tab 6: 📋 Review

See transactions that didn't match anything or have problems:

- **Unmatched Transactions**: Charges that only appear in one source
- **Uncategorized Transactions**: Expenses without a category assigned
- **Blank Vendors**: Transactions with missing payee information

These are worth reviewing—they might be errors or things you need to investigate.

### Tab 7: 💰 Category Reconciliation

For each expense category, see what each source thinks the total is:

- **By Source**: The total from each CSV file
- **Range**: Lowest and highest values across sources
- **Midpoint**: The average across sources
- **Agreed Value**: Your final number

You can:
- Click "Use Low", "Use High", or "Use Midpoint" to set the agreed value automatically
- Type a custom number in "Manual Override" and click "Save Override"

**Important:** If you use the Manual Override, remember to click "Save Override" to make it stick!

### Tab 8: 📥 Export

Download your results:

- **CSV export**: A human-readable file you can open in Excel or Google Sheets
- **JSON export**: A machine-readable file (useful if you're building other tools)

Choose what you want to export (normalized transactions, matches, category totals) and click download.

---

## Common Mistakes to Watch For

### 1. Matches are suggestions, not facts

The app tries to find similar transactions, but it can be wrong. Two transactions might look identical but actually be different (same amount, same day, different vendor that happens to look similar). Always review matches before accepting them.

### 2. Vendor names are messy

"STARBUCKS COFFEE", "Starbucks", and "SBUX" might all be the same vendor in reality. The app uses fuzzy matching to detect similarity, but it's not perfect. You may need to clean up vendor names in your source CSVs first.

### 3. Transfers and payments can be confusing

A credit card payment from your bank account looks like:
- A debit in your bank statement (money leaving checking)
- A credit in your credit card statement (money reducing card balance)

The app tries to detect these automatically using keywords like "autopay" or "payment," but it may miss some. These are often fine to exclude from expense reconciliation.

### 4. This is a helper, not the boss

This tool is here to make your life easier, not to make decisions for you. Use it to identify problems and patterns, but apply your own business judgment to the results.

---

## Privacy and Safety

**Your data stays on your computer.**

- ✅ The app runs entirely locally on your machine
- ✅ Nothing is uploaded to any server or cloud service
- ✅ No telemetry or tracking
- ✅ When you refresh the page, all data is cleared from the app's memory

**Still, be careful:**

- 📁 Keep backups of your original CSV files
- 🔒 Don't leave sensitive financial files in shared folders
- 💾 Consider clearing your browser cache after using the app
- 🧠 Remember that the app forgets everything when you refresh—you'll need to re-upload files to start over

---

## Sample CSV Files (For Testing)

The `sample-data/` folder has 3 fake CSV files you can use to try the app:

1. **bank_statement.csv** - A fictional bank checking account
2. **credit_card_statement.csv** - A fictional credit card
3. **accounting_export.csv** - A fictional accounting software export

**Suggested column mappings for testing:**

**bank_statement.csv:**
- Date → Date column
- Description → Vendor column
- Amount → Amount column
- Account → Account column

**credit_card_statement.csv:**
- Transaction Date → Date column
- Merchant → Vendor column
- Debit → Amount column
- Category → Category column
- Card Number → Account column

**accounting_export.csv:**
- transaction_date → Date column
- vendor_name → Vendor column
- debit_amount → Amount column
- expense_category → Category column
- account_code → Account column
- notes → Memo column

---

## How the Matching Works (Briefly)

The app scores pairs of transactions from different sources:

| Factor | Points |
|---------|---------|
| Same amount | +50 (strongest signal) |
| Same date | +30 |
| Date within 2 days | +20 |
| Very similar vendor (90%+ match) | +15 |
| Similar vendor (75%+ match) | +10 |
| Same account/card | +10 |

Higher scores = more likely to be a match. You can adjust the "Minimum Match Score" slider to be more or less picky.

---

## Current Limitations

This is a minimal viable product, so it has some constraints:

- **Two-source matching only**: Compares pairs of sources, not all three at once
- **Simple rules only**: Supports "contains" patterns, not complex regex
- **Common date formats**: Handles YYYY-MM-DD and MM/DD/YYYY, but not exotic formats
- **Basic vendor matching**: No advanced entity resolution (e.g., knowing "Amazon AWS" and "Amazon Web Services" are the same)
- **Size limit**: Works best with fewer than 10,000 transactions
- **No saving**: Everything disappears when you refresh the page

---

## Next Steps (Ideas for Future)

If you want to extend this project, here are some ideas:

- Save and load reconciliation sessions
- Generate printable PDF reports
- Support multi-source matching (3+ sources)
- Add regex support for more powerful rules
- Bulk accept/reject multiple matches at once
- Better vendor name normalization
- Track reconciliations over time

---

## Screenshots

*(Screenshots would go here in a polished README. For now, just run the app to see it yourself!)*

---

## Need Help?

If something isn't working:

1. Make sure Python is installed and the version is 3.8 or higher
2. Check that all requirements installed: `pip install -r requirements.txt`
3. Ensure your CSV files have headers in the first row and use commas as separators
4. Try lowering the "Minimum Match Score" if you're not finding matches
5. Check that dates are in a common format (YYYY-MM-DD or MM/DD/YYYY)

For the full technical details, see `docs/ARCHITECTURE.md`.

---

## License

This is an MVP demonstration project. Use it however you'd like for your small business reconciliation needs.

---

*Built with Streamlit, pandas, and rapidfuzz. Runs locally, keeps your data private.*
