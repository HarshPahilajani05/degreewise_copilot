# DegreeWise Copilot

**Turn your Degree Works audit into an interactive academic planning assistant.**

DegreeWise Copilot is a Streamlit-based web app powered by OpenAI’s GPT-4o model. Upload a PDF copy of your Degree Works audit, and watch as the app:

- Parses completed and remaining courses, credit counts, and overall GPA.
- Visualizes “Earned,” “Applied,” “Remaining,” and “Required” credits.
- Estimates your graduation term (e.g., **May 2027**).
- Suggests multiple 15-credit semester schedules you can download as CSV.
- Provides a chat interface to ask natural-language questions about your degree plan.
- Includes a GPA “What-If” simulator to see how future grades affect your cumulative GPA.

Whether you’re a first-year student or about to graduate, DegreeWise Copilot makes understanding and planning your path effortless.

---

## Features

- **Dashboard**  
  - Metrics for Earned, Applied, Remaining, and Required credits  
  - Display of Overall GPA (if present in your audit)  
  - Estimated Graduation term (accounts for in-progress credits and assumes 15 credits/semester)  
  - Bar chart of Applied vs. Remaining credits  
  - Downloadable 15-credit semester plan (CSV)

- **Chat Interface**  
  - Ask questions like “How many remaining upper-level CS credits do I have?”  
  - Receive instant, GPT-powered answers based on your audit data  
  - Example questions: “Can I graduate by Spring 2027?” or “Which courses double-count for major and electives?”

- **GPA Simulator**  
  - Input your current or target term GPA and planned credits  
  - Instantly calculate your new cumulative GPA  

- **CSV Export**  
  - One-click download of the first suggested 15-credit plan for easy sharing or import into other tools

- **About Page**  
  - Brief project description and technology stack  
  - Notes on development time (≈ 5 days) and purpose (portfolio showcase)

---

## Demo Screenshot

> *After uploading a Degree Works PDF, the Dashboard automatically appears with your key metrics, chart, and schedule suggestions.*

![Dashboard Screenshot](./assets/dashboard_example.png)

> *Use the Chat tab to ask free-form questions about your degree plan.*

![Chat Screenshot](./assets/chat_example.png)

---

## Getting Started

### Prerequisites

- **Python 3.12** (or 3.11) installed on your machine  
- A free [OpenAI API key](https://platform.openai.com)  
- Optional: [Git](https://git-scm.com/) if you want to clone this repo

### Installation

1. **Clone the repository** (or download the ZIP):

   ```bash
   git clone https://github.com/HarshPahilajani05/degreewise_copilot.git
   cd degreewise_copilot
