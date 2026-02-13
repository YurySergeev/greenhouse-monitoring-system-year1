# Instructuctions to run Frontend – Greenhouse Monitoring System


---

## Run the Streamlit App Locally

### Requirements
- Python 3.10+ (3.11 recommended)
- Git
- macOS / Linux / Windows

Check your Python version:
```bash
python --version

- set up for OS/linux
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app/Home.py


- set up and run for Windows
cd frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app/Home.py


-open browser
