from dotenv import load_dotenv

from langchain_mistralai import ChatMistralAI

load_dotenv()

llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.7
)


def get_ai_response(messages):

    conversation = [
        (
            "system",
            """
You are Nexus AI.

Remember previous messages in the conversation.

Use chat history when answering.

If the user tells you a name, preference, or fact,
remember it during the current chat session.
"""
        )
    ]

    for msg in messages:

        if msg.role == "user":

            conversation.append(
                (
                    "human",
                    msg.content
                )
            )

        else:

            conversation.append(
                (
                    "ai",
                    msg.content
                )
            )

    response = llm.invoke(
        conversation
    )

    return response.content