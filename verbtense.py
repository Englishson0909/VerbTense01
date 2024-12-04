
%%capture
!pip install gradio pandas
#@markdown APP2: Verb tense checking
import gradio as gr
import pandas as pd
import random

# Load the CSV file from the provided URL
csv_url = "https://raw.githubusercontent.com/MK316/241214/refs/heads/main/data/verb_sample.csv"
df = pd.read_csv(csv_url)

# Initialize state
state = {"remaining_verbs": df.copy(), "score": 0, "trials": 0, "current_index": -1}

# Function to select a random verb
def select_random_verb():
    if state["remaining_verbs"].empty:
        return "Completed"
    state["current_index"] = random.randint(0, len(state["remaining_verbs"]) - 1)
    selected_verb = state["remaining_verbs"].iloc[state["current_index"]]
    return f"Verb: {selected_verb['Verb']}"

# Function to check the user's classification and verb forms
def check_answer(user_classification, user_forms):
    if state["remaining_verbs"].empty:
        return "All verbs have been answered correctly. Great job!", f"Score: {state['score']}/{state['trials']}"

    index = state["current_index"]
    if index == -1:
        return "Please click 'Show the Verb' first.", f"Score: {state['score']}/{state['trials']}"

    verb_data = state["remaining_verbs"].iloc[index]
    verb = verb_data['Verb']
    past = verb_data['Past']
    pp = verb_data['PP']
    regularity = verb_data['Regularity']

    # Update trials
    state["trials"] += 1

    # Parse the user input
    user_parts = [part.strip().lower() for part in user_forms.split(",") if part.strip()]
    if len(user_parts) != 2:
        return "Please provide both Past and Past Participle transformations separated by a comma.", f"Score: {state['score']}/{state['trials']}"

    user_past, user_pp = user_parts

    # Check user's answers
    regularity_correct = user_classification.lower() == regularity.lower()
    past_correct = user_past == past.lower()
    pp_correct = user_pp == pp.lower()

    if regularity_correct and past_correct and pp_correct:
        state["score"] += 1
        feedback = f"Correct! {verb} - Past: {past}, PP: {pp} - Regularity: {regularity}"
        # Remove the verb from the remaining list
        state["remaining_verbs"] = state["remaining_verbs"].drop(state["remaining_verbs"].index[index])
    else:
        feedback = (
            f"Incorrect. Correct: Regularity={regularity}, Past={past}, PP={pp}. "
            f"You entered: Regularity={user_classification}, Past={user_past}, PP={user_pp}."
        )

    if state["remaining_verbs"].empty:
        return "Completed", f"Score: {state['score']}/{state['trials']}"

    return feedback, f"Score: {state['score']}/{state['trials']}"

# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("### VerbMaster [Verb list](https://raw.githubusercontent.com/MK316/241214/refs/heads/main/data/verb_sample.csv)")
    gr.Markdown("""
1. Click the 'Show the Verb' button.
2. Choose regular/irregular.
3. Enter the past and past participle (comma-separated) (e.g., "liked, liked").
4. Click the 'Submit' button.
5. Check your score: Your score will be displayed at the bottom of the screen.
6. Play again: To continue, click the 'Show the Verb' button and try another verb.
""")

    # Button to display a verb
    show_button = gr.Button("Show the Verb")
    verb_details = gr.Textbox(label="Verb Details", interactive=False)

    # Radio buttons for regularity question
    options = gr.Radio(["Regular", "Irregular"], label="Is the verb regular or irregular?")

    # Input field for past and past participle transformations
    transformation_input = gr.Textbox(label="Enter Past and Past Participle (comma-separated)")

    # Submit button and feedback
    submit_button = gr.Button("Submit")
    feedback = gr.Textbox(label="Feedback", interactive=False)
    score_display = gr.Textbox(label="Score/Trial", interactive=False)

    # Button click actions
    show_button.click(fn=select_random_verb, outputs=verb_details)
    submit_button.click(
        fn=check_answer, inputs=[options, transformation_input], outputs=[feedback, score_display]
    )

# Launch the app
app.launch()
