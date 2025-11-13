import streamlit as st
from pdfminer.high_level import extract_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
import tempfile
import httpx
import os

os.environ["TIKTOKEN_CACHE_DIR"] = r'C:\Users\GenAINGPMIHUSR18\Desktop\LANGCHAIN\token'

# Disable SSL verification for internal TCS GenAI endpoint
client = httpx.Client(verify=False)

# Streamlit setup
st.set_page_config(page_title="RAG PDF Summarizer", page_icon="📚")
st.title("📄 RAG-powered PDF Summarizer (TCS GenAI Lab)")

# Enter API key
api_key = st.text_input("🔑 Enter your TCS GenAI API Key", type="password")

if api_key:
    # Step 1: Upload PDF
    upload_file = st.file_uploader("📤 Upload a PDF", type="pdf")

    if upload_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(upload_file.read())
            temp_file_path = temp_file.name

        # Step 2: Extract text
        with st.spinner("📖 Extracting text from PDF..."):
            raw_text = extract_text(temp_file_path)

        # Step 3: Chunk the text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(raw_text)

        # Step 4: Initialize LLM + embeddings
        with st.spinner("🧠 Initializing LLM and Embeddings..."):
            llm = ChatOpenAI(
                base_url="https://genailab.tcs.in",
                model="azure_ai/genailab-maas-DeepSeek-V3-0324",
                api_key="sk-6VKZkm_dZltZ3iEoHqvJlQ",
                http_client=client
            )

            embedding_model = OpenAIEmbeddings(
                base_url="https://genailab.tcs.in",
                model="azure/genailab-maas-text-embedding-3-large",
                api_key="sk-6VKZkm_dZltZ3iEoHqvJlQ",
                http_client=client
            )

        # Step 5: Create vector store
        with st.spinner("🔍 Creating and saving vector store..."):
            vectordb = Chroma.from_texts(chunks, embedding_model, persist_directory="./chroma_index")
            vectordb.persist()

        # Step 6: Create retriever and RAG chain
        retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        # Step 7: Ask summarization prompt
        summary_prompt = "Please summarize this document based on the key topics and insights." \
        "generate this from the pdf uploaded Relevance & Tech Landscape (30), Innovation & Creativity (15), Feasibility & Scalability (15), "
        with st.spinner("⚡ Running RAG summarization..."):
            result = rag_chain.invoke(summary_prompt)

        # Step 8: Display result
        st.subheader("📝 Summary")
        st.write(result["result"] if isinstance(result, dict) and "result" in result else result)

else:
    st.info("👆 Please enter your TCS GenAI API key to begin.")
