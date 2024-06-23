import streamlit as st
import pandas as pd
import re 

# Set the logo adn page title
LOGO_URL = 'https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg'
LOGO_HTML = f'''
<div style="display: flex; align-items: center; justify-content: left; font-size: 35px; font-weight: 600;">
    <img src="{LOGO_URL}" style="height: 40px;">
    <span style="margin: 0 20px;">Project Lifecycle Manager</span>
</div>
'''
st.markdown(LOGO_HTML, unsafe_allow_html=True)

# Initialize the session state
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=['env_name', 'stack', 'branch'])
if 'project_mapping' not in st.session_state:
    st.session_state['project_mapping'] = pd.DataFrame(columns=['stack', 'branch', 'project_name'])

# Setup Environments
st.markdown('---')
st.subheader('Setup Environments')
''

# Add and delete environments
@st.experimental_dialog('Add a new environment', width='large')
def add_environment():
    env_name = st.text_input('Environment Name')
    stack = st.selectbox('Stack', ['US', 'EU'])
    branch = st.text_input('Branch')
    
    if st.button('Add'):
        if env_name and stack and branch:
            if env_name not in st.session_state['data']['env_name'].values:
                new_row = pd.DataFrame({"env_name": [env_name], "stack": [stack], "branch": [branch]})
                st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)
                st.session_state['project_mapping'][f'{env_name}_id'] = ''
                st.session_state['project_mapping'][f'{env_name}_link'] = ''
                st.rerun()
            else:
                st.warning('Environment already exists')
        else:
            st.warning('Please fill all the fields')

@st.experimental_dialog('Delete an environment', width='large')
def delete_environment():
    name_to_delete = st.selectbox('Environment Name', st.session_state['data']['env_name'].unique())

    if st.button('Delete'):
        if name_to_delete in st.session_state['data']['env_name'].values:
            st.session_state['data'] = st.session_state['data'][st.session_state['data']['env_name'] != name_to_delete]
            st.session_state['project_mapping'].drop(columns=[f'{name_to_delete}_id', f'{name_to_delete}_link'], inplace=True, errors='ignore')
            st.rerun()
        else:
            st.warning('Environment not found')

col1, col2 = st.columns(2)
if col1.button('➕ Add a new environment', use_container_width=True):
    add_environment()

if col2.button('➖ Delete an environment', use_container_width=True):
    delete_environment()

# Display the environments
st.dataframe(
    st.session_state['data'], 
    column_config={
        'env_name': 'Environment Name',
        'stack': 'Stack', 
        'branch': 'Branch'
    },
    use_container_width=True, 
    hide_index=True
)

# Project Mapping
st.markdown('''---''')
st.subheader('Project Mapping')
''

# Add and delete projects
@st.experimental_dialog('Add a new project', width='large')
def add_project():
    if 'data' not in st.session_state or st.session_state['data'].empty:
        st.info("Please setup environments first")
        return
    
    project_name = st.text_input('Project Name')
    links = {}
    
    for env_name in st.session_state['data']['env_name'].unique():
        st.subheader(f'{env_name}')
        links[env_name] = st.text_input(f'Link', key=f'link_{env_name}')

    if st.button('Add'):
        if project_name:
            new_row = {'project_name': project_name}
            for env_name in st.session_state['data']['env_name'].unique():
                env_data = st.session_state['data'][st.session_state['data']['env_name'] == env_name]
                new_row['stack'] = env_data['stack'].values[0]
                new_row['branch'] = env_data['branch'].values[0]
                new_row[f'{env_name}_link'] = links[env_name]
                match = re.search(r'https://.*keboola\..*/projects/(\d+)', links[env_name])
                new_row[f'{env_name}_id'] = match.group(1) if match else ''

            new_row_df = pd.DataFrame([new_row])
            st.session_state['project_mapping'] = pd.concat([st.session_state['project_mapping'], new_row_df], ignore_index=True)
            st.rerun()
        else:
            st.warning('Please fill the project name')

@st.experimental_dialog('Delete a project', width='large')
def delete_project():
    name_to_delete = st.selectbox('Project Name', st.session_state['project_mapping']['project_name'])

    if st.button('Delete'):
        if name_to_delete in st.session_state['project_mapping']['project_name'].values:
            st.session_state['project_mapping'] = st.session_state['project_mapping'][st.session_state['project_mapping']['project_name'] != name_to_delete]
            st.rerun()
        else:
            st.warning('Environment not found')

col1, col2 = st.columns(2)
if col1.button('➕ Add a new project', use_container_width=True):
    add_project()

if col2.button('➖ Delete a project', use_container_width=True):
    delete_project()

# Display the project mapping
column_config = {'project_name': 'Project Name'}
for env_name in st.session_state['data']['env_name'].unique():
    column_config[f'{env_name}_link'] = st.column_config.LinkColumn(
        f'{env_name}', 
        validate="https://.*keboola\..*/projects/\d+.*$",
        display_text="https://.*keboola\..*/projects/(\d+)"
    )
    
st.dataframe(
    st.session_state['project_mapping'][[col for col in st.session_state['project_mapping'].columns if '_id' not in col and col not in ['stack', 'branch']]],
    column_config=column_config,
    use_container_width=True,
    hide_index=True
)

# Pipeline Actions
st.markdown('''---''')
st.subheader('Pipeline Actions (Version Control Setup)')
scm_platform = st.selectbox('SCM Platform', ['GitHub', 'GitLab', 'Bitbucket'], key='scm_platform')

# Generate the environment
if st.button('Generate Environment'):
    st.markdown('''---''')