from typing import Dict, List, Tuple
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, AIMessage

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

def generate_reply(chat_history: List[Dict[str, str]], user_message: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Generate a human-like reply to the scammer message.
    Uses the chat history passed from the database to maintain context statelessly.
    """
    memory = ConversationBufferWindowMemory(
        memory_key="history",
        return_messages=True,
        k=10,  # Keep only the last 10 messages to prevent LLM context overflow
    )
    
    # Pre-populate memory with existing history
    for msg in chat_history:
        if msg["role"] == "human":
            memory.chat_memory.add_user_message(msg["content"])
        elif msg["role"] == "ai":
            memory.chat_memory.add_ai_message(msg["content"])
            
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        verbose=False,
    )
    
    response = chain.predict(input=user_message)
    reply = response.strip() if response else ""
    
    # Append the new interaction to the history
    chat_history.append({"role": "human", "content": user_message})
    chat_history.append({"role": "ai", "content": reply})
    
    # Enforce window size manually on the saved state as well
    if len(chat_history) > 20: # 10 turns
        chat_history = chat_history[-20:]
        
    return reply, chat_history
