
!pip install gradio gtts pandas

import gradio as gr
import pandas as pd
import random
import os
import tempfile
from gtts import gTTS

# Load the irregular verbs data
data_url = "https://github.com/Hansukson/Application2/raw/main/irregular_verbs%20(1).csv"
verbs_df = pd.read_csv(data_url)

# Extract verbs data into a dictionary
verbs_data = verbs_df.set_index("present")[['past', 'p.p']].to_dict(orient="index")

# Correct Feedback List (unchanged)
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

# Wrong Feedback List (unchanged)
wrong_feedback = [
    "Wrong! Nice try, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Almost there, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Don’t give up, {name}. The correct forms are: {correct_past}, {correct_pp}.",
    "Wrong! Good effort, {name}. The correct answer is: {correct_past}, {correct_pp}.",
    "Wrong! Mistakes happen, {name}. The correct forms are: {correct_past}, {correct_pp}.",
]

# Final Encouragement Feedback - 더 따뜻하고 인간적인 응원 추가
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
    temp_audio_file = os.path.join(tempfile.gettempdir(), "verb_audio.mp3")
    tts = gTTS(tts_text)
    tts.save(temp_audio_file)
    return temp_audio_file

current_verb = ""
correct_count = 0
attempt_count = 0

def start_game(name):
    if name.strip() == "":
        return "Please enter your name to proceed!", gr.update(visible=False)
    return f"Welcome, {name}! Click 'SHOW ME A VERB' to begin.", gr.update(visible=True)

def show_random_verb():
    global current_verb
    current_verb = random.choice(list(verbs_data.keys()))
    return current_verb

def check_answer(name, user_past, user_past_participle):
    global correct_count, attempt_count, current_verb
    attempt_count += 1

    correct_past_str = verbs_data[current_verb]['past'].strip().lower()
    correct_pp_str = verbs_data[current_verb]['p.p'].strip().lower()
    correct_pp_list = [pp.strip() for pp in correct_pp_str.split('/')]

    user_past = user_past.strip().lower()
    user_past_participle = user_past_participle.strip().lower()

    audio_file = tts_play([current_verb, correct_past_str, correct_pp_str])

    if user_past == correct_past_str and user_past_participle in correct_pp_list:
        correct_count += 1
        feedback = random.choice(correct_feedback).format(name=name)
    else:
        feedback = random.choice(wrong_feedback).format(name=name, correct_past=correct_past_str, correct_pp=correct_pp_str)

    score = f"Your Score: {correct_count} / {attempt_count}"

    recheck_msg = f"{current_verb} {correct_past_str} {correct_pp_str}"

    return feedback, gr.update(value=recheck_msg, visible=True), score, audio_file, gr.update(visible=True), gr.update(visible=True)

def final_feedback(name):
    return f"### THE END\n{random.choice(final_encouragement).format(name=name)}"

def reset_inputs():
    return "", "", ""

def verb_game():
    with gr.Blocks() as app:
        gr.Markdown("# VerbMaster: Learn Irregular Verbs! 🎯")
        gr.Markdown("This app will help you learn irregular verbs.")

        name_input = gr.Textbox(label="Your Name")
        start_button = gr.Button("START")
        welcome_output = gr.Markdown()

        show_verb_button = gr.Button("SHOW ME A VERB", visible=False)

        present_verb_output = gr.Textbox(label="Present Verb", interactive=False)
        user_past_input = gr.Textbox(label="Enter Past Form")
        user_pp_input = gr.Textbox(label="Enter Past Participle")

        submit_button = gr.Button("SUBMIT", visible=False)
        feedback_output = gr.Textbox(label="Feedback", interactive=False)
        recheck_output = gr.Textbox(label="Recheck", interactive=False, visible=False)
        score_output = gr.Textbox(label="Score", interactive=False)

        audio_button = gr.Button("NOT SURE HOW TO SAY IT? HEAR IT HERE!", visible=False)
        tts_output = gr.Audio(label="Audio Feedback", visible=False)

        continue_button = gr.Button("IF YOU WANT TO CONTINUE, CLICK HERE!", visible=False)
        end_button = gr.Button("IF YOU WANT TO END THIS APP, CLICK HERE!", visible=False)

        final_feedback_output = gr.Markdown(visible=False)

        # START 버튼 클릭 -> SHOW ME A VERB 활성화
        start_button.click(start_game, inputs=name_input, outputs=[welcome_output, show_verb_button])

        # SHOW ME A VERB 클릭 -> 동사 표시
        show_verb_button.click(show_random_verb, outputs=present_verb_output)

        # Past Participle 입력 시 Submit 버튼 표시
        user_pp_input.change(
            lambda val: gr.update(visible=True) if val.strip() else gr.update(visible=False),
            inputs=user_pp_input,
            outputs=submit_button
        )

        # SUBMIT 클릭 -> feedback, recheck, score, 오디오, 발음 버튼, continue, end 버튼
        submit_button.click(
            check_answer,
            inputs=[name_input, user_past_input, user_pp_input],
            outputs=[feedback_output, recheck_output, score_output, tts_output, audio_button, continue_button]
        )
        submit_button.click(lambda: gr.update(visible=True), outputs=end_button)

        # 발음 버튼 클릭 -> 오디오 표시
        audio_button.click(lambda: gr.update(visible=True), outputs=tts_output)

        # Continue 버튼 -> 입력 리셋, 새로운 동사
        continue_button.click(reset_inputs, outputs=[user_past_input, user_pp_input, feedback_output])
        continue_button.click(show_random_verb, outputs=present_verb_output)

        # End 버튼 클릭 시 Final Feedback 표시
        end_button.click(final_feedback, inputs=name_input, outputs=final_feedback_output)
        end_button.click(lambda: gr.update(visible=True), outputs=final_feedback_output)

    return app

app = verb_game()
app.launch()

