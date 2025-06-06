# DegreeWise Copilot

Turn your Degree Works audit into an interactive academic planning assistant.

DegreeWise Copilot is a Streamlit app powered by GPT-4o. Upload your Degree Works PDF and the app will:

- Parse your completed/remaining courses, credit counts, and GPA.  
- Show “Earned,” “Applied,” “Remaining,” and “Required” credits.  
- Estimate your graduation term (e.g., May 2027).  
- Suggest 15-credit semester schedules (downloadable as CSV).  
- Provide a chat interface for free-form questions about your degree plan.  
- Include a GPA “What-If” simulator.

---

## Getting Started

### Prerequisites

- Python 3.12 installed  
- An OpenAI API key  
- (Optional) Git, if you want to clone this repo

### Clone the repository

```bash
git clone https://github.com/HarshPahilajani05/degreewise_copilot.git
cd degreewise_copilot

Installation (Windows)
1. Create a virtual environment
shell:
python -m venv .venv
2. Activate the venv in Shell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate
3. Install dependencies
shell:
pip install --upgrade pip
pip install streamlit pypdf openai python-dotenv pandas altair
4. Create a .env file next to main.py:
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
MODEL=gpt-4o-mini
5. Run the app
shell
python -m streamlit run main.py

Installation (macOS/Linux)
git clone https://github.com/HarshPahilajani05/degreewise_copilot.git
cd degreewise_copilot
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install streamlit pypdf openai python-dotenv pandas altair
echo "OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX" > .env
echo "MODEL=gpt-4o-mini" >> .env
python -m streamlit run main.py

### Usage
Upload a Degree Works PDF from the sidebar.

The Dashboard tab shows your credit metrics and graduation estimate.

The Chat tab lets you ask questions like “How many credits remain?”

The GPA Simulator tab models how future grades affect your GPA.

The About tab explains the project and tech stack.

## Demo Screenshots

> *After uploading a Degree Works PDF, the Dashboard automatically appears with your key metrics, chart, and schedule suggestions.*

![Dashboard Screenshot](https://github.com/user-attachments/assets/09eed5ec-581d-46ca-8c26-ac221f007773)

> *Use the Chat tab to ask free-form questions about your degree plan.*

![Chat Screenshot](https://github.com/user-attachments/assets/6815ad41-9208-4730-8324-db789cfc5f19)

