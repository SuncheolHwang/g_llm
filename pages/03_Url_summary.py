import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.memory import ConversationTokenBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(
    page_title="Url Summary",
    page_icon="📃",
)

# Gemini 모델 옵션
options = [
    "gemini-2.0-flash-thinking-exp-01-21",
    "gemini-2.0-flash-exp",
]


with st.sidebar:
    selected_option = st.selectbox("Select a model:", options, index=0)
    url_input = st.text_input(
        "URL:", placeholder="Enter the URL of the webpage you want to analyze"
    )

if "url_messages" not in st.session_state:
    st.session_state["url_messages"] = []

llm = ChatGoogleGenerativeAI(
    model=selected_option,
    temperature=0.1,
    streaming=True,
)

memory = ConversationTokenBufferMemory(
    llm=llm,
    max_token_limit=2000,
    return_messages=True,
)


if "url_chat_summary" not in st.session_state:
    st.session_state["url_chat_summary"] = []
else:
    for chat_list in st.session_state["url_chat_summary"]:
        memory.save_context(
            {"input": chat_list["question"]},
            {"output": chat_list["answer"]},
        )


def save_messages(message, role):
    st.session_state["url_messages"].append(
        {
            "message": message,
            "role": role,
        }
    )


def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_messages(message, role)


def paint_history():
    for message in st.session_state["url_messages"]:
        send_message(message["message"], message["role"], save=False)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Answer the question to the point.
            """,
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def load_memory(_):
    return memory.load_memory_variables({})["history"]


def save_context(question, result):
    st.session_state["url_chat_summary"].append(
        {
            "question": question,
            "answer": result,
        }
    )


@st.spinner("Preparing your question...")
def invoke_chain(question):
    context = ""
    if url_input:
        context = process_url(url_input)
        if context:
            question = f"refer to the following webpages to answer your questions:\n\ncontext: {context}\n\nquestion: {question}"

    result = chain.invoke(
        {"question": question},
    )

    st.write(result.content)
    save_context(message, result.content)
    save_messages(result.content, "ai")


def process_url(url):
    try:
        loader = UnstructuredURLLoader(urls=[url])
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(data)

        return "\n".join([doc.page_content for doc in splits])
    except Exception as e:
        st.error(f"An error occurred while processing the URL: {str(e)}")
        return None


st.title("Webpage Summary")

st.markdown(
    """
    <style>
    .big-font {
        font-size:30px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "authentication_status" not in st.session_state:
    st.markdown(
        "<p class='big-font'>You need to log in from the 'Home' page in the left sidebar.</p>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        Welcome!
        
        Use this chatbot to ask questions to an AI about your Questions!
        
        """
    )

    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()

    authentication_status = st.session_state["authentication_status"]
    if authentication_status:
        message = st.chat_input("Ask anything about something...")
        if message:
            send_message(message, "human")
            chain = RunnablePassthrough.assign(history=load_memory) | prompt | llm

            with st.chat_message("ai"):
                invoke_chain(message)
    else:
        st.markdown(
            "<p class='big-font'>You need to log in from the 'Home' page in the left sidebar.</p>",
            unsafe_allow_html=True,
        )
