from typing import List

from langchain_core.documents import Document
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from scripts import get_faq_collection, get_kb_collection


faq_collection, kb_collection = get_faq_collection(), get_kb_collection()

def faq_retriever(query, threshold = 0.6) -> List[Document]:
    ret = faq_collection.similarity_search_with_relevance_scores(query, k=5)

    if not ret:
        return []

    faqs = [doc for doc, s in ret if s >= threshold]
    return faqs

def kb_retriever(query) -> List[Document]:
    return kb_collection.similarity_search(
        query,
        k=3
    )

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    last_query = request.state["messages"][-1].text
    retrieved_docs = kb_retriever(last_query)

    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # TODO: prompt injection prevention
    system_message = (
        "You are the AI assistant for Cytovision, a company specializing in Digital Pathology and Whole Slide Imaging (WSI)."

        "Task:"
        "Answer visitor and client questions accurately using the provided context."

        "Rules:"
        "- Use ONLY the information in the context."
        "- If the answer is not in the context, say you do not have enough information."
        "- Answer in a professional tone."
        "- Use a maximum of 60 words"

        "- Output MUST be valid Markdown (CommonMark)."
        "- Use headings (##, ###, ####) where appropriate."
        "- Use bullet lists when applicable."

        "Context:"
        f"\n\n{docs_content}"
    )

    return system_message