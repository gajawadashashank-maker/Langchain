import streamlit as st
from langchain_openai import ChatOpenAI
import httpx

# Streamlit UI
st.title("💬 LangChain Chat Demo - DeepSeek (TCS GenAI Lab)")

# Input prompt
prompt = st.text_area("Enter your prompt:", "Explain what is SwiftUI")

# On button click
if st.button("Ask"):
    with st.spinner("Fetching response from DeepSeek..."):
        try:
            # Create httpx client with SSL disabled
            client = httpx.Client(verify=False)

            # Initialize LLM
            llm = ChatOpenAI(
                base_url="https://genailab.tcs.in",
                model="azure_ai/genailab-maas-DeepSeek-V3-0324",
                api_key="sk-6VKZkm_dZltZ3iEoHqvJlQ",
                http_client=client
            )

            # Get response
            response = llm.invoke(prompt)

            # Display output
            st.subheader("🧠 Response:")
            st.write(response.content if hasattr(response, "content") else response)

        except Exception as e:
            st.error(f"❌ Error: {e}")
