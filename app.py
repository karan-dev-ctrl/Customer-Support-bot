import uuid

import streamlit as st

from bot.pipeline import handle_message

st.set_page_config(page_title="Support Bot", page_icon="💬")
st.title("💬 Support Bot")

with st.sidebar:
    show_debug = st.checkbox("Show model details", value=True)
    if st.button("New chat"):
        st.session_state.clear()
        st.rerun()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.history = []

# Draw the conversation so far
for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.write(turn["text"])
        if show_debug and turn.get("debug"):
            st.caption(turn["debug"])

# Handle a new message
if prompt := st.chat_input("How can I help you?"):
    result = handle_message(prompt, st.session_state.session_id)
    st.session_state.history.append({"role": "user", "text": prompt})
    st.session_state.history.append({
        "role": "assistant",
        "text": result["reply"],
        "debug": (f"route={result['route']} · intent={result['intent']} "
                  f"({result['intent_conf']}) · sentiment={result['sentiment']} "
                  f"({result['sentiment_conf']})"),
    })
    st.rerun()