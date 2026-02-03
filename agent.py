from typing import Dict, List
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

# LLM (Ollama – local)
llm = Ollama(
    model="llama3.2:3b-instruct-q4_K_M",
    temperature=0.6,
)

# Agent Persona Prompt
SYSTEM_PROMPT = """
You are an older person who is not very good with technology.
You are polite, cautious, and slightly worried.
You believe you are talking to a bank or customer support representative.

Rules you must follow:
- NEVER say you think this is a scam
- NEVER say you are an AI
- NEVER accuse the other person
- Ask simple clarification questions
- Respond in clear, simple English
- Sound realistic and human
- Keep messages short and natural
- Write responses as a single paragraph only
- Do NOT use line breaks, bullet points, or lists
- Do NOT put technical words in quotation marks
- Avoid repeating the same sentence structure across turns
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# Per-session chains (each has its own conversation memory)
_chains: Dict[str, LLMChain] = {}


def _get_or_create_chain(session_id: str) -> LLMChain:
    """Get or create an LLM chain with its own memory for this session."""
    if session_id in _chains:
        return _chains[session_id]
    memory = ConversationBufferMemory(
        memory_key="history",
        return_messages=True,
    )
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=False,
    )
    _chains[session_id] = chain
    return chain


def generate_reply(session_id: str, user_message: str) -> str:
    """
    Generate a human-like reply to the scammer message.
    Uses session-scoped conversation memory so each session has its own history.
    """
    chain = _get_or_create_chain(session_id)
    response = chain.predict(input=user_message)
    return response.strip() if response else ""


def cleanup_chains_for_sessions(session_ids: List[str]) -> None:
    """Drop in-memory chains for the given session ids (e.g. after session cleanup)."""
    for sid in session_ids:
        _chains.pop(sid, None)
