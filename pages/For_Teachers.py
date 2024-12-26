import streamlit as st

def main():
    st.title("For Teachers")
    st.markdown(
        """
        This app is designed to help students systematically practice the three principal parts of English verbs 
        (present, past, and past participle).  
        It focuses on 100 key irregular verbs—selected from the core vocabulary recommended by the **Korea Institute 
        for Curriculum and Evaluation (KICE)** and other education authorities—and encourages learners to input the 
        past and past participle forms on their own for hands-on practice.  
        
        Additionally, the app provides audio so students can listen to each verb’s pronunciation and become more 
        familiar with these words.  
        Overall, the goal is to guide students in naturally mastering irregular verb forms and enhancing their language proficiency.

        **If you want to know the words list, [click here (The word list)](https://github.com/Hansukson/Application2/raw/main/irregular_verbs%20(1).csv).**
        """
    )

# 멀티페이지에선 아래 if문이 필수는 아니지만, 단독 실행할 때는 필요.
if __name__ == "__main__":
    main()

