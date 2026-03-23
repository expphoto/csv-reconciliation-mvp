# Using Open Code (or Similar AI) to Help Set Up the App

If you're not comfortable with terminals and commands, you can ask an AI coding assistant to do the setup for you.

## What to Ask Your AI Assistant

Open your AI assistant (Open Code, GitHub Copilot, Claude, ChatGPT with code analysis, etc.) and paste something like this:

---

**Copy and paste this prompt:**

> Please set up this local Python project for me. Create a virtual environment, install the requirements from requirements.txt, and run the Streamlit app. If anything fails, fix the setup and tell me what URL to open in my browser to access the app.

---

## What the AI Should Do

The AI should walk through these steps:

1. **Create a virtual environment** (`python -m venv venv` or `python3 -m venv venv`)
2. **Activate the virtual environment** (`source venv/bin/activate` on Mac, `venv\Scripts\activate` on Windows)
3. **Install requirements** (`pip install -r requirements.txt`)
4. **Run the app** (`streamlit run app.py`)
5. **Give you a URL** to open in your browser

If something goes wrong (like missing Python or permission issues), the AI should troubleshoot and fix it.

## What to Expect

### On Mac

The AI should give you commands that look like:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### On Windows

The AI should give you commands that look like:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The AI might ask you to copy-paste these commands into your terminal, or it might offer to run them directly if you're using a tool with terminal integration.

## Important: Using AI With Your Data

### For Setup (Safe)
✅ **Using AI for setup is safe.** The AI only needs to see code files and setup instructions. It doesn't need your financial data.

### For Analysis (Be Careful)
⚠️ **Be cautious about sharing CSV files with AI.**

If you want the AI to help you analyze your actual CSVs:

**Consider these risks:**
- AI assistants may store your data on their servers
- Your data might be used to improve the AI's models
- Once uploaded, you can't always delete the data

**Safer alternatives:**
- Use the app yourself first to see results
- Only ask AI to help with structure/formatting, not analysis
- Use synthetic or anonymized data if you need AI help with analysis
- Read the AI assistant's privacy policy before uploading sensitive files

## What If the AI Can't Access the Files?

Some AI tools can't see your local files directly. In that case:

**Option 1: Share the setup commands**
Ask the AI: "Give me the step-by-step commands to set up a Python Streamlit app on Mac/Windows" and run them yourself.

**Option 2: Share non-sensitive files**
You can share files that don't contain sensitive information:
- `requirements.txt` - safe to share
- `app.py` - safe to share (it's just code)
- `sample-data/*.csv` - safe to share (fake data)

**Don't share:**
- Your actual bank statements
- Your actual credit card statements
- Any CSV with real transaction data

## Getting More Help

If the AI gets stuck or gives you confusing instructions:

1. **Ask for clarification**: "Can you explain that in simpler terms?" or "I'm on Windows, can you give me Windows-specific commands?"

2. **Ask for verification**: "Can you check if Python is installed and tell me what version?"

3. **Ask for step-by-step**: "Can you give me one command at a time and wait for me to say it worked before giving the next one?"

4. **Check the other docs**: See [SETUP_MAC.md](./SETUP_MAC.md) or [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) for detailed manual instructions.

## Example Conversation

Here's what a good AI-assisted setup conversation might look like:

**You:** Please set up this local Python project. Create a virtual environment, install the requirements, and run the Streamlit app.

**AI:** I'll help you set up the CSV Reconciliation tool. First, let me check the requirements...

**AI:** I see the project needs streamlit, pandas, and rapidfuzz. Let me create a virtual environment and install these.

**AI:** Run these commands in your terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**You:** I ran the first two commands and see `(venv)` at the start of my line. Is that right?

**AI:** Yes! That means the virtual environment is activated. Go ahead and run the pip install command next.

**You:** Done! No errors. Now what?

**AI:** Great! Now run `streamlit run app.py` to start the app.

**You:** It says "You can now view your Streamlit app in your browser. Local URL: http://localhost:8501"

**AI:** Perfect! Open that URL in your browser and you should see the CSV Reconciliation app. Let me know if you run into any issues.

---

**Ready to try?** Copy the prompt above and paste it into your AI assistant, or follow the manual setup instructions in the main [README.md](../README.md).
