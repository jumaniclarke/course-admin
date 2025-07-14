import streamlit as st
import pandas as pd
import psycopg2
import methods

if "df_cand" not in st.session_state:
    st.session_state.df_cand = pd.DataFrame()
if "student_options" not in st.session_state:
    st.session_state.student_options = []
if "student_options_index" not in st.session_state:
    st.session_state.student_options_index = 0
if "student_answers" not in st.session_state:
    st.session_state.student_answers = pd.DataFrame()
if "student_sessions" not in st.session_state:
    st.session_state.student_sessions = pd.DataFrame()
if "student_selected" not in st.session_state:
    st.session_state.student_selected = 1
if "choose_student_df" not in st.session_state:
    st.session_state.choose_student_df = pd.DataFrame()
if "selection_mode" not in st.session_state:
    st.session_state.selection_mode = "Slider"
if "list_of_students" not in st.session_state:
    st.session_state.list_of_students = pd.DataFrame()
if "browse_submissions" not in st.session_state:
    st.session_state.browse_submissions = "Last submission"
#if "session_selected" not in st.session_state:
#    st.session_state.session_selected = 1
        
with st.sidebar.form("course_tut_form"):
    with st.sidebar:
        st.title("Excel Tutorial marking")
        st.markdown(" ## Select the options below to mark a submission")
        # get user input for course and tutorial/exam selection
        course = st.segmented_control(    " ### Select a course",
                ["MAM1013F", "MAM1014F", "MAM1022F"], 
                selection_mode="single",
                key="the_course",
            )
        thetut = st.selectbox("Select a tutorial/exam",
            ["TUT1", "TUT2", "TUT3","TUT4", "TUT5", "TUT6", "EXAM2025"], 
            key="the_tut",
            #on_change=methods.list_students,
            index=None
            )
        st.form_submit_button("Show students")
    
if course and thetut:
    methods.list_students()
    try:
        mode = st.sidebar.radio(
            "Selection mode: ",
            ["Slider", "List"],
            index = 0,
        )
        if st.session_state.browse_submissions == "Last submission":
            if mode == "Slider":
                o_student = st.sidebar.select_slider('Slider:',
                    options=range(1, len(st.session_state.student_options) + 1), 
                    key="student_selected",
                    on_change=methods.get_student_sessions(st.session_state.student_selected-1),
                    value = 1
                )
                st.sidebar.write("Student selected: " + st.session_state.student_options[st.session_state.student_selected - 1] if st.session_state.student_selected > 0 else "None")
                col1, col2 = st.sidebar.columns(2)

                if len(st.session_state.student_options) > 0:
                    
                    col1.button("Prev. Student", on_click=methods.decrease_student_selected)

                    col2.button("Next Student", on_click=methods.increase_student_selected)
                    
            else:
                methods.get_student_names(course)
                st.sidebar.write("### Choose a student by student number")
                choose_student = st.sidebar.dataframe(
                    st.session_state.df_cand,
                    use_container_width=True,
                    hide_index=True,
                    height = int(35.2*(10)),
                    on_select="rerun",
                    selection_mode=["single-row"],   
                    column_order=["studentnumber", "students"],
                )
                if choose_student.selection["rows"]:
                    methods.get_student_sessions(choose_student.selection["rows"][0])
            if course and thetut:
                st.write("### Student answers from " + st.session_state.student_options[st.session_state.student_selected - 1] + " for " + course + " " + thetut
                            )
    except Exception as e:
        st.error(f"An error occurred while selecting a student: {e}")


    if len(st.session_state.student_sessions) == 1:
        st.write("Only one submission found for this student. No need to select a submission.")
    elif not st.session_state.student_sessions.empty:
        o_session = st.select_slider(
            "Select submission",
            options=st.session_state.student_sessions["answer_number"] if "answer_number" in st.session_state.student_sessions.columns else [],
            key="session_selected",
            #on_change=methods.list_answers(st.session_state.session_selected),
            value=st.session_state.student_sessions["answer_number"].iloc[-1] if not st.session_state.student_sessions.empty and "answer_number" in st.session_state.student_sessions.columns else None,
        )
        methods.list_answers(st.session_state.session_selected)
    try:
        display_df = st.data_editor(
            st.session_state.student_answers, 
            column_config={
                "sessionid": None,
                "questionid": st.column_config.Column(label="Question ID", width="small", disabled=True),
                "answertext": st.column_config.Column(label="Answer Text", width="large", disabled=True),
                "markawarded": st.column_config.Column(label="Mark Awarded", width="small", disabled=False),
                "View?": st.column_config.Column(label="View?", width="small", disabled=False) if "View?" in st.session_state.student_answers.columns else None
            },
            key="data", 
            disabled=["sessionid", "questionid", "answertext"],
            hide_index=True,
        )
            #on_change=methods.get_answer_text,
            #selection_mode=["single-row"],

            #"""Get the answer text for the selected row."""
    except Exception as e:
        st.error(f"An error occurred while displaying the data editor: {e}")
        display_df = None
    changed_rows = st.session_state["data"]["edited_rows"]

    #if changed_rows:
        # Get indices of rows where 'View?' is True
    for row in changed_rows:
        if 'View?' in changed_rows[row]:
            if changed_rows[row]['View?']:
                answer_text = st.session_state.student_answers.loc[row, 'answertext']
                view_text = st.session_state.student_answers.loc[row, 'View?']
                st.write(f"Answer Text for row {row}: {answer_text}")

    if st.button("Save Changes"):
        # Only update the rows that have changed
        updated_rows = []
        for row in changed_rows:
            # Create a copy of the original row and update only changed columns
            updated_row = st.session_state.student_answers.loc[row].copy()
            for col, val in changed_rows[row].items():
                updated_row[col] = val
            updated_rows.append(updated_row)
        if updated_rows:
            # Create a DataFrame with only the changed rows
            updated_df = pd.DataFrame(updated_rows)
            # Call your method to save only the changed rows to the database
            if course and thetut:
                methods.save_student_answers_to_db(updated_df, course, thetut)
        else:
            st.info("No changes to save.")
        





