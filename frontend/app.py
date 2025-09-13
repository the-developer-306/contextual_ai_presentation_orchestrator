import streamlit as st
import requests
import json
import os

# FastAPI backend URL
API_BASE_URL = os.getenv("API_BASE_URL")
# API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")


st.set_page_config(
    page_title="AI Presentation Orchestrator",
    page_icon="",
    layout="wide"
)

st.title(" Contextual AI Presentation Orchestrator")

# ---------------- LOGIN ----------------
st.sidebar.header(" Login")

if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["user"] = None

# Default headers
headers = {}



# Login form
if not st.session_state["token"]:
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"email": email, "password": password},
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user")
                if token:
                    st.session_state["token"] = token
                    st.session_state["user"] = (
                        user if user and isinstance(user, dict)
                        else {"email": email, "role": data.get("role", "Unknown")}
                    )
                    st.sidebar.success(f" Logged in as {st.session_state['user'].get('role', 'Unknown')}")
                    st.rerun()
                else:
                    st.sidebar.error(" Login succeeded but token missing in response.")
            else:
                try:
                    err = response.json()
                    st.sidebar.error(f" Login failed: {err.get('detail') or err}")
                except Exception:
                    st.sidebar.error(f" Login failed: status {response.status_code}")
        except Exception as e:
            st.sidebar.error(f" Error: {e}")
    st.stop()

# Now logged in
if st.session_state["token"] and st.session_state.get("user"):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    st.sidebar.markdown(
        f" **User:** {st.session_state['user'].get('email', 'Unknown')}  \n"
        f" **Role:** {st.session_state['user'].get('role', 'Unknown')}"
    )
else:
    st.sidebar.warning("Not fully logged in. Please login again.")
    st.stop()



# ---------------- Permission Mapping ----------------
role = st.session_state["user"].get("role", "")
PERMISSIONS = {
    "Executive": {"upload": True, "generate": True, "download": True},
    "Senior Manager": {"upload": True, "generate": True, "download": True},
    "Analyst": {"upload": False, "generate": True, "download": True},
    "Junior Staff": {"upload": False, "generate": False, "download": False}
}
perms = PERMISSIONS.get(role, {"upload": False, "generate": False, "download": False})

st.sidebar.markdown("**Allowed actions:**")
st.sidebar.markdown(f"- Upload: {'Yes' if perms['upload'] else 'No'}")
st.sidebar.markdown(f"- Generate: {'Yes' if perms['generate'] else 'No'}")
st.sidebar.markdown(f"- Download: {'Yes' if perms['download'] else 'No'}")

# Logout button
if st.session_state.get("token"):
    if st.sidebar.button(" Logout"):
        st.session_state["token"] = None
        st.session_state["user"] = None
        st.sidebar.success(" Logged out successfully")
        st.rerun()

# ---------------- UPLOAD DOCS ----------------
st.subheader(" Step 1: Upload Documents")
if not perms["upload"]:
    st.info("You do not have permission to upload documents.")
    uploaded_files = None
else:
    uploaded_files = st.file_uploader(
        "Upload multiple documents (PDF/DOCX/TXT/MD):",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True
    )

if uploaded_files and perms["upload"] and st.button(" Upload & Process Documents"):
    with st.spinner("Uploading and processing documents..."):
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {st.session_state['token']}"})

        files = []
        for f in uploaded_files:
            f.seek(0)
            file_bytes = f.read()  # read into bytes
            files.append(
                ("files", (f.name, file_bytes, f.type or "application/octet-stream"))
            )

        try:
            response = session.post(f"{API_BASE_URL}/upload-doc", files=files, timeout=120)
            if response.status_code == 200:
                st.success(" Documents uploaded and processed successfully!")
                # st.json(response.json())
            else:
                st.error(f" Upload failed: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f" Error: {e}")

st.divider()

# ---------------- GENERATE PPT ----------------
st.subheader(" Step 2: Generate Presentation")
topic = st.text_input("Enter a topic for your presentation:", "Renewable Energy Storage")

if not perms["generate"]:
    st.info("You do not have permission to generate presentations.")
else:
    if st.button(" Generate Presentation"):
        with st.spinner("Generating presentation via multi-agent orchestration..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/generate-presentation",
                    params={"topic": topic},
                    headers=headers,
                    timeout=600
                )
                if response.status_code == 200:
                    result = response.json()
                    st.session_state["ppt_json"] = result.get("ppt_json")

                    st.success(" Presentation generated successfully!")
                    if st.session_state["ppt_json"]:
                        st.success("Presentation is ready for download below")
                    else:
                        st.info("No JSON returned.")
                elif response.status_code in (401, 403):
                    msg = response.json()
                    st.error(f" {msg.get('detail') or msg}")
                else:
                    st.error(f" Generation failed: status {response.status_code}")
            except Exception as e:
                st.error(f" Error: {e}")

# ---------------- DOWNLOAD PPT ----------------
if perms["download"] and st.session_state.get("ppt_json"):
    if st.button(" Download PPT"):
        with st.spinner("Preparing your PPT..."):
            try:
                dl_response = requests.post(
                    f"{API_BASE_URL}/download-ppt",
                    json=st.session_state["ppt_json"],
                    headers=headers,
                    timeout=300
                )
                if dl_response.status_code == 200:
                    st.download_button(
                        label="📂 Save PPT File",
                        data=dl_response.content,
                        file_name="AI_Presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                else:
                    st.error(f" Download failed: {dl_response.status_code} {dl_response.text}")
            except Exception as e:
                st.error(f" Error: {e}")


st.divider()

# ---------------- STATUS ----------------
if "ppt_path" in st.session_state and st.session_state["ppt_path"]:
    st.success(" Your PPT is ready! Scroll up to download it.")
