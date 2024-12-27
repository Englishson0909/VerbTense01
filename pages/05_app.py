pip install --upgrade streamlit gradio gTTS pandas
streamlit run 05_app.py

import streamlit as st
import streamlit.components.v1 as components
import gradio as gr
import pandas as pd
import random
import os
import tempfile
from gtts import gTTS

###############################################################################
# (1) 불규칙 동사 처리 로직
###############################################################################
# CSV에서 동사 목록 불러오기
data_url = "https://github.com/Hansukson/Application2/raw/main/irregular_verbs%20(1).csv"
verbs_df = pd.read_csv(data_url)
verbs_data = verbs_df.set_index("present")[['past', 'p.p']].to_dict(orient="index")

# 정오답 시 피드백 문구
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

wrong_feedback = [
    "Wrong! Nice try, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Almost there, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Don’t give up, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Good effort, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Mistakes happen, {name}. The correct forms are: {correct_past}, {correct_pp}."
]

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

# 세트 및 전역 상태
max_sets = 10
limit_per_set = 10

set_number = 1
attempt_in_set = 0
already_submitted = False
attempt_count = 0
correct_count = 0
current_verb = ""

# 음성 TTS 파일 생성
def tts_play(verb_forms):
    tts_text = f"{verb_forms[0]}, {verb_forms[1]}, {verb_forms[2]}"
    temp_audio_file = os.path.join(tempfile.gettempdir(), "verb_audio.mp3")
    tts = gTTS(tts_text)
    tts.save(temp_audio_file)
    return temp_audio_file

# 진행 상황 표시 함수
def explain_sets():
    tries_left_in_set = limit_per_set - attempt_in_set
    return (
        f"We have a total of {max_sets} sets, each set has {limit_per_set} tries.\n"
        f"**You are now on set {set_number}/{max_sets}.**\n"
        f"You have **{tries_left_in_set} tries left** in this set."
    )

# START 버튼 눌렀을 때 호출
def start_game(name):
    if not name.strip():
        return "Please enter your name to proceed!", gr.update(visible=False), ""
    msg = (
        f"Welcome, {name}! Click 'SHOW ME A VERB' to begin.\n\n" 
        + explain_sets()
    )
    return msg, gr.update(visible=True), ""

# 동사 보여주기
def show_random_verb():
    global current_verb, already_submitted
    current_verb = random.choice(list(verbs_data.keys()))
    already_submitted = False
    return current_verb

# 사용자가 past, p.p 입력 후 SUBMIT했을 때
def check_answer(name, user_past, user_pp):
    global correct_count, attempt_count, current_verb
    global set_number, attempt_in_set, already_submitted

    # 아직 제출 안 했다면 제출 처리
    if not already_submitted:
        attempt_count += 1
        attempt_in_set += 1
        already_submitted = True

    correct_past_str = verbs_data[current_verb]['past'].strip().lower()
    correct_pp_str = verbs_data[current_verb]['p.p'].strip().lower()
    correct_pp_list = [pp.strip() for pp in correct_pp_str.split('/')]

    upast = user_past.strip().lower()
    upp = user_pp.strip().lower()

    audio_file = tts_play([current_verb, correct_past_str, correct_pp_str])

    # 정답/오답 체크
    if upast == correct_past_str and upp in correct_pp_list:
        correct_count += 1
        feedback = random.choice(correct_feedback).format(name=name)
    else:
        feedback = random.choice(wrong_feedback).format(
            name=name,
            correct_past=correct_past_str,
            correct_pp=correct_pp_str
        )

    percentage = (correct_count / attempt_count * 100) if attempt_count else 0
    score_str = f"Your Score: {correct_count} / {attempt_count} ({percentage:.1f}%)"
    recheck_msg = f"{current_verb} {correct_past_str} {correct_pp_str}"

    # 세트 진행도
    if attempt_in_set >= limit_per_set:
        # 세트 종료 시점
        if set_number < max_sets:
            # 다음 세트로 이동 가능
            return (
                feedback,
                gr.update(value=recheck_msg, visible=True),
                score_str,
                audio_file,
                gr.update(visible=False),  # audio_button
                gr.update(visible=False),  # continue_button
                gr.update(visible=True),   # one_more_set_button
                explain_sets()
            )
        else:
            # 마지막 세트까지 끝
            return (
                feedback,
                gr.update(value=recheck_msg, visible=True),
                score_str,
                audio_file,
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                "**You have finished the 10th (final) set.**\n\n" + explain_sets()
            )
    else:
        # 아직 세트 진행 중
        return (
            feedback,
            gr.update(value=recheck_msg, visible=True),
            score_str,
            audio_file,
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            explain_sets()
        )

# Continue 버튼 클릭 시 필드 초기화
def reset_inputs():
    return "", "", "", ""

# Try One More Set 버튼 클릭 시 다음 세트
def try_one_more_set():
    global set_number, attempt_in_set, already_submitted
    set_number += 1
    attempt_in_set = 0
    already_submitted = False
    msg = f"**Now starting set {set_number}.**\n" + explain_sets()
    return msg, gr.update(visible=True), gr.update(visible=False)

# End 버튼 클릭 시 마지막 격려
def final_feedback(name):
    return f"### THE END\n\n{random.choice(final_encouragement).format(name=name)}"


###############################################################################
# (2) Gradio 인터페이스 생성 함수
###############################################################################
def create_gradio_app():
    with gr.Blocks() as app:
        # 제목/소개
        gr.Markdown("# VerbMaster: Learn Irregular Verbs! 🎯")
        gr.Markdown("This app will help you learn irregular verbs. We have **10 sets** total, each set has **10 tries**.")

        # 이름 입력 + START
        name_input = gr.Textbox(label="Your Name", placeholder="Enter your name here")
        start_button = gr.Button("START")

        welcome_output = gr.Markdown()
        show_verb_button = gr.Button("SHOW ME A VERB", visible=False)
        status_output = gr.Markdown()

        # 동사 및 입력 폼
        present_verb_output = gr.Textbox(label="Present Verb", interactive=False)
        user_past_input = gr.Textbox(label="Enter Past Form")
        user_pp_input = gr.Textbox(label="Enter Past Participle")
        submit_button = gr.Button("SUBMIT", visible=False)

        # 피드백 및 점수
        feedback_output = gr.Textbox(label="Feedback", interactive=False)
        recheck_output = gr.Textbox(label="Recheck", interactive=False, visible=False)
        score_output = gr.Textbox(label="Score", interactive=False)

        # 오디오 재생
        audio_button = gr.Button("NOT SURE HOW TO SAY IT? HEAR IT HERE!", visible=False)
        tts_output = gr.Audio(label="Audio Feedback", visible=False)

        # 진행 제어 버튼
        continue_button = gr.Button("IF YOU WANT TO CONTINUE, CLICK HERE!", visible=False)
        one_more_set_button = gr.Button("TRY ONE MORE SET", visible=False)
        end_button = gr.Button("IF YOU WANT TO END THIS APP, CLICK HERE!")
        final_feedback_output = gr.Markdown(visible=False)

        # --- 이벤트 연결 ---
        start_button.click(
            fn=start_game,
            inputs=name_input,
            outputs=[welcome_output, show_verb_button, status_output]
        )

        show_verb_button.click(
            fn=show_random_verb,
            outputs=present_verb_output
        )

        user_pp_input.change(
            fn=lambda val: gr.update(visible=True) if val.strip() else gr.update(visible=False),
            inputs=user_pp_input,
            outputs=submit_button
        )

        submit_button.click(
            fn=check_answer,
            inputs=[name_input, user_past_input, user_pp_input],
            outputs=[
                feedback_output,
                recheck_output,
                score_output,
                tts_output,
                audio_button,
                continue_button,
                one_more_set_button,
                status_output
            ]
        )

        audio_button.click(
            fn=lambda: gr.update(visible=True),
            outputs=tts_output
        )

        continue_button.click(
            fn=reset_inputs,
            outputs=[user_past_input, user_pp_input, feedback_output, recheck_output]
        )
        continue_button.click(
            fn=show_random_verb,
            outputs=present_verb_output
        )
        continue_button.click(
            fn=lambda: explain_sets(),
            outputs=status_output
        )

        one_more_set_button.click(
            fn=try_one_more_set,
            outputs=[welcome_output, show_verb_button, one_more_set_button]
        )

        end_button.click(
            fn=final_feedback,
            inputs=name_input,
            outputs=final_feedback_output
        )
        end_button.click(
            fn=lambda: gr.update(visible=True),
            outputs=final_feedback_output
        )

    return app


###############################################################################
# (3) Streamlit 내에 Gradio 임베드
###############################################################################
# Streamlit 페이지 설정
st.set_page_config(page_title="Irregular Verb Practice", layout="wide")
st.title("Irregular Verb Practice in Streamlit + Gradio")
st.write("Below is the embedded Gradio interface:")

# Gradio 앱 생성 (Blocks 반환)
demo = create_gradio_app()

# launch()로 HTML을 반환받아 임베드 (fallback 방식)
# inline=True : HTML 문자열로 반환 / prevent_thread_lock=True : Streamlit과의 충돌 방지
app_html = demo.launch(
    inline=True,
    prevent_thread_lock=True,
    inbrowser=False,
    show_error=True
)

# Streamlit에 해당 HTML 삽입
components.html(
    app_html,
    height=2200,          # 필요에 따라 조절 가능
    scrolling=True,
    unsafe_allow_html=True # iframe 등을 허용하기 위해 필요
)
