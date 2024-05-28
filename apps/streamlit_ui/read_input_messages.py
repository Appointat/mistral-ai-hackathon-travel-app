import json

import streamlit as st


def read_input_messages():
    try:
        with open('apps/streamlit_ui/human_messages_tmp.txt', 'r') as file:
            new_human_messages = file.readlines()

        if 'human_messages' not in st.session_state:
            st.session_state['human_messages'] = []

        # FIFO queue
        current_human_messages = {
            json.dumps(msg) for msg in st.session_state['human_messages']
        }
        new_messages = [
            msg for msg in new_human_messages if msg not in current_human_messages
        ]

        for human_message in new_messages:
            st.session_state['human_messages'].append(
                json.loads(human_message)['message']
            )

        # Clear the file
        with open('apps/streamlit_ui/human_messages_tmp.txt', 'w') as file:
            file.truncate(0)
    except FileNotFoundError:
        pass
