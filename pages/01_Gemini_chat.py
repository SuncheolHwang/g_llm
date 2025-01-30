import streamlit as st
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(
    page_title="Gemini",
    page_icon="🤖",
)

# Gemini 모델 옵션
options = [
    "gemini-2.0-flash-thinking-exp-01-21",
    "gemini-2.0-flash-exp",
]

with st.sidebar:
    selected_option = st.selectbox("Select a model:", options, index=0)

    prompt_text = st.text_area(
        "Prompt",
        """
Description: As a hardware and software expert, your job is to provide detailed and easy-to-understand explanations in Korean for inquiries or statements. 
You need to explain complex concepts related to hardware and software in an easy-to-understand manner so that they can be understood by a wide audience. 
Your goal is not only to simplify the explanation, but also to provide relevant examples wherever possible to enhance the questioner's understanding.

    Role: Hardware and software expert
    Goal: Help the questioner gain a comprehensive understanding of hardware and software concepts.

    Guidelines
    1. break down complex technical topics into simple, easy-to-understand explanations.
    2. Use clear, accessible language that individuals without a technical background can understand.
    3. Provide real-world examples or hypothetical scenarios to illustrate explanations and make abstract concepts concrete.
    4. Explain the "how" and "why" of processes and technologies to deepen the questioner's understanding.
    5. When discussing software, explain how the software interacts with hardware to perform its function.
""".strip(),
    )

if "gemini_messages" not in st.session_state:
    st.session_state["gemini_messages"] = []

llm = ChatGoogleGenerativeAI(
    model=selected_option,
    temperature=0.1,
    streaming=True,
)

memory = ConversationBufferMemory(
    llm=llm,
    max_token_limit=2000,
    return_messages=True,
)

if "gemini_chat_summary" not in st.session_state:
    st.session_state["gemini_chat_summary"] = []
else:
    for chat_list in st.session_state["gemini_chat_summary"]:
        memory.save_context(
            {"input": chat_list["question"]},
            {"output": chat_list["answer"]},
        )


def save_messages(message, role):
    st.session_state["gemini_messages"].append(
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
    for message in st.session_state["gemini_messages"]:
        send_message(message["message"], message["role"], save=False)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
            {prompt_text}
            """,
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def load_memory(_):
    return memory.load_memory_variables({})["history"]


def save_context(question, result):
    st.session_state["gemini_chat_summary"].append(
        {
            "question": question,
            "answer": result,
        }
    )


@st.spinner("Preparing your question...")
def invoke_chain(question):
    result = chain.invoke(
        {"question": question},
    )
    print(result.content)
    st.write(result.content)
    save_context(message, result.content)
    save_messages(result.content, "ai")


st.title("Gemini Chatbot")

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
