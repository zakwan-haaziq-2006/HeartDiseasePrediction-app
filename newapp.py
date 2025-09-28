import streamlit as st
import time
import numpy as np
import pickle
import random

# ---------------- Conversion Functions ----------------
def converting_chestpain_type(chestPain, chestpain_while_working, pain_reduce_after_rest, pain_Feel):
    """Convert chest pain description into numeric category."""
    pain = {'ASY': 0, 'ATA': 1, 'NAP': 2, 'TA': 3}
    if chestPain:
        if chestpain_while_working:
            if pain_reduce_after_rest:
                return pain['TA']
            else:
                return pain['ATA']
        else:
            return pain['NAP'] if pain_Feel else pain['ATA']
    return pain['ASY']

def Fasting_bs(thirsty, urine):
    return 1 if thirsty or urine else 0

def RestingECG(heartBeat):
    return 1 if heartBeat else 0

def to_bool(answer):
    return str(answer).strip().lower() in ["yes", "y", "true", "sure"]

# ---------------- UI Setup ----------------
st.set_page_config("MediBot", page_icon="🧑‍⚕️")
st.markdown("""
    <h1 style='text-align: center; color: white;'>🧑‍⚕️ MediBot</h1>
    <p style='text-align: center; color: #AAAAAA;'>Your Personal Health Assistant</p>
""", unsafe_allow_html=True)

# CSS for chat bubbles
st.markdown("""
    <style>
    .chat-container { display: flex; flex-direction: column; width: 100%; }
    .user-row { display: flex; justify-content: flex-end; margin: 10px 0; }
    .bot-row { display: flex; justify-content: flex-start; margin: 10px 0; }
    .user-bubble, .bot-bubble {
        padding: 10px 15px; border-radius: 15px; max-width: 60%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3); text-align: left;
    }
    .user-bubble { background-color: #2e3b4e; color: white; }
    .bot-bubble { background-color: #3c3c3c; color: white; }
    textarea { background-color: #1e1e1e !important; color: white !important; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Typewriter Animation ----------------
def typewriter(text):
    typed = ""
    placeholder = st.empty()
    for char in text:
        typed += char
        placeholder.markdown(f'''
            <div class="bot-row"><div class="bot-bubble">{typed}</div></div>
        ''', unsafe_allow_html=True)
        time.sleep(0.02)
    st.session_state.chat_history.append(("bot", text))

# ---------------- Questions ----------------
sections = [
    ("chest_pain", [
        {"key": "chestPain", "text": "Do you have chest pain? (yes/no)", "type": "bool"},
        {"key": "chestpain_while_working", "text": "Does it occur while working? (yes/no)", "type": "bool"},
        {"key": "pain_reduce_after_rest", "text": "Does the pain reduce after rest? (yes/no)", "type": "bool"},
        {"key": "pain_Feel", "text": "Is it a sharp pain? (yes for sharp / no for dull)", "type": "bool"}
    ]),
    ("vitals", [
        {"key": "age", "text": "What is your age?", "type": "numeric"},
        {"key": "gender", "text": "What is your gender? (Male/Female)", "type": "text"},
        {"key": "restingBP", "text": "What is your resting blood pressure?", "type": "numeric"},
        {"key": "cholesterol", "text": "What is your cholesterol level?", "type": "numeric"}
    ]),
    ("fasting_bs", [
        {"key": "thirsty", "text": "Do you feel unusually thirsty? (yes/no)", "type": "bool"},
        {"key": "urine", "text": "Do you urinate frequently? (yes/no)", "type": "bool"}
    ]),
    ("ecg_exercise", [
        {"key": "heartBeat", "text": "Is your heartbeat irregular? (yes/no)", "type": "bool"},
        {"key": "exercise", "text": "Do you feel discomfort during exercise? (yes/no)", "type": "bool"}
    ])
]

# ---------------- State Initialization ----------------
if "section_index" not in st.session_state:
    st.session_state.section_index = -1
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "animated_keys" not in st.session_state:
    st.session_state.animated_keys = set()
if "greeted" not in st.session_state:
    st.session_state.greeted = False
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False
if "final_input" not in st.session_state:
    st.session_state.final_input = []

# ---------------- Render Chat History ----------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for role, msg in st.session_state.chat_history:
    row_class = "user-row" if role == "user" else "bot-row"
    bubble_class = "user-bubble" if role == "user" else "bot-bubble"
    st.markdown(f'''
        <div class="{row_class}"><div class="{bubble_class}">{msg}</div></div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Greeting Phase ----------------
if st.session_state.section_index == -1 and not st.session_state.greeted:
    typewriter("👋 Hi there! I'm MediBot, your personal health consultant 🤖.")
    typewriter("We'll work together to understand your symptoms and guide you toward the right care 🩺.")
    typewriter("Just answer a few simple questions 🙏.")
    typewriter("Would you like to continue?")
    st.session_state.greeted = True

# ---------------- Consent Check ----------------
if st.session_state.section_index == -1 and not st.session_state.consent_given:
    user_input = st.chat_input("Type 'yes' to continue or 'no' to exit")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        if to_bool(user_input):
            typewriter("🙌 Great! Let's get started...")
            st.session_state.consent_given = True
            st.session_state.section_index = 0
            st.rerun()
        else:
            typewriter("👋 No worries! Take care, and come back anytime.")
            st.stop()

# ---------------- Question Loop ----------------
elif st.session_state.section_index < len(sections):
    section_name, questions = sections[st.session_state.section_index]
    if st.session_state.step < len(questions):
        q = questions[st.session_state.step]
        if q["key"] not in st.session_state.animated_keys:
            typewriter(q["text"])
            st.session_state.animated_keys.add(q["key"])

        user_input = st.chat_input("Your answer")
        if user_input:
            st.session_state.chat_history.append(("user", user_input))
            if q["type"] == "bool":
                st.session_state.answers[q["key"]] = to_bool(user_input)
            elif q["type"] == "numeric":
                try:
                    st.session_state.answers[q["key"]] = float(user_input)
                except ValueError:
                    st.warning("⚠️ Please enter a valid number.")
                    st.stop()
            else:
                st.session_state.answers[q["key"]] = user_input.strip()

            st.session_state.step += 1
            st.rerun()
    else:
        st.session_state.section_index += 1
        st.session_state.step = 0
        st.rerun()

# ---------------- Final Conversion & Prediction ----------------
elif st.session_state.section_index >= len(sections):
    a = st.session_state.answers
    
    chestpain_val = converting_chestpain_type(
        a["chestPain"], a["chestpain_while_working"], 
        a["pain_reduce_after_rest"], a["pain_Feel"]
    )
    fasting_val = Fasting_bs(a["thirsty"], a["urine"])
    ecg_val = RestingECG(a["heartBeat"])
    maxHR = 220 - int(a["age"])   # ✅ auto-calculate

    # ✅ Random values for oldpeak and ST slope
    oldpeak = round(random.uniform(0.0, 6.0), 1)
    st_slope = random.choice([0, 1, 2])

    st.session_state.final_input = [
        int(a["age"]),
        0 if a["gender"].lower() == "female" else 1,
        chestpain_val,
        int(a["restingBP"]),
        int(a["cholesterol"]),
        fasting_val,
        ecg_val,
        maxHR,
        1 if a["exercise"] else 0,
        oldpeak,
        st_slope
    ]
    
    features = np.array(st.session_state.final_input).reshape(1, -1)
    
    typewriter("✅ Thank you for answering all the questions!")
    st.success("Final Input Vector (ML-ready):")
    st.write(features)
    
    # --------- Load Model & Predict ---------
    try:
        with open("Model.pkl", "rb") as f:
            model = pickle.load(f)
        prediction = model.predict(features)

        if prediction[0] == 0:
            st.success("🟢 No heart disease detected. You are healthy! 🎉")
            typewriter("💚 Great news! No signs of heart disease were detected.")
        else:
            st.error("🔴 You might have heart disease. Please consult a doctor immediately. 🩺")
            typewriter("⚠️ Based on your inputs, you might have heart disease. I strongly recommend consulting a doctor.")
            
    except FileNotFoundError:
        st.error("⚠️ Model.pkl not found. Please train and save the model first.")
    except Exception as e:
        st.error(f"⚠️ Model error: {e}")

    # Restart option
    if st.button("🔄 Start Again"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
