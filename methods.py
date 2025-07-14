import streamlit as st
import pandas as pd
import psycopg2-binary as ps
import psycopg2.extras as extras


conn1 = None
cur = None
#initialize connection


@st.cache_resource
def init_connection():
    return ps.connect(**st.secrets["postgres"])
# make a connection to the database
conn1 = init_connection()

def run_query(query): #returns a pandas dataframe
    conn1.rollback()  # Ensure we start with a clean slate
    with conn1.cursor() as cur:
        cur.execute(query)
        the_dataframe = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        return the_dataframe
def list_students():
    """List all students who have submitted the workbook for the selected course and tutorial/exam."""
    try:
        if st.session_state.the_course and st.session_state.the_tut:
            values = {st.session_state.the_course, st.session_state.the_tut}
            # select the final submission and student number of 
            # all the students who have submitted the workbook for the selected course and tutorial/exam
            query_candidates = f"""
                SELECT studentnumber, MAX(sessionid) 
                AS MaxSessID FROM session_stream 
                WHERE workbookname = '{st.session_state.the_course}{st.session_state["the_tut"].upper()}.XLS' GROUP BY studentnumber"""
            #st.write("the candidates query: ", query_candidates)
            cursor = conn1.cursor()
            cur = conn1.cursor()

            df_candidates = run_query(query_candidates)
            st.session_state.df_cand = df_candidates
            st.session_state.student_options = sorted(df_candidates['studentnumber'].unique().tolist())
            #st.session_state.student_selected = 1  # Reset to the first student by default
        #get_student_sessions()
        
    except Exception as e:
        st.error(f"Error retrieving student list: {e}")
def get_student_names(ocourse):
    # get student names from the database table studentclassesnew_stream 
    # that match the student numbers in the df_candidates dataframe 
    try:
        if st.session_state.df_cand.empty:
            st.error("No candidates found. Please run the list_students function first.")
            return
        student_numbers = tuple(st.session_state.df_cand['studentnumber'].unique())
        query_names = f"""
            SELECT studentid, students FROM studentclassesnew_stream 
            WHERE studentid IN {student_numbers}
            AND courseid = '{ocourse}'
            ORDER BY studentid
        """
        #st.write("the names query: ", query_names)
        df_names = run_query(query_names)
        # add the column 'students' to the df_candidates dataframe where the student number matches the studentid in the df_names dataframe
        # but first check if the df_candidates dataframe has the column 'students' and if not, create it, but if it does, just update it
        if 'students' not in st.session_state.df_cand.columns:
            st.session_state.df_cand['students'] = ""
        # update the df_candidates dataframe with the student names
        for index, row in df_names.iterrows():
            student_number = row['studentid']
            student_name = row['students']
            # update the df_candidates dataframe with the student name
            st.session_state.df_cand.loc[st.session_state.df_cand['studentnumber'] == student_number, 'students'] = student_name
            # sort the df_candidates dataframe by studentnumber
            st.session_state.df_cand = st.session_state.df_cand.sort_values(by='studentnumber')

    except Exception as e:
        st.error(f"Error retrieving student names: {e}")

def get_student_sessions(s_index):
    """
    Populate the variable student_sessions with all entries from the 'sessions' table
    that match the selected student and workbook.
    """
    try:
        if st.session_state.student_selected and st.session_state.the_course and st.session_state.the_tut:
            student = st.session_state.student_options[s_index] if s_index > 0 else st.session_state.student_options[0]
            workbook = f"{st.session_state.the_course}{st.session_state['the_tut'].upper()}.XLS"
            query = f"""
                SELECT * FROM session_stream
                WHERE studentnumber = '{student}'
                AND workbookname = '{workbook}'
                ORDER BY sessionid
            """
            #st.write(query)
            student_sessions = run_query(query)
            st.session_state.student_sessions = student_sessions
            st.session_state.student_sessions['answer_number'] = list(range(1, len(student_sessions) + 1)) if len(student_sessions) > 1 else [1]
            #adjust the session_selected to the last session if it exists
            if not student_sessions.empty:
                #st.session_state.session_selected = student_sessions['answer_number'].iloc[-1]
                list_answers(student_sessions['answer_number'].iloc[-1])
            elif len(student_sessions) == 1:
                #st.session_state.session_selected = 1
                list_answers(1)  
            else:
                st.write("No sessions found for this student.")
                st.session_state.student_answers = pd.DataFrame()  # Reset answers if no sessions found
            
    except Exception as e:
        st.error(f"Error retrieving student sessions: {e}")


def increase_student_selected():
    """
    Increase the student selected index by 1.
    This function is called when the user clicks the Next Student button.
    """
    try:
        if st.session_state.student_selected < len(st.session_state.student_options) - 1:
            st.session_state.student_selected += 1
            get_student_sessions(st.session_state.student_selected-1)
        else:
            st.warning("You are already at the last student.")
    except Exception as e:
        st.error(f"Error increasing student selected: {e}")
def decrease_student_selected():
    """
    Decrease the student selected index by 1.
    This function is called when the user clicks the Previous Student button.
    """
    try:
        if st.session_state.student_selected > 0:
            st.session_state.student_selected -= 1
            get_student_sessions(st.session_state.student_selected-1)
        else:
            st.warning("You are already at the first student.")
    except Exception as e:
        st.error(f"Error decreasing student selected: {e}")
def set_student_selected_with_button(index_input):
    st.session_state.student_selected = index_input
def update_student_options_index(o_index):
    """
    Update the student options index based on the current student selected.
    This function is called when the student selection changes.
    """
    try:
        if o_index < 0 or o_index >= len(st.session_state.student_options):
            st.error(f"Index {o_index} is out of range for student options.")
            return
        st.session_state.student_options_index = o_index
        get_student_sessions()
    except Exception as e:
        st.error(f"Error updating student options index: {e}")
def list_answers(session_index):
    try:
        these_candidates = st.session_state.df_cand
        idx = session_index - 1
        if idx < 0 or idx >= len(st.session_state.student_sessions):
            st.error(f"Selected session index {idx+1} is out of range.")
            return
        o_session = st.session_state.student_sessions.loc[idx, 'sessionid']
        value = {st.session_state.student_selected, o_session}
        answers_query = f"""
            SELECT sessionid, questionid, answertext, markawarded FROM answers_stream 
            WHERE sessionid = {o_session}
            ORDER BY questionid
            """
        # create a view of the answers for the selected student
        #st.write("the answers query: ", answers_query)
        these_candidatesstudent_answers = run_query(answers_query)
        st.session_state.student_answers = these_candidatesstudent_answers
        st.session_state.student_answers['View?'] = False
        data = st.session_state.student_answers
    except Exception as e:
        st.error(f"Error retrieving answers: {e}")
def set_mark(the_mark_given, the_row):
    update_mark_query = f"""
        UPDATE answers_stream 
        SET markawarded = {the_mark_given} 
        WHERE sessionid = {st.session_state.student_answers.loc[the_row, 'sessionid']}
        AND questionid = '{st.session_state.student_answers.loc[the_row, 'questionid']}'
        """
    st.write("the update mark query: ", update_mark_query)
    try:
        with conn1.cursor() as cur:
            cur.execute(update_mark_query)
            conn1.commit()
            list_answers(st.session_state.sessoin_selected)
            st.success("Mark updated successfully!")
    except Exception as e:
        st.error(f"Error updating mark: {e}")

def save_student_answers_to_db(df, course, tut):
    """
    Efficiently update student answers from a DataFrame to the 'answers_stream' table in the database.
    Uses batch updates for better performance.
    Assumes df has columns: studentnumber, questionid, answertext, markawarded, sessionid (if needed).
    """
    table_name = "answers_stream"
    df['course'] = course
    df['tut'] = tut

    # Prepare data for batch update
    data_tuples = [
        (row['markawarded'], row['questionid'], row.get('sessionid', None))
        for _, row in df.iterrows()
    ]

    update_query = f"""
        UPDATE {table_name}
        SET markawarded = %s
        WHERE questionid = %s
            AND sessionid = %s
    """

    try:
        with conn1.cursor() as cur:
            extras.execute_batch(cur, update_query, data_tuples, page_size=100)
            conn1.commit()
        st.success("Student answers updated in database successfully!")
    except Exception as e:
        st.error(f"Error updating student answers: {e}")
    
