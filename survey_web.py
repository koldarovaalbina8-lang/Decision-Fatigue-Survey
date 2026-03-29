import streamlit as st
import streamlit.components.v1 as components
import json
import csv
import re
from io import StringIO
from pathlib import Path
from datetime import datetime, date

# =========================================================
# AI-Based Decision Fatigue Assessment System - Web Version
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "questions.json"
ALL_RESULTS_FILE = BASE_DIR / "saved_results_history.json"

VALID_NAME_PATTERN = r"^[A-Za-z\s\-']+$"
GENDER_OPTIONS = ("Male", "Female", "Other", "Prefer not to say")
YEAR_OPTIONS = (1, 2, 3, 4)
OPTION_TEXTS = ["Never", "Rarely", "Sometimes", "Often", "Always"]
NORMAL_SCORES = [0, 1, 2, 3, 4]
REVERSE_SCORES = [4, 3, 2, 1, 0]

RESULT_BANDS = [
    (0, 13, "Mentally Clear", "You currently show a low level of decision fatigue."),
    (14, 26, "Mild Cognitive Load", "You show some mental tiredness, but it is still manageable."),
    (27, 39, "Noticeable Decision Fatigue", "Your answers suggest a moderate level of mental overload."),
    (40, 52, "High Mental Overload", "You may be struggling with significant mental pressure."),
    (53, 66, "Severe Cognitive Exhaustion", "Your results suggest serious emotional and cognitive fatigue."),
    (67, 80, "Critical Mental Drain", "Your level of overload is very high and support is strongly recommended.")
]

# Variable types for assessment criteria
example_int = 1
example_float = 7.5
example_str = "survey"
example_list = [1, 2, 3]
example_tuple = ("A", "B")
example_range = range(5)
example_bool = True
example_dict = {"mode": "web"}
example_set = {1, 2, 3}
example_frozenset = frozenset({"txt", "csv", "json"})

if "latest_result" not in st.session_state:
    st.session_state["latest_result"] = None

if "average_sleep_raw" not in st.session_state:
    st.session_state["average_sleep_raw"] = ""

st.set_page_config(
    page_title="AI-Based Decision Fatigue Assessment System",
    page_icon="🧠",
    layout="wide"
)

# ---------------------------------------------------------
# Custom style
# ---------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(124, 182, 255, 0.22), transparent 28%),
        radial-gradient(circle at 90% 8%, rgba(255, 174, 201, 0.16), transparent 24%),
        radial-gradient(circle at 85% 85%, rgba(130, 230, 180, 0.15), transparent 22%),
        linear-gradient(180deg, #eef4ff 0%, #f7f7ff 48%, #eef8f3 100%);
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2.6rem;
    max-width: 1380px;
}

.main-title {
    font-size: 3.15rem;
    font-weight: 800;
    color: #25324a;
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}

.subtitle {
    font-size: 1.12rem;
    color: #596883;
    margin-bottom: 1rem;
}

.hero-box {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 26px;
    padding: 24px 26px;
    box-shadow: 0 12px 30px rgba(31, 59, 115, 0.08);
    margin-bottom: 0.9rem;
}

.info-box {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(8px);
    border-radius: 20px;
    padding: 16px 18px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.05);
    border-left: 6px solid #7ea6ff;
    margin-bottom: 0.9rem;
}

.section-card {
    background: rgba(255,255,255,0.84);
    backdrop-filter: blur(8px);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.question-box {
    background: rgba(255,255,255,0.88);
    backdrop-filter: blur(6px);
    border-radius: 18px;
    padding: 15px 17px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.045);
    margin-bottom: 12px;
    border: 1px solid rgba(110, 143, 214, 0.10);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.question-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(44, 73, 140, 0.08);
}

.result-box {
    background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(242, 252, 246, 0.96));
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.06);
    border-left: 8px solid #43a76b;
    margin-top: 1rem;
}

.small-muted {
    color: #5e6b82;
    font-size: 0.96rem;
}

.progress-label {
    font-weight: 700;
    color: #30435f;
    margin-bottom: 0.45rem;
}

.fact-card {
    background: rgba(255,255,255,0.84);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 8px 22px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}

.fact-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #28406b;
    margin-bottom: 0.8rem;
}

.fact-item {
    background: rgba(247, 250, 255, 0.95);
    border-left: 5px solid #97b4ff;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 12px;
    color: #42526b;
    line-height: 1.55;
    animation: fadeUp 0.45s ease;
}

.answer-flash {
    display: inline-block;
    background: linear-gradient(90deg, #e9fff2, #f4fffa);
    color: #167a4b;
    border: 1px solid #b7ebcb;
    border-radius: 999px;
    padding: 7px 14px;
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 10px;
    animation: popIn 0.45s ease-out;
    box-shadow: 0 4px 12px rgba(35, 160, 98, 0.12);
}

.soft-pill {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(126, 166, 255, 0.14);
    color: #31528c;
    font-weight: 700;
    font-size: 0.9rem;
    margin-bottom: 0.9rem;
}

.saved-result-card {
    background: rgba(255,255,255,0.86);
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    margin-bottom: 12px;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eef3fb 0%, #f6f8fd 100%);
}

div[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem;
}

.stDownloadButton > button,
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

@keyframes popIn {
    0% {
        opacity: 0;
        transform: translateY(-6px) scale(0.96);
    }
    60% {
        opacity: 1;
        transform: translateY(0px) scale(1.02);
    }
    100% {
        opacity: 1;
        transform: translateY(0px) scale(1);
    }
}

@keyframes fadeUp {
    0% {
        opacity: 0;
        transform: translateY(8px);
    }
    100% {
        opacity: 1;
        transform: translateY(0px);
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sound
# ---------------------------------------------------------
SUCCESS_SOUND_BASE64 = (
    "UklGRlQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YTAAAAA="
)

def play_success_sound():
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/wav;base64,{SUCCESS_SOUND_BASE64}" type="audio/wav">
    </audio>
    """
    components.html(audio_html, height=0)

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def validate_name(name):
    return bool(re.fullmatch(VALID_NAME_PATTERN, name.strip()))

def validate_student_id(student_id):
    return student_id.isdigit()

def validate_dob_value(dob_value):
    if dob_value is None:
        return "Please select your date of birth."

    today = date.today()

    if dob_value > today:
        return "Date of birth cannot be in the future."

    age = today.year - dob_value.year - ((today.month, today.day) < (dob_value.month, dob_value.day))

    if age < 7:
        return "Date of birth is not realistic for this survey."
    if age > 130:
        return "Date of birth is not realistic."

    return None

def normalize_sleep_hours_text(sleep_text):
    if not sleep_text.strip():
        return "", None, "Please enter average sleep hours per night."

    try:
        value = float(sleep_text.replace(",", ".").strip())
        if 0 <= value <= 24:
            return f"{value:.1f}", value, None
        return sleep_text, None, "Average sleep hours must be between 0 and 24."
    except ValueError:
        return sleep_text, None, "Average sleep hours must be a valid number, for example 6 or 7.5."

def validate_questions(questions):
    if not isinstance(questions, list):
        return False

    if len(questions) < 15 or len(questions) > 25:
        return False

    for item in questions:
        if not isinstance(item, dict):
            return False
        if "question" not in item or "reverse" not in item:
            return False
        if not isinstance(item["question"], str):
            return False
        if not isinstance(item["reverse"], bool):
            return False

    return True

def load_questions():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
            questions = json.load(file)

        if validate_questions(questions):
            return questions, None
        return [], "questions.json exists, but its structure is invalid."

    except FileNotFoundError:
        return [], "questions.json was not found in the same folder as survey_web.py."
    except json.JSONDecodeError:
        return [], "questions.json has invalid JSON format."
    except OSError as error:
        return [], f"An error occurred while reading questions.json: {error}"

def get_question_score(is_reverse, selected_index):
    if is_reverse:
        return REVERSE_SCORES[selected_index]
    return NORMAL_SCORES[selected_index]

def interpret_score(score):
    for minimum, maximum, state, interpretation in RESULT_BANDS:
        if minimum <= score <= maximum:
            return state, interpretation
    return "Unknown State", "No interpretation available."

def build_result_record(
    surname,
    given_name,
    dob_value,
    student_id,
    gender,
    year_of_study,
    average_sleep_hours,
    total_score,
    average_score,
    psychological_state,
    interpretation,
    answer_details
):
    return {
        "surname": surname,
        "given_name": given_name,
        "date_of_birth": dob_value.strftime("%d/%m/%Y"),
        "student_id": student_id,
        "gender": gender,
        "year_of_study": year_of_study,
        "average_sleep_hours": average_sleep_hours,
        "total_score": total_score,
        "average_score": average_score,
        "psychological_state": psychological_state,
        "interpretation": interpretation,
        "completed": True,
        "completion_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "answer_details": answer_details
    }

def save_result_history(result_data):
    history = load_saved_history()
    history.append(result_data)
    with open(ALL_RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

def load_saved_history():
    if not ALL_RESULTS_FILE.exists():
        return []

    try:
        with open(ALL_RESULTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def convert_result_to_json_text(result_data):
    return json.dumps(result_data, indent=4, ensure_ascii=False)

def convert_result_to_txt_text(result_data):
    lines = []

    for key, value in result_data.items():
        if key != "answer_details":
            lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("Detailed Answers:")

    for item in result_data["answer_details"]:
        lines.append(
            f"Q{item['question_number']}: {item['question_text']} | "
            f"Answer: {item['selected_option']} | "
            f"Score: {item['score_awarded']} | "
            f"Reverse: {item['reverse_scored']}"
        )

    return "\n".join(lines)

def convert_result_to_csv_text(result_data):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["field", "value"])
    for key, value in result_data.items():
        if key != "answer_details":
            writer.writerow([key, value])

    writer.writerow([])
    writer.writerow(["question_number", "question_text", "selected_option", "score_awarded", "reverse_scored"])

    for item in result_data["answer_details"]:
        writer.writerow([
            item["question_number"],
            item["question_text"],
            item["selected_option"],
            item["score_awarded"],
            item["reverse_scored"]
        ])

    return output.getvalue()

def parse_uploaded_json(uploaded_file):
    try:
        return json.load(uploaded_file), None
    except Exception:
        return None, "The uploaded JSON file could not be read."

def parse_uploaded_txt(uploaded_file):
    try:
        content = uploaded_file.read().decode("utf-8")
        lines = content.splitlines()

        result_data = {}
        answer_details = []
        detailed_section = False

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line == "Detailed Answers:":
                detailed_section = True
                continue

            if not detailed_section and ": " in line:
                key, value = line.split(": ", 1)
                result_data[key] = value
            elif detailed_section and line.startswith("Q"):
                answer_details.append(line)

        if "year_of_study" in result_data:
            result_data["year_of_study"] = int(result_data["year_of_study"])
        if "average_sleep_hours" in result_data:
            result_data["average_sleep_hours"] = float(result_data["average_sleep_hours"])
        if "total_score" in result_data:
            result_data["total_score"] = int(result_data["total_score"])
        if "average_score" in result_data:
            result_data["average_score"] = float(result_data["average_score"])
        if "completed" in result_data:
            result_data["completed"] = result_data["completed"] == "True"

        result_data["answer_details"] = answer_details
        return result_data, None

    except Exception:
        return None, "The uploaded TXT file could not be read."

def parse_uploaded_csv(uploaded_file):
    try:
        content = uploaded_file.read().decode("utf-8")
        reader = list(csv.reader(StringIO(content)))

        result_data = {}
        answer_details = []
        detailed_section = False

        for row in reader:
            if not row:
                continue

            if row[0] == "field":
                continue

            if row[0] == "question_number":
                detailed_section = True
                continue

            if not detailed_section and len(row) >= 2:
                result_data[row[0]] = row[1]
            elif detailed_section and len(row) >= 5:
                answer_details.append({
                    "question_number": int(row[0]),
                    "question_text": row[1],
                    "selected_option": row[2],
                    "score_awarded": int(row[3]),
                    "reverse_scored": row[4] == "True"
                })

        if "year_of_study" in result_data:
            result_data["year_of_study"] = int(result_data["year_of_study"])
        if "average_sleep_hours" in result_data:
            result_data["average_sleep_hours"] = float(result_data["average_sleep_hours"])
        if "total_score" in result_data:
            result_data["total_score"] = int(result_data["total_score"])
        if "average_score" in result_data:
            result_data["average_score"] = float(result_data["average_score"])
        if "completed" in result_data:
            result_data["completed"] = result_data["completed"] == "True"

        result_data["answer_details"] = answer_details
        return result_data, None

    except Exception:
        return None, "The uploaded CSV file could not be read."

def display_loaded_result(data, title):
    st.subheader(title)
    st.write(f"**Surname:** {data.get('surname', '')}")
    st.write(f"**Given Name:** {data.get('given_name', '')}")
    st.write(f"**Date of Birth:** {data.get('date_of_birth', '')}")
    st.write(f"**Student ID:** {data.get('student_id', '')}")
    st.write(f"**Gender:** {data.get('gender', '')}")
    st.write(f"**Year of Study:** {data.get('year_of_study', '')}")
    st.write(f"**Average Sleep Hours:** {data.get('average_sleep_hours', '')}")
    st.write(f"**Total Score:** {data.get('total_score', '')}")
    st.write(f"**Average Score:** {data.get('average_score', '')}")
    st.write(f"**Psychological State:** {data.get('psychological_state', '')}")
    st.write(f"**Interpretation:** {data.get('interpretation', '')}")
    st.write(f"**Completed:** {data.get('completed', '')}")
    st.write(f"**Completion Time:** {data.get('completion_time', '')}")

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">🧠 AI-Based Decision Fatigue Assessment System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A data-driven psychological evaluation tool for students</div>',
    unsafe_allow_html=True
)

questions, questions_error = load_questions()

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.markdown("## Navigation")
sidebar_mode = st.sidebar.radio(
    "Choose an option",
    ["Start New Questionnaire", "Load Existing Result"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Survey Purpose")
st.sidebar.write(
    "This web application explores how repeated choices, academic demands, and cognitive strain may influence a student's current psychological balance."
)

# ---------------------------------------------------------
# Main content
# ---------------------------------------------------------
if sidebar_mode == "Start New Questionnaire":
    if questions_error:
        st.error(questions_error)
        st.stop()

    left_col, right_col = st.columns([2.2, 1], gap="large")

    with left_col:
        st.markdown("""
        <div class="hero-box">
            <div style="font-size:1.45rem; font-weight:800; color:#27344c; margin-bottom:0.55rem;">
                Intelligent Decision Fatigue Analysis
            </div>
            <div style="color:#53627c; line-height:1.7; font-size:1.02rem;">
                This web-based questionnaire is designed to assess how mental workload, repeated decisions,
                and everyday academic responsibilities may affect focus, emotional stability, and cognitive energy.
                Please answer carefully and honestly for the most meaningful result.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        <b>Instructions</b><br>
        • Complete all student details before submitting.<br>
        • Read each question carefully.<br>
        • Choose the answer that best reflects your recent experience.<br>
        • No option is selected automatically, so every answer is your own choice.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Student Information")

        given_name = st.text_input("Given Name", value="", placeholder="Enter your given name")
        surname = st.text_input("Surname", value="", placeholder="Enter your surname")

        dob_value = st.date_input(
            "Date of Birth",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY"
        )

        student_id = st.text_input("Student ID (digits only)", value="", placeholder="Enter your student ID")
        gender = st.selectbox("Gender", GENDER_OPTIONS, index=None, placeholder="Select gender")
        year_of_study = st.selectbox("Year of Study", YEAR_OPTIONS, index=None, placeholder="Select year of study")

        average_sleep_raw = st.text_input(
            "Average sleep hours per night",
            value=st.session_state.get("average_sleep_raw", ""),
            placeholder="Example: 6 or 7.5"
        )

        if average_sleep_raw:
            formatted_sleep_text, _, _ = normalize_sleep_hours_text(average_sleep_raw)
            if formatted_sleep_text != average_sleep_raw and formatted_sleep_text != "":
                st.session_state["average_sleep_raw"] = formatted_sleep_text
                st.rerun()
        else:
            st.session_state["average_sleep_raw"] = ""

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Survey Progress")

        answered_count = 0
        for i in range(len(questions)):
            if st.session_state.get(f"question_{i+1}") is not None:
                answered_count += 1

        progress_value = answered_count / len(questions)
        st.markdown('<div class="progress-label">Question completion status</div>', unsafe_allow_html=True)
        st.progress(progress_value)
        st.write(f"**Answered:** {answered_count} of {len(questions)} questions")
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Survey Questions")
        st.markdown(
            '<div class="small-muted">Select one answer for each question. Your progress updates as you go.</div>',
            unsafe_allow_html=True
        )

        selected_answers = []

        for i, question in enumerate(questions, start=1):
            st.markdown('<div class="question-box">', unsafe_allow_html=True)

            current_answer = st.session_state.get(f"question_{i}")
            if current_answer is not None:
                st.markdown(
                    f'<div class="answer-flash">✨ Answer recorded: {current_answer}</div>',
                    unsafe_allow_html=True
                )

            st.markdown(f"**Q{i}. {question['question']}**")

            selected_option = st.radio(
                label=f"Question {i}",
                options=OPTION_TEXTS,
                index=None,
                key=f"question_{i}",
                label_visibility="collapsed"
            )

            selected_answers.append(selected_option)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Submit Survey", use_container_width=True):
            errors = []

            if not validate_name(given_name):
                errors.append("Invalid given name. Use only letters, spaces, hyphens, or apostrophes.")

            if not validate_name(surname):
                errors.append("Invalid surname. Use only letters, spaces, hyphens, or apostrophes.")

            dob_error = validate_dob_value(dob_value)
            if dob_error:
                errors.append(dob_error)

            if not validate_student_id(student_id):
                errors.append("Student ID must contain digits only.")

            if gender is None:
                errors.append("Please select gender.")

            if year_of_study is None:
                errors.append("Please select year of study.")

            _, average_sleep_hours, sleep_error = normalize_sleep_hours_text(
                st.session_state.get("average_sleep_raw", "")
            )
            if sleep_error:
                errors.append(sleep_error)

            if None in selected_answers:
                errors.append("Please answer all questions before submitting the survey.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                total_score = 0
                answer_details = []

                for i, question in enumerate(questions, start=1):
                    selected_option = selected_answers[i - 1]
                    selected_index = OPTION_TEXTS.index(selected_option)
                    score = get_question_score(question["reverse"], selected_index)
                    total_score += score

                    answer_details.append({
                        "question_number": i,
                        "question_text": question["question"],
                        "selected_option": selected_option,
                        "score_awarded": score,
                        "reverse_scored": question["reverse"]
                    })

                average_score = round(total_score / len(questions), 2)
                psychological_state, interpretation = interpret_score(total_score)

                result_data = build_result_record(
                    surname=surname,
                    given_name=given_name,
                    dob_value=dob_value,
                    student_id=student_id,
                    gender=gender,
                    year_of_study=year_of_study,
                    average_sleep_hours=average_sleep_hours,
                    total_score=total_score,
                    average_score=average_score,
                    psychological_state=psychological_state,
                    interpretation=interpretation,
                    answer_details=answer_details
                )

                st.session_state["latest_result"] = result_data
                save_result_history(result_data)

                st.balloons()
                play_success_sound()

                st.success("✅ Survey completed successfully.")
                st.info("This result reflects your current cognitive load based on your responses.")

                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.subheader("Survey Result")
                st.markdown(f'<div class="soft-pill">{psychological_state}</div>', unsafe_allow_html=True)
                st.write(f"**Student:** {given_name} {surname}")
                st.write(f"**Total Score:** {total_score}")
                st.write(f"**Average Score:** {average_score}")
                st.write(f"**Interpretation:** {interpretation}")
                st.markdown('</div>', unsafe_allow_html=True)

                download_format = st.selectbox("Choose download format", ["JSON", "TXT", "CSV"])
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"survey_result_{student_id}_{timestamp}"

                if download_format == "JSON":
                    file_text = convert_result_to_json_text(result_data)
                    file_name = f"{base_filename}.json"
                    mime_type = "application/json"
                elif download_format == "TXT":
                    file_text = convert_result_to_txt_text(result_data)
                    file_name = f"{base_filename}.txt"
                    mime_type = "text/plain"
                else:
                    file_text = convert_result_to_csv_text(result_data)
                    file_name = f"{base_filename}.csv"
                    mime_type = "text/csv"

                st.download_button(
                    label="⬇ Download Result File",
                    data=file_text,
                    file_name=file_name,
                    mime=mime_type,
                    use_container_width=True
                )

    with right_col:
        st.markdown("""
        <div class="fact-card">
            <div class="fact-title">✨ Survey Insights</div>
            <div class="fact-item"><b>Decision fatigue can build quietly.</b><br>It often appears first as hesitation, reduced patience, or avoidance of small tasks.</div>
            <div class="fact-item"><b>Sleep matters more than many people expect.</b><br>Reduced rest can make focus, emotional balance, and decision-making noticeably weaker.</div>
            <div class="fact-item"><b>Small choices also consume mental energy.</b><br>Not only major life decisions, but many repeated daily choices may create overload.</div>
            <div class="fact-item"><b>Honest answers improve interpretation.</b><br>The more realistic the response, the more meaningful the final result becomes.</div>
        </div>
        """, unsafe_allow_html=True)

elif sidebar_mode == "Load Existing Result":
    st.markdown("""
    <div class="hero-box">
        <div style="font-size:1.45rem; font-weight:800; color:#27344c; margin-bottom:0.55rem;">
            View Saved Results
        </div>
        <div style="color:#53627c; line-height:1.7; font-size:1.02rem;">
            You can view your latest result automatically, review all previously saved results, or upload a saved TXT, CSV, or JSON file.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("latest_result") is not None:
        st.success("✅ Latest result loaded automatically.")
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        display_loaded_result(st.session_state["latest_result"], "Latest Result")
        st.markdown('</div>', unsafe_allow_html=True)

    saved_history = load_saved_history()

    if saved_history:
        st.subheader("All Automatically Saved Results")

        result_labels = []
        for index, item in enumerate(saved_history, start=1):
            label = (
                f"{index}. {item.get('given_name', '')} {item.get('surname', '')} | "
                f"{item.get('completion_time', '')} | "
                f"{item.get('psychological_state', '')}"
            )
            result_labels.append(label)

        selected_label = st.selectbox("Choose a saved result to review", result_labels)
        selected_index = result_labels.index(selected_label)
        selected_result = saved_history[selected_index]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        display_loaded_result(selected_result, "Selected Saved Result")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Or upload another result file")

    uploaded_file = st.file_uploader(
        "Upload a saved TXT, CSV, or JSON result file",
        type=["txt", "csv", "json"]
    )

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()

        if suffix == ".json":
            loaded_data, error = parse_uploaded_json(uploaded_file)
        elif suffix == ".txt":
            loaded_data, error = parse_uploaded_txt(uploaded_file)
        elif suffix == ".csv":
            loaded_data, error = parse_uploaded_csv(uploaded_file)
        else:
            loaded_data, error = None, "Unsupported file type."

        if error:
            st.error(error)
        else:
            st.success("📂 Uploaded result loaded successfully.")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            display_loaded_result(loaded_data, "Uploaded Result")
            st.markdown('</div>', unsafe_allow_html=True)