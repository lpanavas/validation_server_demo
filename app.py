import streamlit as st
import pandas as pd
import ast

# Load the dataset
file_path = 'https://raw.githubusercontent.com/lpanavas/DPEducationDatasets/master/PUMS_california_demographics_1000.csv'
df = pd.read_csv(file_path)

# Allowed nodes for the AST parser
ALLOWED_NODES = {
    'Module', 'Expr', 'Call', 'Attribute', 'Name', 'Load', 'Subscript',
    'Index', 'Compare', 'Num', 'Str', 'List', 'Tuple', 'BinOp', 'Add', 'Gt',
    'GtE', 'Lt', 'LtE', 'Eq', 'NotEq', 'And', 'Or', 'BoolOp', 'In', 'NotIn',
    'Is', 'IsNot', 'Constant', 'keyword'
}

# Allowed attributes (methods) for DataFrame
ALLOWED_ATTRS = {'filter', 'shape', 'count', 'size', 'groupby', 'cut', 'value_counts'}

# Function to validate the user query
def validate_query(query):
    try:
        tree = ast.parse(query, mode='exec')
        for node in ast.walk(tree):
            if type(node).__name__ not in ALLOWED_NODES:
                return False, f"Disallowed operation: {type(node).__name__}"
            if isinstance(node, ast.Attribute) and node.attr not in ALLOWED_ATTRS:
                return False, f"Disallowed attribute: {node.attr}"
        return True, None
    except Exception as e:
        return False, str(e)

# Function to execute the user query with validation
def execute_query_with_validation(query, df):
    valid, error = validate_query(query)
    if not valid:
        return False, error
    try:
        result = eval(query, {'df': df, 'pd': pd})
        return True, result
    except Exception as e:
        return False, str(e)

# Example queries with descriptions
example_queries = {
    "Count rows where income is greater than 20000: df[df['income'] > 20000].shape[0]": 'df[df["income"] > 20000].shape[0]',
    "Count rows where age is greater than 30: df[df['age'] > 30].shape[0]": 'df[df["age"] > 30].shape[0]',
    "Count rows where sex is 1 (male): df[df['sex'] == 1].shape[0]": 'df[df["sex"] == 1].shape[0]',
    "Count rows where education level is 11: df[df['educ'] == 11].shape[0]": 'df[df["educ"] == 11].shape[0]',
    "Count rows where race is 1: df[df['race'] == 1].shape[0]": 'df[df["race"] == 1].shape[0]',
    "Count rows by sex: df.groupby('sex').size()": 'df.groupby("sex").size()',
    "Count rows by education level: df.groupby('educ').size()": 'df.groupby("educ").size()',
    "Count rows by race and sex: df.groupby(['race', 'sex']).size()": 'df.groupby(["race", "sex"]).size()',
    "Count rows where income is greater than 50000 by education level: df[df['income'] > 50000].groupby('educ').size()": 'df[df["income"] > 50000].groupby("educ").size()',
    "Group by sex and education level: df.groupby(['sex', 'educ']).size()": 'df.groupby(["sex", "educ"]).size()',
    "Group by race and count income categories: pd.cut(df['income'], bins=[0, 10000, 20000, 30000, 40000, 50000, float('inf')]).value_counts()": 'pd.cut(df["income"], bins=[0, 10000, 20000, 30000, 40000, 50000, float("inf")]).value_counts()'
}

# Two-column layout
col1, col2 = st.columns(2)

with col1:
    # Dropdown for example queries
    selected_query_desc = st.selectbox('Select an example query:', list(example_queries.keys()))
    selected_query = example_queries[selected_query_desc]
    
    # Display the description of the selected query
    st.write(selected_query_desc)
    
    # Text area for code input with the selected query as default
    user_query = st.text_area('Enter your Pandas query:', selected_query)
    
    # Button to execute the query
    if st.button('Run Query'):
        valid, result = execute_query_with_validation(user_query, df)
        
        if not valid:
            st.error(result)
        else:
            st.session_state['result'] = result

with col2:
    if 'result' in st.session_state:
        st.write('Query Output:')
        if isinstance(st.session_state['result'], (pd.DataFrame, pd.Series)):
            st.dataframe(st.session_state['result'])
        else:
            st.write(st.session_state['result'])
