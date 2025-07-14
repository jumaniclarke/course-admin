# Perform query
# Uses st.experimental_memo to only rerun when the query changes
from re import sub


@st.cache_data
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
    
#rows = run_query("SELECT * FROM empolyee")
rows = pd.DataFrame(run_query("SELECT * FROM empolyee"))

#df = pd.DataFrame(rows, columns=[desc[0] for desc in conn.cursor().description])
# print results

with st.form("data_editor_form"):
    st.caption("Edit the dataframe below")
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    submit_button = st.form_submit_button("Submit") 

if submit_button:
    try:
        #write the edited dataframe back to the database
        edited.to_sql('answers_stream', conn, if_exists='append', index=False)
        st.success("Data updated successfully!")
    except Exception as e:
        st.warning(f"Error updating data: {e}")
        
        
if selected_index is not None:
    selected_row = df.iloc[selected_index]
    st.write("Selected Row:")
    st.write(selected_row)
    
    # Display the selected row's details
    st.write(f"Session ID: {selected_row['sessionid']}")
    st.write(f"Question ID: {selected_row['questionid']}")
    st.write(f"Answer Text: {selected_row['answertext']}")
    st.write(f"Mark Awarded: {selected_row['markawarded']}")
    
    # Option to update the mark awarded
    new_mark = st.number_input("Update Mark Awarded", value=selected_row['markawarded'], step=1)
    
    if st.button("Update Mark"):
        try:
            update_query = f"""
                UPDATE answers_stream 
                SET markawarded = {new_mark} 
                WHERE sessionid = {selected_row['sessionid']} AND questionid = {selected_row['questionid']}
            """
            cur.execute(update_query)
            conn1.commit()
            st.success("Mark updated successfully!")
        except Exception as e:
            st.error(f"Error updating mark: {e}")
  
  with st.form("all_answers_form"):
    
    # Select a row from the table
    row_options = [f"Row {i+1}: {row['questionid']}" for i, row in df.iterrows()]
    selected_row_idx = st.selectbox("Select a row to edit", range(len(df)), format_func=lambda x: row_options[x])
    # record selection
    submitted_sb = st.form_submit_button("Confirm selection")

if submitted_sb:
    # Display editable text boxes for the selected row
    selected_row = df.iloc[selected_row_idx]
    st.write(selected_row_idx)
    edited_answertext = st.text_input("Answer Text", value=selected_row['answertext'])
    edited_markawarded = st.text_input("Mark Awarded", value=str(selected_row['markawarded']))

#submitted = st.form_submit_button("Submit Changes")
if st.button("Update Row"):
#if submitted:
    try:
        update_query = """
            UPDATE answers_stream
            SET answertext = %s, markawarded = %s
            WHERE sessionid = %s AND questionid = %s
        """
        cur.execute(update_query, (edited_answertext, edited_markawarded, selected_row['sessionid'], selected_row['questionid']))
        conn1.commit()
        st.success("Row updated successfully.")
    except Exception as e:
        st.error(f"Failed to update row: {e}")