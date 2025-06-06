import os
import json
import itertools
import io
import datetime
import math
import re

import streamlit as st
import altair as alt
import pandas as pd
from pypdf import PdfReader
from dotenv import load_dotenv
import openai
from json import JSONDecodeError


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
st.set_page_config(page_title="DegreeWise Copilot", page_icon="🎓", layout="wide")


def extract_text(file):
    reader = PdfReader(file)
    return "\n".join(p.extract_text() for p in reader.pages)

def safe_json_load(txt):
    """
    Strip code fences or extra prose; parse the first {...} block.
    Return None on failure.
    """
    cleaned = re.sub(r"```[^`]*\n", "", txt).strip("` \n")
    m = re.search(r"\{.*\}", cleaned, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except JSONDecodeError:
        return None

def audit_to_json(text):
    """
    Ask GPT-4o to convert the degree audit into JSON containing:
      - completedCourses[] (each has 'code' & 'credits')
      - remainingCourses[] (each has 'code' & 'credits')
      - creditsEarned   (number)
      - creditsApplied  (number)
      - creditsNeeded   (number)
      - creditsRequired (number)
      - overallGPA      (number)
    Return None if GPT cannot produce valid JSON.
    """
    prompt = (
        "Convert this degree audit into JSON with keys:\n"
        "  - completedCourses (array of {code, credits})\n"
        "  - remainingCourses (array of {code, credits})\n"
        "  - creditsEarned   (number)\n"
        "  - creditsApplied  (number)\n"
        "  - creditsNeeded   (number)\n"
        "  - creditsRequired (number)\n"
        "  - overallGPA      (number)\n"
        "Return ONLY valid JSON with exactly those keys; no Markdown or commentary. "
        "If you cannot, return the string ERROR.\n\n"
        + text[:4000]
    )
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    raw = resp.choices[0].message.content
    if raw.strip().startswith("ERROR"):
        return None
    return safe_json_load(raw)

def valid_schedules(rem_list, floor=15, max_courses=5, top_n=3):
    """
    From rem_list = [(code, credits), ...], find up to top_n combinations
    of 3..max_courses courses whose total credits >= floor.
    """
    picks = []
    for r in range(3, max_courses + 1):
        for combo in itertools.combinations(rem_list, r):
            total = sum(c[1] for c in combo)
            if total >= floor:
                picks.append((combo, total))
                if len(picks) == top_n:
                    return picks
    return picks

def gpa_after_term(cur_cred, cur_pts, new_cred, term_gpa):
    """
    Given:
      - cur_cred: current earned credits
      - cur_pts:  current total quality points (credits * GPA)
      - new_cred: credits planned for next term
      - term_gpa: target GPA for next term
    Return the new cumulative GPA.
    """
    return round((cur_pts + term_gpa * new_cred) / (cur_cred + new_cred), 3)

def estimate_grad_term(applied, required, earned):
    """
    Estimate graduation term:
      - 'applied' = credits earned + in-progress (e.g. registered for Fall)
      - 'required' = total credits needed for degree
      - 15 credits assumed per future semester
      - If 'applied > earned', assume those in-progress credits are for Fall this year,
        so the next term is Spring next year.
      - Otherwise, determine the next academic term based on current date:
          * Jan–Apr  => Spring of current year
          * May–Aug  => Fall   of current year
          * Sep–Dec  => Spring of next year
      - Advance by ceil((required - applied) / 15) semesters (skipping summers),
        flipping Spring↔Fall and incrementing year appropriately.
      - Return "May YYYY" if finishing in Spring, "Dec YYYY" if finishing in Fall.
    """
    needed = required - applied
    if needed <= 0:
        return "Already eligible"

    sems_needed = math.ceil(needed / 15)

    today = datetime.date.today()
    month = today.month
    year = today.year


    if applied > earned:
        term, term_year = ("Spring", year + 1)
    else:
        if month <= 4:
            term, term_year = ("Spring", year)
        elif month <= 8:
            term, term_year = ("Fall", year)
        else:
            term, term_year = ("Spring", year + 1)


    for _ in range(sems_needed - 1):
        if term == "Fall":
            term = "Spring"
            term_year += 1
        else:  # Spring
            term = "Fall"
            # same year for Fall


    return f"May {term_year}" if term == "Spring" else f"Dec {term_year}"


st.sidebar.header("🎓 DegreeWise Copilot")
page = st.sidebar.radio("Navigate", ["Dashboard", "Chat", "GPA Simulator", "About"],
                        label_visibility="collapsed")
pdf_file = st.sidebar.file_uploader("Upload Degree Works PDF", type="pdf")

if "audit" not in st.session_state and pdf_file:
    with st.spinner("Parsing audit…"):
        audit_data = audit_to_json(extract_text(pdf_file))
        if audit_data:
            st.session_state.audit = audit_data
            st.sidebar.success("Audit loaded!")
            st.sidebar.balloons()
        else:
            st.sidebar.error("❌ Parse failed. Try a smaller PDF or re-upload.")

audit = st.session_state.get("audit")  # may be None


if page == "Dashboard":
    st.header("📊 Progress Dashboard")
    if not audit:
        st.info("Upload your Degree Works PDF in the sidebar to begin.")
        st.stop()

    earned   = audit.get("creditsEarned", 0)    # finished credits
    applied  = audit.get("creditsApplied", 0)   # finished + in-progress
    needed   = audit.get("creditsNeeded", 0)    # remaining to hit applied
    required = audit.get("creditsRequired", needed + applied)


    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Earned Credits",  earned)
    c2.metric("Applied Credits", applied)
    c3.metric("Remaining Credits", needed)
    c4.metric("Required Credits", required)


    overall_gpa = audit.get("overallGPA")
    if overall_gpa is not None:
        st.subheader(f"🎓 Overall GPA: {overall_gpa:.2f}")


    grad_term = estimate_grad_term(applied, required, earned)
    st.subheader(f"📅 Estimated Graduation: {grad_term}")


    chart_df = pd.DataFrame({
        "Category": ["Applied", "Remaining"],
        "Credits":  [applied, needed]
    })
    st.altair_chart(
        alt.Chart(chart_df).mark_bar().encode(
            x=alt.X("Category:N", axis=alt.Axis(labelAngle=0)),
            y="Credits:Q", tooltip=["Credits"]
        ).properties(height=300),
        use_container_width=True
    )


    st.subheader("📚 15-Credit Schedule Suggestions")
    rem_list = [(c["code"], c["credits"]) for c in audit.get("remainingCourses", [])]
    opts = valid_schedules(rem_list)
    if opts:
        plan_df = pd.DataFrame(
            [{"Option": i+1,
              "Courses": ", ".join(c[0] for c in opt),
              "Total Credits": tot}
             for i, (opt, tot) in enumerate(opts)]
        )
        st.table(plan_df)

        buf = io.StringIO()
        pd.DataFrame(opts[0][0], columns=["Course", "Credits"]).to_csv(buf, index=False)
        st.download_button("⬇️ Download Option 1 as CSV", buf.getvalue(), "semester_plan.csv")
    else:
        st.info("No 3- to 5-course combos hit 15 credits.")


elif page == "Chat":
    st.header("💬 Ask DegreeWise Copilot")
    if not audit:
        st.info("Upload your Degree Works PDF to start chatting.")
        st.stop()

    if "history" not in st.session_state:
        st.session_state.history = [
            {"role": "system",
             "content": "You are an academic-advisor assistant. "
                        "Here is the student's audit JSON:\n" + json.dumps(audit)}
        ]


    for msg in st.session_state.history[1:]:
        st.chat_message(msg["role"]).write(msg["content"])

    if question := st.chat_input("Ask about your degree plan…"):
        st.chat_message("user").write(question)
        st.session_state.history.append({"role": "user", "content": question})
        with st.spinner("Thinking…"):
            resp = openai.chat.completions.create(
                model=MODEL,
                messages=st.session_state.history,
                temperature=0.3,
                max_tokens=400
            )
        answer = resp.choices[0].message.content
        st.session_state.history.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)


elif page == "GPA Simulator":
    st.header("🎯 GPA What-If")
    if not audit:
        st.info("Upload your Degree Works PDF to enable GPA simulation.")
        st.stop()

    earned = audit.get("creditsEarned", 0)
    cur_gpa = audit.get("overallGPA", 3.0)
    cur_pts = earned * cur_gpa

    target = st.slider("Desired term GPA", 2.0, 4.0, 3.5, 0.1)
    term_credits = st.slider("Credits next term", 12, 18, 15)
    new_cum = gpa_after_term(earned, cur_pts, term_credits, target)
    st.success(f"With **{target}** on **{term_credits}** credits, "
               f"cumulative GPA becomes **{new_cum:.2f}**.")


else:
    st.header("ℹ️ About DegreeWise Copilot")
    st.markdown("""
**DegreeWise Copilot** is a Streamlit + GPT-4o demo that converts a static Degree Works audit
into an interactive academic-planning assistant.

* Python 3.12 · Streamlit · Altair · OpenAI GPT-4o  
* Verified 15-credit semester builder  
* GPA what-if simulator & CSV export  
* Developed in ~5 days as a portfolio showcase for software-engineering internships
""")
