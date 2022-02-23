import json

import streamlit as st

import os
from google.cloud import dialogflow
from google import protobuf

#credential_path =  os.path.dirname(os.path.realpath(__file__)) + "\\ugo-pfritcqo-eaa6a9424cd5.json"
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

project_id = "ugo-pfritcqo"


def delete_all_intents(project_id):
    intent_names = list_intents(project_id)

    for name in intent_names:
        delete_intent(project_id, name)

def list_intents(project_id):
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)

    intents = intents_client.list_intents(request={"parent": parent})

    intent_names = []
    for intent in intents:
        intent_names.append(intent.display_name)

    return intent_names


# [START dialogflow_delete_intent]
def delete_intent(project_id, name):
    """Delete intent with the given intent type and intent value."""
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    intent_id = _get_intent_ids(project_id, name)
    intent_path = intents_client.intent_path(project_id, intent_id[0])

    intents_client.delete_intent(request={"name": intent_path})

# [END dialogflow_delete_intent]


# Helper to get intent from display name.
def _get_intent_ids(project_id, display_name):
    from google.cloud import dialogflow

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent})
    intent_names = [
        intent.name for intent in intents if intent.display_name == display_name
    ]

    intent_ids = [intent_name.split("/")[-1] for intent_name in intent_names]

    return intent_ids


def create_intent(project_id, display_name, training_phrases_parts, message_texts=None, payloads=None, events=[],
                  parent_intent=None):
    """Create an intent of the given intent type."""

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)
    message = None
    if message_texts is not None:
        text = dialogflow.Intent.Message.Text(text=message_texts)
        message = dialogflow.Intent.Message(text=text)

    elif payloads is not None:
        custom_payload = protobuf.struct_pb2.Struct()
        custom_payload.update(payloads)
        message = dialogflow.Intent.Message(payload=custom_payload)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message],
        events=events,
        parent_followup_intent_name=parent_intent
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))
    return response.name



st.title("SPooN's SDK")

if st.button('Delete the scenario'):
    delete_all_intents(project_id)

st.header("MCQ")
question = st.text_input("Question")
visual_answers = st.checkbox("Visual Answers", True)

number_of_choices = st.slider("number of choices", 1,6,1)

cols = st.columns(number_of_choices)
choices = []
for i, col in enumerate(cols):
    choices.append(
        {
            "displayText": col.text_input("display text", key="mcq_display_text_" + str(i)),
            "content": col.text_input("content", key="mc_content_" + str(i)),
            "imageUrl": col.text_input("image_url", key="mcq_image_url_" + str(i))
        }
    )

if st.button("Create MCQ"):
    mcq = {
        "spoon":
            {
                "id": "MCQ",
                "question": question,
                "answers": [
                    {
                        "displayText": choice["displayText"],
                        "content": choice["content"],
                        "imageUrl": choice["imageUrl"]
                    }

                    for choice in choices
                ]
            }
    }
    parent_intent = create_intent(project_id, question, [question], payloads=mcq)

    for choice in choices:
        create_intent(project_id, choice["displayText"], [choice["displayText"]], [choice["content"]],
                      parent_intent=parent_intent)


st.header("Generating JSON for TTSa")
tts = st.text_input("text to say")
expression_type = st.selectbox("Expression type",
                               ["Standard", "Happy", "Sad", "Surprised", "Scared", "Curious", "Proud", "Mocker", "Crazy"])
expression_intensity = st.slider("Expression Intensity", 0., 1., 0.7, 0.1)
expression_gaze_mode = st.radio("Expression Gaze mode",
                                ["Focused", "Distracted"])
bang = st.checkbox("Bang")
json_say = {
  "spoon" :
  {
    "id": "Say",
    "text": tts,
    "expression":
    {
      "type": expression_type,
      "intensity": expression_intensity,
      "gazeMode": expression_gaze_mode
    },
    "bang": bang
  }
}
if st.button("Generate JSON"):
    generated_json = json.dumps(json_say, indent = 2)
    st.text_area("JSON", value=generated_json, height=400)
