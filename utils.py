import os
import json


SKILLS_PATH = "./skills"

def list_skills():
    list_of_skills = []
    for filename in os.listdir(SKILLS_PATH):
        list_of_skills.append(filename.replace(".json", ""))

    return list_of_skills

