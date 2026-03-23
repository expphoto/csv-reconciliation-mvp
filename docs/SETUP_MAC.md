# Setup Guide for Mac

This guide walks you through setting up the CSV Reconciliation tool on a Mac.

## Step 1: Check if Python is Installed

Open the **Terminal** app (you can find it by pressing Command+Space and typing "Terminal") and type:

```bash
python3 --version
```

**What you should see:** A version number like `Python 3.8.0`, `Python 3.9.7`, or higher.

**What if it says "command not found"?**

You don't have Python installed. Go to [python.org](https://www.python.org/downloads/) and download the latest Python 3 installer. Run it and follow the installation prompts.

## Step 2: Download the Project

Download or clone the `reconcile-mvp` folder to your computer. A good place is your Desktop or Documents.

If you downloaded a ZIP file, double-click it to extract it.

## Step 3: Open Terminal in the Project Folder

In Terminal, you need to "change directory" (cd) to the project folder.

Type this:
```bash
cd
```

(Include a space after `cd`, but don't press Enter yet!)

Now drag the `reconcile-mvp` folder from Finder into the Terminal window. The path will automatically appear. Press Enter.

Your Terminal line should now look something like:
```bash
cd /Users/yourname/Desktop/reconcile-mvp
```

## Step 4: Create a Virtual Environment (Recommended but Optional)

A virtual environment keeps the app's requirements separate from other Python projects on your Mac. It's a good habit, even if you're new to Python.

```bash
python3 -m venv venv
```

Wait a moment for it to create. Then activate it:

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your Terminal line, like this:
```bash
(venv) yourname@MacBook-Pro ~ %
```

This tells you the virtual environment is active.

## Step 5: Install the Requirements

Now install the Python packages the app needs:

```bash
pip install -r requirements.txt
```

This will download and install: streamlit, pandas, rapidfuzz, and python-dateutil.

This might take a minute or two. You'll see lots of text scroll by. Wait until it finishes and you see your command prompt again.

## Step 6: Run the App

Start the app:

```bash
streamlit run app.py
```

After a moment, your browser should automatically open to the app. If it doesn't, look in Terminal for a message like:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

Copy that URL and paste it into your browser.

## Step 7: Stop the App When You're Done

When you're finished using the app, go back to Terminal and press:

- `Control + C` (hold Control, press C)

This stops the app. You can close Terminal if you want.

## Running It Again Later

Next time you want to use the app:

1. Open Terminal
2. Navigate to the folder: `cd Desktop/reconcile-mvp` (or wherever you saved it)
3. Activate the virtual environment: `source venv/bin/activate`
4. Run the app: `streamlit run app.py`

That's it!

## Troubleshooting

**"Python 3" isn't found**

Try just `python --version` instead of `python3 --version`. Some Macs have Python named differently.

**"pip: command not found"**

Try `python3 -m pip install -r requirements.txt` instead.

**ModuleNotFoundError: No module named 'streamlit'**

The requirements didn't install properly. Try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Port 8501 is already in use**

This means something else is already using the port. Either close that other application, or run Streamlit on a different port:
```bash
streamlit run app.py --server.port 8502
```

**Permission denied when installing**

If you get permission errors, you might need to use a virtual environment (Step 4) or check that you have write permissions for the folder.

---

Still having trouble? Check the main [README.md](../README.md) for general troubleshooting tips.
