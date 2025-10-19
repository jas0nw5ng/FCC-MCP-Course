import streamlit as st
import requests
from sseclient import SSEClient
import httpx
import uuid

# MCP server base URL
MCP_BASE_URL = "http://localhost:24242/mcp"

# Tool endpoints
TOOLS = {
    "News Search": "fcc_news_search",
    "YouTube Search": "fcc_youtube_search",
    "Secret Message": "fcc_secret_message"
}

# Initialize session ID once per user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Streamlit UI
st.title("🧠 FreeCodeCamp Chatbot")
st.write("Ask me about FreeCodeCamp news, YouTube videos, or get a secret message!")

# Tool selector
selected_tool = st.selectbox("Choose a tool", list(TOOLS.keys()))

# Input fields
if selected_tool != "Secret Message":
    query = st.text_input("Enter your search query")
    max_results = st.slider("Max results", 1, 10, 3)
else:
    query = None
    max_results = None

# Submit button
if st.button("Run Tool"):
    tool_name = TOOLS[selected_tool]

    # Build payload dynamically
    payload = {
        "id": str(uuid.uuid4()),
        "jsonrpc": "2.0",
        # "tool": tool_name,
        "method": tool_name,
        "session_id": st.session_state.session_id,
        "params": {
            "query": "python",
            "max_results": 3
        }
    }

    # if query:
    #     payload["input"]["query"] = query
    # if max_results:
    #     payload["input"]["max_results"] = max_results

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        # "X-Session-ID": st.session_state.session_id
        "x-session-id": st.session_state.session_id
    }

    try:
        with httpx.stream("POST", MCP_BASE_URL, headers=headers, json=payload) as response:
            for line in response.iter_lines():
                if line:
                    st.write(line)

        response.raise_for_status()
        result = response.json()

        session_id = response.headers.get('x-session-id')
        print(f"Session ID: {session_id}")

        st.subheader("🔍 Results")
        if isinstance(result, list):
            for item in result:
                if "title" in item and "url" in item:
                    st.markdown(f"- [{item['title']}]({item['url']})")
                elif "message" in item:
                    st.info(item["message"])
        elif isinstance(result, str):
            st.success(result)
        else:
            st.write(result)

    except Exception as e:
        st.error(f"Error: {e}")


# streamlit run chatbot_feed.py -- --debug --mcp_url http://localhost:24242/mcp --default_tool fcc_news_search

# TODO
# data: {"jsonrpc":"2.0","id":"cf60c73e-c7a7-4abe-afd4-3d9bd6194fd7","error":{"code":-32602,"message":"Invalid request parameters","data":""}}