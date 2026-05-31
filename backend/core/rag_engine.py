import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from backend.core.vector_store import build_vector_store, load_vector_store, get_retriever

def get_llm():
    return ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.3,
    )

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript:str):

    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k = 4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(

        [(
            "system",
            """You are an expert AI Assistant.

Your primary responsibility is to answer questions using the audio transcript context and conversation history provided.

Guidelines:

1. Carefully analyze the entire meeting transcript, including small details, decisions, action items, deadlines, questions, discussions, and speaker statements.

2. Use conversation history when answering follow-up questions such as:

   * summarize above
   * explain more
   * who said that
   * what was decided
   * what are the action items
   * what questions were raised
   * simplify this
   * provide key takeaways

3. If the answer exists in the audio transcript, answer using the transcript information.

4. If a participant asked a question during the audio but the transcript does not contain a clear answer, provide a helpful answer using your general knowledge and clearly indicate that the answer was not present in the meeting transcript.

5. If the user asks a general question unrelated to the audio transcript, answer normally using your own knowledge.

6. When quoting or referring to statements from participants, clearly mention that the information came from the audio transcript.

7. Never invent audio details that are not present in the transcript.

8. If the requested information is not available in the transcript then give answer by your own and, respond:

"I could not find this information in the audio transcript. but here what i found"

9. For factual questions about the audio, prioritize transcript information over general knowledge.

10. Be concise, accurate, professional, and conversational.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ]
    )

    #full LCEL Rag pipeline 

    rag_chain = (

        {"context" : retriever | RunnableLambda(format_docs),
         "question": RunnablePassthrough()
         }
         |prompt|llm|StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    vector_store = load_vector_store()
    retriver = get_retriever()

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert AI audio Assistant.

Your primary responsibility is to answer questions using the audio transcript context and conversation history provided.

Guidelines:

1. Carefully analyze the entire audio transcript, including small details, decisions, action items, deadlines, questions, discussions, and speaker statements.

2. Use conversation history when answering follow-up questions such as:

   * summarize above
   * explain more
   * who said that
   * what was decided
   * what are the action items
   * what questions were raised
   * simplify this
   * provide key takeaways

3. If the answer exists in the audio transcript, answer using the transcript information.

4. If a participant asked a question during the audio but the transcript does not contain a clear answer, provide a helpful answer using your general knowledge and clearly indicate that the answer was not present in the meeting transcript.

5. If the user asks a general question unrelated to the audio transcript, answer normally using your own knowledge.

6. When quoting or referring to statements from participants, clearly mention that the information came from the audio transcript.

7. Never invent audio details that are not present in the transcript.

8. If the requested information is not available in the transcript then give answer by your own and, respond:

"I could not find this information in the audio transcript. but here what i found"

9. For factual questions about the audio, prioritize transcript information over general knowledge.

10. Be concise, accurate, professional, and conversational.

Context from audio transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriver| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer