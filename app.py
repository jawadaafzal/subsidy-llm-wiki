import streamlit as st

from src.query import WikiQuery
from src.draft import generate_draft
from src.review import review_draft


st.set_page_config(
    page_title="Pakistan Subsidy Wiki",
    page_icon="📚",
    layout="wide",
)

st.title("Pakistan Government Subsidy Wiki")
st.caption("AI-powered research and knowledge management system")

tab1, tab2 = st.tabs(["Search Wiki", "Generate Draft"])

with tab1:
    st.header("Search Official Sources")

    question = st.text_input(
        "Ask a question about government subsidies"
    )

    if st.button("Search"):
        if question.strip():
            with st.spinner("Searching sources..."):
                wiki = WikiQuery()
                results = wiki.search(question, top_k=5)

            if results:
                for i, result in enumerate(results, 1):
                    st.subheader(f"Result {i}")
                    st.caption(
                        f"Source: {result['source_id']} | "
                        f"Lines: {result['start_line']}-"
                        f"{result['end_line']}"
                    )
                    st.write(result["text"])
                    st.divider()
            else:
                st.warning("No relevant information found.")

with tab2:
    st.header("Generate Wiki Draft")

    draft_question = st.text_input(
        "What Wiki page should Gemini create?",
        key="draft_question",
    )

    if st.button("Generate Draft"):
        if draft_question.strip():
            with st.spinner("Generating and validating draft..."):
                try:
                    generate_draft(draft_question)
                    st.success(
                        "Draft generated. Check the wiki/drafts folder."
                    )
                except Exception as error:
                    st.error(str(error))