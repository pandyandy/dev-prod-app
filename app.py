import streamlit as st
import pandas as pd
import colorsys
import hashlib

logo_url = "https://assets-global.website-files.com/5e21dc6f4c5acf29c35bb32c/5e21e66410e34945f7f25add_Keboola_logo.svg"

logo_html = f'''
<div style="display: flex; align-items: center; justify-content: left; font-size: 35px; font-weight: 600;">
    <img src="{logo_url}" style="height: 40px;">
    <span style="margin: 0 20px;">Project Lifecycle Manager</span>
</div>
'''
st.markdown(logo_html, unsafe_allow_html=True)

st.markdown('''---''')
st.subheader('Setup Environments')
""

if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=['env_name', 'stack', 'branch'])

if 'project_mapping' not in st.session_state:
    st.session_state['project_mapping'] = pd.DataFrame(columns=['env_name', 'stack', 'branch', 'project_name', 'id', 'link'])

def env_name_color(env_name):
    hash_object = hashlib.md5(env_name.encode())
    hash_digest = hash_object.hexdigest()
    hue = int(hash_digest[:6], 16) % 360 / 360.0
    hue = (hue * 12) % 1
    rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
    r, g, b = [int(x * 255) for x in rgb]
    return f'color: #{r:02X}{g:02X}{b:02X}'

col1, col2 = st.columns(2)

@st.experimental_dialog('Add a new environment')
def add_environment():
    env_name = st.text_input('Env Name')
    stack = st.selectbox('Stack', ['US', 'EU'])
    branch = st.text_input('Branch')
    
    if st.button('Add'):
        if env_name and stack and branch:
            if env_name not in st.session_state['data']['env_name'].values:
                new_row = pd.DataFrame({"env_name": [env_name], "stack": [stack], "branch": [branch]})
                st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)
                st.rerun()
            else:
                st.warning('Environment already exists')
        else:
            st.warning('Please fill all the fields')

if col1.button('➕ Add a new environment', use_container_width=True):
    add_environment()

@st.experimental_dialog('Delete an environment')
def delete_environment():
    name_to_delete = st.selectbox('Env Name', st.session_state['data']['env_name'].unique())

    if st.button('Delete'):
        if name_to_delete in st.session_state['data']['env_name'].values:
            st.session_state['data'] = st.session_state['data'][st.session_state['data']['env_name'] != name_to_delete]
            st.session_state['project_mapping'] = st.session_state['project_mapping'][st.session_state['project_mapping']['env_name'] != name_to_delete]
            st.rerun()
        else:
            st.warning('Environment not found')

if col2.button('➖ Delete an environment', use_container_width=True):
    delete_environment()

st.dataframe(
    st.session_state['data'].style.map(env_name_color, subset=['env_name']), 
    column_config={
        'env_name': 'Env Name',
        'stack': 'Stack', 
        'branch': 'Branch'
    },
    use_container_width=True, 
    hide_index=True
)

st.markdown("""---""")
st.subheader('Project Mapping')
""
col1, col2 = st.columns(2)

@st.experimental_dialog('Add a new project')
def add_project():
    project_name = st.text_input('Project Name')
    env_name = st.selectbox('Env Name', st.session_state['data']['env_name'].unique())
    id = st.text_input('ID')
    link = st.text_input('Link')

    if st.button('Add'):
        if project_name and env_name and id and link:
            env_data = st.session_state['data'][st.session_state['data']['env_name'] == env_name]
            stack = env_data['stack'].values[0]
            branch = env_data['branch'].values[0]
            new_row = pd.DataFrame({'project_name': [project_name], 'env_name': [env_name], 'stack': [stack], 'branch': [branch], 'id': [id], 'link': [link]})
            st.session_state['project_mapping'] = pd.concat([st.session_state['project_mapping'], new_row], ignore_index=True)
            st.rerun()
        else:
            st.warning('Please fill all the fields')

if col1.button('➕ Add a new project', use_container_width=True):
    add_project()

@st.experimental_dialog('Delete a a project')
def delete_project():
    project_env_combinations = st.session_state['project_mapping'].apply(
        lambda row: f"{row['project_name']} ({row['env_name']})", axis=1)
    name_to_delete = st.selectbox('Project Name (Env Name)', project_env_combinations.unique())

    if st.button('Delete'):
        if name_to_delete in st.session_state['project_mapping']['project_name'].values:
            st.session_state['project_mapping'] = st.session_state['project_mapping'][st.session_state['project_mapping']['project_name'] != name_to_delete]
            st.rerun()
        else:
            st.warning('Environment not found')

if col2.button('➖ Delete a project', use_container_width=True):
    delete_project()
    
st.dataframe(
    st.session_state['project_mapping'][['env_name', 'project_name', 'id', 'link']].style.map(env_name_color, subset=['env_name']),
    column_config={
        'env_name': 'Env Name',
        'project_name': 'Project Name',
        'id': 'Project ID',
        'link': st.column_config.LinkColumn('Link', display_text='Go to Project')
    },
    use_container_width=True,
    hide_index=True
)

st.markdown('''---''')
st.subheader('Pipeline Actions (Version Control Setup)')

scm_platform = st.selectbox('SCM Platform', ['GitHub', 'GitLab', 'Bitbucket'])

if st.button('Generate Environment'):
# generate some step by step instructions
    st.markdown('''---''')


