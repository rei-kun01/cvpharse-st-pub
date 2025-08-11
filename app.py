import streamlit as st
import requests

st.set_page_config(page_title="CV Analyzer", page_icon="📄")
st.title("📄 CV Analyzer Baseline Testing")

# --- Track parser selection changes ---
if "last_parser" not in st.session_state:
    st.session_state.last_parser = None
if "uploaded_file_cache" not in st.session_state:
    st.session_state.uploaded_file_cache = None

st.sidebar.header("Choose a parser")
parser_type = st.sidebar.selectbox(
    "Parser Type", ["LLM-based", "Traditional"], index=0)

uploaded_file = st.file_uploader(
    "Upload your CV (.pdf or .docx)", type=["pdf", "docx"])

# Store uploaded file in session state
if uploaded_file:
    st.session_state.uploaded_file_cache = uploaded_file


API_URL = (
    "http://localhost:8000/analyze"
    if parser_type == "Traditional"
    else "http://localhost:8000/llm-cvpharse"
)

if st.session_state.uploaded_file_cache:
    with st.spinner("Sending file to backend..."):
        file_obj = st.session_state.uploaded_file_cache
        files = {
            "file": (
                file_obj.name,
                file_obj.read(),
                file_obj.type
            )
        }
        response = requests.post(API_URL, files=files)
    if response.status_code == 200:
        result = response.json()
        if "error" in result:
            st.error(result["error"])
        else:
            st.success("CV analyzed successfully!")
            st.write(f"Detected language: **{result['language']}**")

            st.subheader("CV Extraction Results")
            result = result["response"]["text"][0]
            # st.json(result)

            if result:
                st.subheader("👤 Personal Information")
                st.markdown(f"**Name**: {result.get('name', 'Not detected')}")
                st.markdown(
                    f"**Email**: {result.get('email', 'Not detected')}")
                st.markdown(
                    f"**Phone**: {result.get('phone', 'Not detected')}")

                st.subheader("📝 Summary")
                st.markdown(result.get("summary", "Not provided."))

                st.subheader("🎓 Education")
                education = result.get("education", [])
                if education:
                    st.markdown("\n".join(f"- {edu}" for edu in education))
                else:
                    st.markdown("Not detected.")

                st.subheader("💼 Work Experience")
                work_experience = result.get("work_experience", [])
                if work_experience:
                    st.markdown(
                        "\n".join(f"- {exp}" for exp in work_experience))
                else:
                    st.markdown("Not detected.")

                st.subheader("🛠 Skills")
                skills = result.get("skills", [])
                if skills:
                    st.markdown("\n".join(f"- {skill}" for skill in skills))
                else:
                    st.markdown("Not detected.")

            # for key, value in result["personal_info"].items():
            #     st.markdown(f"- **{key}**: {value}")

            # st.subheader("🎓 Education")
            # st.markdown("\n".join(
            #     f"- {edu}" for edu in result["education"]) if result["education"] else "Not detected.")

            # st.subheader("🛠 Skills")
            # st.markdown("\n".join(
            #     f"- {skill}" for skill in result["skills"]) if result["skills"] else "Not detected.")
    else:
        st.error("Backend error: " + response.text)
