import streamlit as st
import pandas as pd
import random
import io
from gtts import gTTS

# Load the irregular verbs data
data_url = "https://github.com/Hansukson/Application2/raw/main/irregular_verbs%20(1).csv"
verbs_df = pd.read_csv(data_url)

# Extract verbs data into a dictionary
verbs_data = verbs_df.set_index("present")[['past', 'p.p']].to_dict(orient="index")

# Correct Feedback List
correct_feedback = [
    "Correct! Fantastic job, {name}!",
    "Correct! Excellent work, {name}!",
    "Correct! You're doing great, {name}!",
    "Correct! Keep it up, {name} – you're unstoppable!",
    "Correct! Outstanding effort, {name}!",
    "Correct! Brilliant work, {name} – you nailed it!",
    "Correct! Amazing job, {name}! Keep shining!",
    "Correct! You're crushing it, {name}! Well done!",
    "Correct! Superb, {name}! You’re on fire!",
    "Correct! Perfect answer, {name}! Keep going strong!"
]

# Wrong Feedback List
wrong_feedback = [
    "Wrong! Nice try, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Almost there, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Don’t give up, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Good effort, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Mistakes happen, {name}. The correct forms are: {correct_past}, {correct_pp}.",
]

# Final Encouragement
final_encouragement = [
    "You’ve done so well today, {name}. I can truly see your effort. Keep learning and growing!",
    "I’m really proud of you, {name}. You’re moving forward step by step, and that’s what matters.",
    "You’ve made real progress, {name}! Remember, every new word is a step towards confidence.",
    "That was great work, {name}! Don’t forget how far you’ve come. Keep believing in yourself!",
    "Look at how much you’ve learned, {name}! I’m cheering you on every step of the way.",
    "Your dedication shows, {name}. Keep this up, and you’ll be amazed at your own growth.",
    "It’s wonderful to see you improve, {name}. Keep your spirits high and keep going!",
    "You’re getting stronger with every try, {name}. Your hard work is truly inspiring!",
    "Your commitment is shining through, {name}. Just keep at it, and you’ll do even better!",
    "I know it’s not always easy, {name}, but your progress is real. Stay motivated and keep pushing forward!"
]

def tts_play(verb_forms):
    tts_text = f"{verb_forms[0]}, {verb_forms[1]}, {verb_forms[2]}"
    tts = gTTS(tts_text)
    bytes_io = io.BytesIO()
    tts.write_to_fp(bytes_io)
    bytes_io.seek(0)
    return bytes_io

# Session state 초기화
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'current_verb' not in st.session_state:
    st.session_state.current_verb = ""
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'attempt_count' not in st.session_state:
    st.session_state.attempt_count = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'final_stage' not in st.session_state:
    st.session_state.final_stage = False

st.title("VerbMaster: Learn Irregular Verbs! 🎯")
st.write("This app will help you learn irregular verbs.")

# 게임 시작 전 이름 입력
if not st.session_state.game_started and not st.session_state.final_stage:
    st.session_state.name = st.text_input("Your Name", value=st.session_state.name)
    if st.button("START"):
        if st.session_state.name.strip() == "":
            st.warning("Please enter your name to proceed!")
        else:
            st.session_state.game_started = True
            st.success(f"Welcome, {st.session_state.name}! Click 'SHOW ME A VERB' to begin.")

# 동사 보여주기
if st.session_state.game_started and not st.session_state.final_stage:
    if st.button("SHOW ME A VERB"):
        st.session_state.current_verb = random.choice(list(verbs_data.keys()))

    if st.session_state.current_verb:
        st.write("Present Verb:", st.session_state.current_verb)
        user_past = st.text_input("Enter Past Form", key='user_past')
        user_pp = st.text_input("Enter Past Participle", key='user_pp')

        if st.button("SUBMIT"):
            st.session_state.attempt_count += 1
            correct_past_str = verbs_data[st.session_state.current_verb]['past'].strip().lower()
            correct_pp_str = verbs_data[st.session_state.current_verb]['p.p'].strip().lower()
            correct_pp_list = [pp.strip() for pp in correct_pp_str.split('/')]

            upast = user_past.strip().lower()
            upp = user_pp.strip().lower()

            audio_bytes = tts_play([st.session_state.current_verb, correct_past_str, correct_pp_str])

            if upast == correct_past_str and upp in correct_pp_list:
                st.session_state.correct_count += 1
                feedback = random.choice(correct_feedback).format(name=st.session_state.name)
            else:
                feedback = random.choice(wrong_feedback).format(
                    name=st.session_state.name,
                    correct_past=correct_past_str,
                    correct_pp=correct_pp_str
                )

            score = f"Your Score: {st.session_state.correct_count} / {st.session_state.attempt_count}"

            st.write("Feedback:", feedback)
            st.write("Recheck:", f"{st.session_state.current_verb} {correct_past_str} {correct_pp_str}")
            st.write(score)
            st.audio(audio_bytes, format='audio/mp3')

            # 계속하기 및 끝내기
            col1, col2 = st.columns(2)
            with col1:
                if st.button("IF YOU WANT TO CONTINUE, CLICK HERE!"):
                    # 다음 동사 준비
                    st.session_state.user_past = ""
                    st.session_state.user_pp = ""
                    st.session_state.current_verb = ""
                    st.experimental_rerun()

            with col2:
                if st.button("IF YOU WANT TO END THIS APP, CLICK HERE!"):
                    st.session_state.final_stage = True
                    st.experimental_rerun()

# 게임 종료 후 메시지
if st.session_state.final_stage:
    st.markdown("### THE END")
    st.markdown(random.choice(final_encouragement).format(name=st.session_state.name))

