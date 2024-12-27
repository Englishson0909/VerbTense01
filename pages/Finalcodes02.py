import streamlit as st
import gradio as gr
import pandas as pd
import random
import os
import tempfile
from gtts import gTTS

# ----- 데이터 불러오기 -----
data_url = "https://github.com/Hansukson/Application2/raw/main/irregular_verbs%20(1).csv"
verbs_df = pd.read_csv(data_url)
verbs_data = verbs_df.set_index("present")[['past', 'p.p']].to_dict(orient="index")

# ----- 피드백 문구들 -----
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

# ----- 전역 상태 -----
max_sets = 10
limit_per_set = 10

set_number = 1
attempt_in_set = 0
already_submitted = False

attempt_count = 0   
correct_count = 0   
current_verb = ""

def tts_play(verb_forms):
    tts_text = f"{verb_forms[0]}, {verb_forms[1]}, {verb_forms[2]}"
    temp_audio_file = os.path.join(tempfile.gettempdir(), "verb_audio.mp3")
    tts = gTTS(tts_text)
    tts.save(temp_audio_file)
    return temp_audio_file

def explain_sets():
    tries_left_in_set = limit_per_set - attempt_in_set
    return (
        f"We have a total of {max_sets} sets, each set has {limit_per_set} tries.\n"
        f"**You are now on set {set_number}/{max_sets}.**\n"
        f"You have **{tries_left_in_set} tries left** in this set."
    )

def start_game(name):
    """START 버튼 클릭 시: 이름 확인 후, 환영 메시지 + Show me a verb 버튼 표시"""
    if name.strip() == "":
        return "Please enter your name to proceed!", gr.update(visible=False), ""
    msg = (
        f"Welcome, {name}! Click 'SHOW ME A VERB' to begin.\n\n" 
        + explain_sets()
    )
    return msg, gr.update(visible=True), ""

def show_random_verb():
    global current_verb, already_submitted
    current_verb = random.choice(list(verbs_data.keys()))
    already_submitted = False
    return current_verb

def check_answer(name, user_past, user_pp):
    global correct_count, attempt_count, current_verb
    global set_number, attempt_in_set, already_submitted

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

    if upast == correct_past_str and upp in correct_pp_list:
        correct_count += 1
        feedback = random.choice(correct_feedback).format(name=name)
    else:
        feedback = random.choice(wrong_feedback).format(
            name=name,
            correct_past=correct_past_str,
            correct_pp=correct_pp_str
        )

    percentage = 0
    if attempt_count > 0:
        percentage = (correct_count / attempt_count) * 100
    score_str = f"Your Score: {correct_count} / {attempt_count} ({percentage:.1f}%)"

    recheck_msg = f"{current_verb} {correct_past_str} {correct_pp_str}"

    if attempt_in_set >= limit_per_set:
        if set_number < max_sets:
            # 한 세트 종료, 다음 세트로 넘어갈 옵션
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
            # 마지막 세트 종료
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
        # 세트 아직 진행중
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

def reset_inputs():
    return "", "", "", ""

def try_one_more_set():
    global set_number, attempt_in_set, already_submitted
    set_number += 1
    attempt_in_set = 0
    already_submitted = False
    msg = (f"**Now starting set {set_number}.**\n" + explain_sets())
    return msg, gr.update(visible=True), gr.update(visible=False)

def final_feedback(name):
    return f"### THE END\n\n{random.choice(final_encouragement).format(name=name)}"

def create_gradio_app():
    """Return the Gradio Blocks interface (but do NOT launch)."""
    with gr.Blocks() as app:
        gr.Markdown("# VerbMaster: Learn Irregular Verbs! 🎯")
        gr.Markdown("This app will help you learn irregular verbs. We have **10 sets** total, each set has **10 tries**.")

        # 이름 입력 + START
        name_input = gr.Textbox(label="Your Name", placeholder="Enter your name here")
        start_button = gr.Button("START")

        # 환영 메시지
        welcome_output = gr.Markdown()

        # Show me a verb 버튼 (처음에는 숨김)
        show_verb_button = gr.Button("SHOW ME A VERB", visible=False)

        # 현재 세트 상태 표시
        status_output = gr.Markdown()

        # 동사, 유저 입력, 제출
        present_verb_output = gr.Textbox(label="Present Verb", interactive=False)
        user_past_input = gr.Textbox(label="Enter Past Form")
        user_pp_input = gr.Textbox(label="Enter Past Participle")
        submit_button = gr.Button("SUBMIT", visible=False)

        # 피드백 영역
        feedback_output = gr.Textbox(label="Feedback", interactive=False)
        recheck_output = gr.Textbox(label="Recheck", interactive=False, visible=False)
        score_output = gr.Textbox(label="Score", interactive=False)

        # 오디오
        audio_button = gr.Button("NOT SURE HOW TO SAY IT? HEAR IT HERE!", visible=False)
        tts_output = gr.Audio(label="Audio Feedback", visible=False)

        # Continue & Try One More Set
        continue_button = gr.Button("IF YOU WANT TO CONTINUE, CLICK HERE!", visible=False)
        one_more_set_button = gr.Button("TRY ONE MORE SET", visible=False)

        # 제일 아래에 배치될 End 버튼
        end_button = gr.Button("IF YOU WANT TO END THIS APP, CLICK HERE!")
        final_feedback_output = gr.Markdown(visible=False)

        # --- 기능 연결 ---

        # 1) START 버튼 -> 환영메시지, Show me a verb 버튼 표시
        start_button.click(
            start_game,
            inputs=name_input,
            outputs=[welcome_output, show_verb_button, status_output]
        )

        # 2) Show me a verb -> 현재 동사 표시
        show_verb_button.click(
            show_random_verb,
            outputs=present_verb_output
        )

        # 3) Past Participle 입력 시 SUBMIT 버튼 보이기
        user_pp_input.change(
            lambda val: gr.update(visible=True) if val.strip() else gr.update(visible=False),
            inputs=user_pp_input,
            outputs=submit_button
        )

        # 4) SUBMIT -> check_answer
        submit_button.click(
            check_answer,
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

        # 5) Audio 버튼 -> 오디오 영역 표시
        audio_button.click(
            lambda: gr.update(visible=True),
            outputs=tts_output
        )

        # 6) Continue -> 입력값 초기화 & 새 동사
        continue_button.click(
            reset_inputs,
            outputs=[user_past_input, user_pp_input, feedback_output, recheck_output]
        )
        continue_button.click(
            show_random_verb,
            outputs=present_verb_output
        )
        continue_button.click(
            lambda: explain_sets(),
            outputs=status_output
        )

        # 7) Try One More Set -> 다음 세트로
        one_more_set_button.click(
            try_one_more_set,
            outputs=[welcome_output, show_verb_button, one_more_set_button]
        )

        # 8) End 버튼 (맨 아래) -> 최종 Encourage
        end_button.click(
            final_feedback,
            inputs=name_input,
            outputs=final_feedback_output
        )
        end_button.click(
            lambda: gr.update(visible=True),
            outputs=final_feedback_output
        )

    return app


# ================ STREAMLIT SECTION ================
def main():
    st.title("Gradio App inside Streamlit")
    st.write("Below is your Gradio interface, embedded within Streamlit!")

    # 1) Create the Gradio Blocks app (but don't launch)
    gradio_app = create_gradio_app()
    
    # 2) Run it in 'inline' mode so we get back HTML
    #    and use prevent_thread_lock so it doesn't block Streamlit
    gradio_app_html = gradio_app.run(
        show_error=True,
        inline=True,
        prevent_thread_lock=True
    )
    
    # 3) Embed that HTML into our Streamlit app
    st.components.v1.html(
        gradio_app_html,
        height=1400,  # adjust as needed
        scrolling=True
    )

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    app = create_gradio_app()
    app.launch()  # normal Gradio usage
