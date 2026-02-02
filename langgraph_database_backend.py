from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=groq_api_key,
    temperature=0
)
print("✓ Using model: llama-3.3-70b-versatile")


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)



def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

def get_chat_summary(thread_id):
    """Generate a summary of the chat based on the first user message"""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    
    if messages:
        for msg in messages:
            if isinstance(msg, HumanMessage):
                # Get first user message and limit to 50 chars
                summary = msg.content[:50]
                if len(msg.content) > 50:
                    summary += "..."
                return summary
    
    return f"Chat {str(thread_id)[:8]}"