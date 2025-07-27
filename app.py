import streamlit as st
from backend import ingest_file, crawl_website, index_data
import pandas as pd

st.set_page_config(page_title="Doc Chatbot", layout="centered")

# ---------- Custom CSS for styling ----------
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-bottom: 1.5em;
        background: #f9f9f9;
        border-radius: 12px;
        padding: 10px 16px;
    }
    .bubble-user {
        align-self: flex-end;
        background: #dcf8c6;
        color: #222;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 16px;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-right: 8px;
    }
    .bubble-ai {
        align-self: flex-start;
        background: #e9e9eb;
        color: #222;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 16px;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-left: 8px;
    }
    .chat-label {
        font-weight: bold;
        font-size: 0.95em;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
    }
    .icon {margin-right: 6px;}
    </style>
""", unsafe_allow_html=True)

# ---------- Title & Tagline ----------
st.title("📄 Docs or Links. One Bot. All Your Answers.")
st.markdown("""
<p style='font-size:17px; color:gray; margin-top:-10px;'>
Drop a file. Paste a URL. Discover answers instantly with AI.
</p>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("### 📂 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload a File", type=["csv", "xlsx", "xls", "docx", "pdf"])
url = st.sidebar.text_input("🔗 Or enter a website URL")

# ---------- Session State ----------
if 'doc_context' not in st.session_state:
    st.session_state['doc_context'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'data_type' not in st.session_state:
    st.session_state['data_type'] = None
if 'csv_info' not in st.session_state:
    st.session_state['csv_info'] = None
if 'web_snippet' not in st.session_state:
    st.session_state['web_snippet'] = None

# ---------- Ingestion ----------
if uploaded_file:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        file_text = ingest_file(uploaded_file.name)
        st.session_state['doc_context'] = file_text
        st.session_state['data_type'] = 'file'
        st.sidebar.success("✅ File uploaded and indexed!")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading file: {str(e)}")

elif url:
    with st.spinner("🌐 Crawling website..."):
        text = crawl_website(url)
        st.session_state['doc_context'] = text
        st.session_state['data_type'] = 'web'
        st.session_state['web_snippet'] = text[:500]
        st.sidebar.success("✅ Website crawled and indexed!")

# ---------- Data Display ----------
if st.session_state['doc_context']:
    st.subheader("🧾 Data Details")

    if st.session_state['data_type'] == 'file':
        st.write("**Extracted Text Snippet:**")
        st.code(st.session_state['doc_context'][:500])

    elif st.session_state['data_type'] == 'web' and st.session_state['web_snippet']:
        st.write("**Website Text Snippet:**")
        st.code(st.session_state['web_snippet'])

    # ---------- Chat Interface ----------
    st.markdown("---")
    st.markdown("### 💬 Chat with your Data")

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state['chat_history']:
        if msg['role'] == 'user':
            st.markdown(f"""
                <div class="bubble-user">
                    <div class="chat-label"><span class="icon">🧑‍💻</span>You</div>
                    <div>{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            ai_content = ""
            if isinstance(msg['content'], dict):
                if 'processor_output' in msg['content']:
                    ai_content = msg['content']['processor_output']
                elif 'processor_raw_response' in msg['content']:
                    ai_content = msg['content']['processor_raw_response']
                elif 'processor_error' in msg['content']:
                    ai_content = f"<span style='color:red'>AI Error: {msg['content']['processor_error']}</span>"
                elif 'error' in msg['content']:
                    ai_content = f"<span style='color:red'>AI Error: {msg['content']['error']}</span>"
                else:
                    ai_content = str(msg['content'])
            else:
                ai_content = str(msg['content'])

            st.markdown(f"""
                <div class="bubble-ai">
                    <div class="chat-label"><span class="icon">🤖</span>AI</div>
                    <div>{ai_content}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
        with st.spinner("AI is typing..."):
            ai_response = index_data(f"Context: {st.session_state['doc_context']}\nUser: {user_input}")
        st.session_state['chat_history'].append({'role': 'bot', 'content': ai_response})
        st.rerun()
else:
    st.info("Upload a document (CSV, Excel, Word, PDF) or enter a website URL to begin chatting.")

# ---------- Footer ----------
st.markdown("""
<hr style='margin-top:30px;'>
<p style='text-align:center; color:gray; font-size:13px'>
Made with ❤️  Monika &  AI
</p>
""", unsafe_allow_html=True)
