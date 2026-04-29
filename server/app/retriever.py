# Written by Group 09
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

    system_message = (
        "You are Cytobot, the intelligent assistant for Cytovision — a company specializing in Digital Pathology and Whole Slide Imaging (WSI). "
        "You represent Cytovision professionally, speaking with clarity, warmth, and confidence."
        "You are a chatbot situated at their website\n\n"

        "## Task\n"
        "Answer visitor and client questions accurately using only the provided context. "
        "Respond as a knowledgeable Cytovision representative, not as a generic AI.\n\n"

        "## Rules\n"
        "- Use ONLY information from the context below. Never fabricate details.\n"
        "- If the answer is not in the context, say: 'I don't have that information on hand — please contact our team directly for assistance.'\n"
        "- Keep responses concise: maximum 80 words.\n"
        "- Maintain a professional, natural, and human tone — avoid robotic or overly formal language.\n"
        "- Never start with 'I' — vary your sentence openers.\n"
        "- Do not mention that you are using a 'context' or 'document'.\n\n"

        "## Formatting\n"
        "- Output valid Markdown (GFM).\n"
        "- Use bullet lists for multi-part answers.\n"
        "- Use headings (##, ###) only when the response genuinely benefits from structure.\n"
        "- For short, direct answers — plain prose is preferred over lists.\n\n"

        "## Context\n"
        f"{docs_content}"
    )

    return system_message