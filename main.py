import json

import streamlit as st
from streamlit_option_menu import option_menu

from utils import list_skills


SKILLS_PATH = "./skills"

st.set_page_config(
     page_title="SPooN's SDK - helper",
     page_icon="https://www.spoon-cloud.com/favicon.ico",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
     }
 )

st.title("SPooN's SDK")

skills = list_skills()

selected = []
with st.sidebar:
    selected = option_menu("Skills", skills,
        icons=['bricks']*len(skills), menu_icon="robot", default_index=0)

def is_list_of_numbers(mylist):
    for i in mylist:
        if type(i) != float:
            return False
    return True

def parse_subskill(subskill):
    filled_skill = {}
    for key in subskill:
        subskill_name = key
        subskill_content = subskill[subskill_name]

        # don't show the id but store it in the generated json
        if subskill_name == "id":
            filled_skill[subskill_name] = subskill_content

        if subskill_content == "str":
            filled_skill[subskill_name] = st.text_input(subskill_name)
        elif subskill_content == "bool":
            filled_skill[subskill_name] = st.checkbox(subskill_name)
        elif subskill_content == "float":
            filled_skill[subskill_name] = st.number_input(subskill_name)
        elif type(subskill_content) == list:
            if len(subskill_content) == 2:
                filled_skill[subskill_name] = st.radio(subskill_name, subskill_content)
            elif len(subskill_content) == 4 and is_list_of_numbers(subskill_content):
                filled_skill[subskill_name] = st.slider(subskill_name, subskill_content[0], subskill_content[1],
                                                        value=subskill_content[3],
                                                        step=subskill_content[2])
            else:
                filled_skill[subskill_name] = st.selectbox(subskill_name, subskill_content)
        elif type(subskill_content) is dict:
            st.subheader(subskill_name)
            filled_skill[subskill_name] = parse_subskill(subskill_content)
        else:
            filled_skill[subskill_name] = subskill_content

    return filled_skill

def skill_to_streamlit(skill_name):
    st.header(skill_name)
    with open(SKILLS_PATH + "/" + skill_name + ".json") as f:
        skill_as_json = json.load(f)

        filled_skill = {}
        filled_skill["spoon"] = parse_subskill(skill_as_json)

        generated_json = json.dumps(filled_skill, indent=2)

        st.code(body=generated_json, language="json")



skill_to_streamlit(selected)
