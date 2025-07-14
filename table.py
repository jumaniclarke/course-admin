import streamlit as st
import pandas as pd

# Sample DataFrame
df = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5],
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 35, 40, 45]
})

st.subheader("Original DataFrame")
st.dataframe(df)

# Programmatically "select" a row by filtering
# For example, select the row where 'ID' is 3
selected_row_data = df.loc[df['ID'] == 3]

st.subheader("Programmatically 'Selected' Row (Filtered)")
st.dataframe(selected_row_data)

# You can also use a multiselect widget to allow user selection and then filter
selected_names = st.multiselect('Select names to display:', df['Name'].tolist())
if selected_names:
    user_selected_rows = df[df['Name'].isin(selected_names)]
    st.subheader("User Selected Rows")
    st.dataframe(user_selected_rows)