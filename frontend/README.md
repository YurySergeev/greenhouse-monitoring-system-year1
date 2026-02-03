# Frontend – Greenhouse Monitoring System


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
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/main.py


- set up and run for Windows
cd frontend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/main.py


-open browser
