import streamlit as st
import streamlit.components.v1 as components
import random
import os

# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="Final Exam Simulator", layout="centered")

# --- 2. CHECK FOR "STUDENT MODE" URL PARAMETER ---
params = st.query_params
shared_exam = params.get("exam")

# Inject clean custom CSS 
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    /* FORCE GLOBAL DARK MODE FOR ALL USERS */
    .stApp, .stApp > header {
        background-color: #0e1117 !important;
        color: #fafafa !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    html, body, [class*="css"], .stMarkdown p, .stButton button {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* COMPACT MAIN TITLE */
    h1 {
        font-size: 22px !important; 
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
    }
    
    /* GOLDEN RATIO TYPOGRAPHY */
    .stMarkdown p {
        font-size: 16px !important;
    }
    h4 {
        font-size: 20px !important; 
        line-height: 1.5 !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* LEFT-ALIGNMENT FOR CLOUD BUTTONS */
    .stButton > button {
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        padding: 10px 15px !important;
        font-weight: 500 !important;
    }
    .stButton > button * {
        text-align: left !important;
        width: 100% !important;
        margin: 0 !important;
    }
    
    /* PERFECT PURE WHITE SLIDER */
    .stSlider [data-baseweb="slider"] {
        padding-top: 15px !important;
    }
    .stSlider [role="slider"] {
        background-color: #ffffff !important;
        border-color: #ffffff !important;
        box-shadow: none !important;
    }
    .stSlider [data-baseweb="slider"] > div:first-child > div:nth-child(2) {
        background-color: #ffffff !important;
    }
    .stSlider [data-baseweb="slider"] > div:first-child > div:first-child {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    .stSlider [data-testid="stThumbValue"] {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* FORCE MOBILE COLUMNS SIDE-BY-SIDE */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 15px !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        width: 50% !important;
        min-width: 50% !important;
    }
    
    /* STICKY TOOLBELT & HIDE STREAMLIT/GITHUB UI */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important; 
    }
    .viewerBadge_container, .viewerBadge_link {
        display: none !important; 
    }
    footer {
        display: none !important; 
    }
    
    .block-container {
        padding-top: 2rem !important;
    }
    /* Targets ONLY the 2nd block (The Toolbelt) to be sticky */
    div[data-testid="stVerticalBlock"] > div:nth-of-type(2) {
        position: sticky !important;
        top: 0px !important;
        z-index: 999 !important;
        background-color: #0e1117 !important;
        padding: 10px 0px 5px 0px !important;
        border-bottom: 1px solid #333 !important;
    }
    </style>
""", unsafe_allow_html=True)

if shared_exam:
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. THE JAVASCRIPT TIMER ---
def render_timer():
    timer_html = """
    <div id="timerContainer" style="display: flex; justify-content: space-between; align-items: center; background-color: #1e1e1e; padding: 6px 15px; border-radius: 6px; border: 1px solid #333; font-family: 'Inter', sans-serif; color: white; margin: 0;">
        <div style="font-size: 12px; font-weight: 600; color: #888; letter-spacing: 1px;">TIME REMAINING</div>
        <div id="timerDisplay" style="font-size: 18px; font-weight: bold; font-variant-numeric: tabular-nums;">120:00</div>
        <button onclick="togglePause()" id="pauseBtn" style="background-color: #333; color: white; border: 1px solid #555; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 500;">Pause</button>
    </div>

    <script>
        let totalSeconds = sessionStorage.getItem('examTimer') ? parseInt(sessionStorage.getItem('examTimer')) : 7200;
        let isPaused = sessionStorage.getItem('examPaused') === 'true';

        function updateTimer() {
            if(!isPaused && totalSeconds > 0) {
                totalSeconds--;
                sessionStorage.setItem('examTimer', totalSeconds);
            }
            
            let hours = Math.floor(totalSeconds / 3600);
            let mins = Math.floor((totalSeconds % 3600) / 60);
            let secs = totalSeconds % 60;
            
            let minStr = mins < 10 ? '0' + mins : mins;
            let secStr = secs < 10 ? '0' + secs : secs;
            document.getElementById('timerDisplay').innerText = (hours > 0 ? hours + ':' : '') + minStr + ':' + secStr;
            document.getElementById('pauseBtn').innerText = isPaused ? "Resume" : "Pause";

            let display = document.getElementById('timerDisplay');
            if (totalSeconds > 3600) display.style.color = '#28a745';
            else if (totalSeconds > 900) display.style.color = '#ffc107';
            else display.style.color = '#dc3545';
        }

        function togglePause() {
            isPaused = !isPaused;
            sessionStorage.setItem('examPaused', isPaused);
            updateTimer();
        }

        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
    """
    components.html(timer_html, height=50)

# --- 4. PARSE THE TEXT FILE ---
def load_curriculum(filepath):
    questions = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        current_q = None
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("### Question"):
                if current_q:
                    current_q['options'] = options
                    questions.append(current_q)
                # Added 'bundle' to the dictionary
                current_q = {'question': '', 'answer': '', 'image': None, 'bundle': None}
                options = []
            elif line.startswith("IMAGE:"):
                current_q['image'] = line.split("IMAGE:")[1].strip()
            elif line.startswith("BUNDLE:"):
                # Extract the bundle identifier
                current_q['bundle'] = line.split("BUNDLE:")[1].strip()
            elif line.startswith("A)") or line.startswith("B)") or line.startswith("C)") or line.startswith("D)"):
                options.append(line)
            elif line.startswith("Answer:"):
                current_q['answer'] = line.split("Answer:")[1].strip()
            elif current_q is not None and not current_q['question'] and not line.startswith("IMAGE:") and not line.startswith("BUNDLE:"):
                current_q['question'] = line.replace('### ', '')
                
        if current_q:
            current_q['options'] = options
            questions.append(current_q)
            
    except FileNotFoundError:
        st.error(f"Error: Could not find '{filepath}'.")
        
    return questions

# --- 5. FIND ALL TEXT FILES & ROUTE THE USER ---
txt_files = [f for f in os.listdir('.') if f.endswith('.txt') and f != 'requirements.txt']

if not txt_files:
    st.error("No text files found! Please add your exam .txt files to this folder.")
    st.stop()

if shared_exam:
    target_file = f"{shared_exam}.txt"
    if target_file in txt_files:
        selected_file = target_file
    else:
        st.error(f"Exam '{shared_exam}' not found. Please check the link.")
        st.stop()
else:
    st.sidebar.title("Exam Settings")
    selected_file = st.sidebar.selectbox("📚 Select Subject:", txt_files)
# --- 6. MANAGE THE EXAM STATE & SHUFFLE ---
if 'current_file' not in st.session_state or st.session_state.current_file != selected_file:
    st.session_state.current_file = selected_file
    raw_data = load_curriculum(selected_file)
    
    if raw_data:
        grouped_data = {}
        single_questions = []
        
        # 1. Sort questions into bundles or single items
        for q in raw_data:
            if q.get('bundle'):
                b_id = q['bundle']
                if b_id not in grouped_data:
                    grouped_data[b_id] = []
                grouped_data[b_id].append(q)
            else:
                single_questions.append([q]) # Store single questions as lists of 1
                
        # 2. Combine bundles and single questions into a list of blocks
        all_blocks = list(grouped_data.values()) + single_questions
        
        # 3. Shuffle the blocks
        random.shuffle(all_blocks)
        
        # 4. Flatten the blocks back into a single 1D list
        final_exam_data = [q for block in all_blocks for q in block]
    else:
        final_exam_data = []

    st.session_state.exam_data = final_exam_data
    st.session_state.user_answers = {} 
    st.session_state.current_index = 0
    st.session_state.exam_finished = False
    components.html("<script>sessionStorage.removeItem('examTimer'); sessionStorage.removeItem('examPaused');</script>", height=0)

# Initialize finished state if not present
if 'exam_finished' not in st.session_state:
    st.session_state.exam_finished = False

# --- 7. BUILD THE USER INTERFACE ---
exam_title = selected_file.replace('.txt', '').replace('_', ' ')
st.title(exam_title) 

if not st.session_state.exam_data:
    st.warning("No questions loaded. Please check your text formatting.")
elif st.session_state.exam_finished:
    # --- 8. THE RESULTS DASHBOARD ---
    st.container() # Dummy container to safely absorb the "sticky" CSS rule
    
    correct_count = sum(1 for idx, ans in st.session_state.user_answers.items() if ans.startswith(st.session_state.exam_data[idx]['answer']))
    incorrect_count = len(st.session_state.user_answers) - correct_count
    total_q = len(st.session_state.exam_data)
    unanswered_count = total_q - (correct_count + incorrect_count)
    percentage = (correct_count / total_q) * 100 if total_q > 0 else 0
    
    color = "#28a745" if percentage >= 60 else "#dc3545" # Green if passed, red if failed
    
    st.markdown(f"""
    <div style='text-align: center; padding: 30px 20px; background-color: #1e1e1e; border-radius: 12px; border: 1px solid #333; margin-top: 20px; margin-bottom: 30px;'>
        <h2 style='color: #fafafa; margin-bottom: 10px; font-weight: 500;'>Exam Complete</h2>
        <h1 style='color: {color}; font-size: 56px; font-weight: 600; margin: 0;'>{percentage:.1f}%</h1>
        <p style='color: #888; font-size: 16px; margin-top: 5px; margin-bottom: 25px;'>Final Score</p>
        <div style='display: flex; justify-content: space-around; font-size: 16px; border-top: 1px solid #333; padding-top: 25px;'>
            <div style='color: #28a745;'>✅ Correct<br><b style='font-size: 22px;'>{correct_count}</b></div>
            <div style='color: #dc3545;'>❌ Incorrect<br><b style='font-size: 22px;'>{incorrect_count}</b></div>
            <div style='color: #888;'>⚪ Skipped<br><b style='font-size: 22px;'>{unanswered_count}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Restart Exam", use_container_width=True):
        st.session_state.clear()
        components.html("<script>sessionStorage.removeItem('examTimer'); sessionStorage.removeItem('examPaused');</script>", height=0)
        st.rerun()

else:
    # --- 9. THE ACTIVE EXAM UI ---
    correct_count = sum(1 for idx, ans in st.session_state.user_answers.items() if ans.startswith(st.session_state.exam_data[idx]['answer']))
    incorrect_count = len(st.session_state.user_answers) - correct_count
    remaining = len(st.session_state.exam_data) - len(st.session_state.user_answers)

    # === THE STICKY TOOLBELT ===
    toolbelt = st.container()
    with toolbelt:
        st.markdown(f"""
        <div style='display: flex; justify-content: space-around; background-color: #1e1e1e; padding: 10px; border-radius: 6px; border: 1px solid #333; margin-bottom: 10px; font-size: 14px; font-weight: 500;'>
            <span style='color: #28a745;'>✅ Correct: <b>{correct_count}</b></span>
            <span style='color: #dc3545;'>❌ Incorrect: <b>{incorrect_count}</b></span>
            <span style='color: #fff;'>📝 Remaining: <b>{remaining}</b></span>
        </div>
        """, unsafe_allow_html=True)
        render_timer()
   
        
    # === THE SLIDER (Moved outside the toolbelt so it scrolls away!) ===
    current_q_num = st.session_state.current_index + 1
    new_q_num = st.slider("Navigate Questions", min_value=1, max_value=len(st.session_state.exam_data), value=current_q_num, label_visibility="collapsed")
    
    if new_q_num != current_q_num:
        st.session_state.current_index = new_q_num - 1
        st.rerun()

# === THE QUESTION FRAME ===
    q_data = st.session_state.exam_data[st.session_state.current_index]
    
    st.markdown(f"#### {st.session_state.current_index + 1}. {q_data['question']}")
    
    # Check if there is an image and render it
    if q_data.get('image'):
        try:
            # Use columns to create invisible bumpers, shrinking and centering the image
            spacer_left, img_col, spacer_right = st.columns([1, 2, 1])
            with img_col:
                st.image(q_data['image'], use_container_width=True) 
        except Exception as e:
            st.error(f"⚠️ Could not load image: {q_data['image']}")
    
    has_answered_current = st.session_state.current_index in st.session_state.user_answers
    
    if not has_answered_current:
        for opt in q_data['options']:
            parts = opt.split(') ', 1)
            if len(parts) == 2:
                display_label = f":gray[{parts[0]})] {parts[1]}"
            else:
                display_label = opt
                
            if st.button(display_label, use_container_width=True, key=f"btn_{st.session_state.current_index}_{opt}"):
                st.session_state.user_answers[st.session_state.current_index] = opt
                st.rerun()
    else:
        selected_option = st.session_state.user_answers[st.session_state.current_index]
        for opt in q_data['options']:
            is_correct_answer = opt.startswith(q_data['answer'])
            is_user_choice = (opt == selected_option)
            
            parts = opt.split(') ', 1)
            if len(parts) == 2:
                html_opt = f"<span style='opacity: 0.4; font-weight: 400; margin-right: 6px;'>{parts[0]})</span>{parts[1]}"
            else:
                html_opt = opt
            
            if is_correct_answer:
                bg_color = "rgba(40, 167, 69, 0.2)"
                border_color = "rgba(40, 167, 69, 0.8)"
            elif is_user_choice and not is_correct_answer:
                bg_color = "rgba(220, 53, 69, 0.2)"
                border_color = "rgba(220, 53, 69, 0.8)"
            else:
                bg_color = "transparent"
                border_color = "rgba(250, 250, 250, 0.2)"
                
            st.markdown(f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 10px 15px; margin-bottom: 15px; font-size: 16px; text-align: left; font-weight: 500;">
                {html_opt}
            </div>
            """, unsafe_allow_html=True)
                
    st.write("---")
    
    nav_col1, nav_col2 = st.columns(2)
    
    with nav_col1:
        if st.button("⬅️ Back", use_container_width=True, disabled=(st.session_state.current_index == 0)):
            st.session_state.current_index -= 1
            st.rerun()
            
    with nav_col2:
        is_last = st.session_state.current_index == len(st.session_state.exam_data) - 1
        btn_text = "Finish Exam 🏁" if is_last else "Next ➡️"
        
        if st.button(btn_text, use_container_width=True):
            if not is_last:
                st.session_state.current_index += 1
                st.rerun()
            else:
                # Trigger the Results Dashboard instead of wiping the app
                st.session_state.exam_finished = True
                st.rerun()
