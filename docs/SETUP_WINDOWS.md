# Setup Guide for Windows

This guide walks you through setting up the CSV Reconciliation tool on Windows.

## Step 1: Check if Python is Installed

Open **Command Prompt** or **PowerShell**:

- Press Windows Key
- Type "cmd" for Command Prompt or "powershell" for PowerShell
- Press Enter

Then type:

```bash
python --version
```

**What you should see:** A version number like `Python 3.8.0`, `Python 3.10.0`, or higher.

**What if it says "'python' is not recognized"?**

You don't have Python installed, or it's not in your PATH.

1. Go to [python.org](https://www.python.org/downloads/)
2. Download the latest Python 3 installer (it will say something like "Python 3.12.x")
3. Run the installer
4. **Important:** Check the box that says "Add Python to PATH" before clicking Install
5. Follow the prompts

After installing, open a new Command Prompt window (close the old one first) and try `python --version` again.

## Step 2: Download the Project

Download or clone the `reconcile-mvp` folder to your computer. A good place is your Desktop.

If you downloaded a ZIP file:
1. Right-click the ZIP file
2. Choose "Extract All..."
3. Extract it to your Desktop or wherever you prefer

## Step 3: Open Command Prompt in the Project Folder

Open Command Prompt and navigate to where you saved the folder:

```bash
cd Desktop\reconcile-mvp
```

(If you saved it somewhere else, adjust the path accordingly. For example: `cd Documents\reconcile-mvp`)

**Tip:** You can also open Command Prompt directly in the folder:
1. Open File Explorer
2. Navigate to the reconcile-mvp folder
3. Click in the address bar at the top and type `cmd`
4. Press Enter

## Step 4: Create a Virtual Environment (Recommended but Optional)

A virtual environment keeps the app's requirements separate from other Python projects on your computer.

```bash
python -m venv venv
```

Wait a moment for it to create. You'll see a new `venv` folder appear in your project folder.

Then activate it:

```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your command line, like this:
```bash
(venv) C:\Users\YourName\Desktop\reconcile-mvp>
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

After a moment, your browser should automatically open to the app. If it doesn't, look in Command Prompt for a message like:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

Copy that URL and paste it into your browser.

## Step 7: Stop the App When You're Done

When you're finished using the app, go back to Command Prompt and press:

- `Control + C` (hold Control, press C)

This stops the app. You can close Command Prompt if you want.

## Running It Again Later

Next time you want to use the app:

1. Open Command Prompt
2. Navigate to the folder: `cd Desktop\reconcile-mvp` (or wherever you saved it)
3. Activate the virtual environment: `venv\Scripts\activate`
4. Run the app: `streamlit run app.py`

That's it!

## Troubleshooting

**"'python' is not recognized"**

Make sure you checked "Add Python to PATH" during installation. If you didn't:
1. Re-run the Python installer
2. Choose "Modify" or "Repair"
3. Make sure "Add Python to PATH" is checked

**"pip: command not found"**

Try `python -m pip install -r requirements.txt` instead.

**ModuleNotFoundError: No module named 'streamlit'**

The requirements didn't install properly. Try:
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**"The system cannot find the path specified"**

Check that you're in the right folder. Type `dir` to see what's in the current directory. You should see `app.py`, `requirements.txt`, and the other project files.

**Firewall or antivirus warning**

Some security software might warn you about Streamlit opening a local web server. This is normal—the app runs entirely on your computer. You can allow it.

**Port 8501 is already in use**

This means something else is already using the port. Either close that other application, or run Streamlit on a different port:
```bash
streamlit run app.py --server.port 8502
```

**PowerShell execution policy error**

If PowerShell says running scripts is disabled, you can either:
- Use Command Prompt instead (it doesn't have this restriction)
- Or run this command once in PowerShell (as administrator):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

---

Still having trouble? Check the main [README.md](../README.md) for general troubleshooting tips.
