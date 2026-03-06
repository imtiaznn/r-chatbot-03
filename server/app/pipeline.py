import argparse

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

from scripts import get_embeddings
from app.retriever import faq_retriever, prompt_with_context

FAQ_DISABLED = False
LLM_DISABLED = False

FAQ_THRESHOLD = 0.85

# TODO: set API key as env variable in production
checkpointer = InMemorySaver()
model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.1,
    max_tokens=1000,
    timeout=30,
)

embeddings = get_embeddings()
agent = create_agent(
    model, 
    tools=[],
    middleware=[prompt_with_context],
    checkpointer=checkpointer
)


def process_user_message(user_query, session_id):
    print(f"---- PROCESSING {session_id}: {user_query}")

    # Agent configs
    messages = [{
            "role" : "user",
            "content" : user_query
        }]
    
    config = {
        "configurable": {"thread_id": "1"}
    }
    
    response = ""

    # Perform similarity search in vector database (FAQ)
    if not FAQ_DISABLED:
        print("---- SEARCHING FAQS...")
        context_query = " ".join(
            m["content"] for m in messages[-3:]
        )

        faqs = faq_retriever(context_query, FAQ_THRESHOLD)
        if faqs:
            faq_a = faqs[0].metadata.get("answer", "")
            print(f"---- RETRIEVED FAQS: {[faq.id for faq in faqs]}\n\n")

            response = faq_a
            return response

    # Forward query to LLM if no FAQ matches found
    if not LLM_DISABLED:
        print("---- PROMPTING LLM...")
    
        # Streaming
        for message_chunk, metadata in agent.stream(
            {"messages":messages}, 
            stream_mode="messages", 
            config=config
        ):
        
            if message_chunk.content:
                print(message_chunk.content, end="", flush=True)
                response += message_chunk.content

    return response