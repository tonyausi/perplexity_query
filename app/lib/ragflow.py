import os
import logging
from dotenv import load_dotenv
from typing import Union, Iterator, List
from ragflow_sdk.modules.session import Message
from ragflow_sdk import RAGFlow, Session, Chat

load_dotenv()
logger = logging.getLogger(__name__)

RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY")
RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL")
TENDER_KNOWLEDGE_BASE = os.getenv("TENDER_KNOWLEDGE_BASE", "SeismaTender")
TENDER_QUESTION_HEADER = os.getenv(
    "TENDER_QUESTION_HEADER",
    "From the knowledge Base, find the solution to the following requirement:\n\n",
)


# obtain the chat assistant object
def get_chat_assistant(
    api_key=RAGFLOW_API_KEY,
    base_url=RAGFLOW_BASE_URL,
    assistant_name=TENDER_KNOWLEDGE_BASE,
) -> list[Chat]:
    rag_object = RAGFlow(api_key=api_key, base_url=base_url)
    logger.info("RAGFlow object created")
    assistant_list = rag_object.list_chats(name=assistant_name)
    if assistant_list:
        return assistant_list[0]
    else:
        raise ValueError("Assistant not found")


# create an new instance of RAGFlow session with the API key, base URL and the assistant name
def get_chat_assistant_session(
    api_key=RAGFLOW_API_KEY,
    base_url=RAGFLOW_BASE_URL,
    assistant_name=TENDER_KNOWLEDGE_BASE,
    session_name="SeismaTenderSession",
) -> Session:
    assistant = get_chat_assistant(api_key, base_url, assistant_name)
    logger.info(f"assistant fetched with name = {assistant.name}")

    new_session = assistant.create_session(name=session_name)
    logger.info(
        f"Created new session.id: {new_session.id}, "
        f"session.name: {new_session.name}, "
        f"session.messages: {new_session.messages}, "
        f"session.chat_id: {new_session.chat_id}"
    )
    return new_session


# ask a question to the chat assistant session
def ask_questions_to_chat_assistant(
    session: Session, questions: list[str], stream: bool = False
):  # -> Union[Message, Iterator[Message]]:
    output = []
    logger.info(f"stream={stream}")
    for question_raw in questions:
        logger.info(f"Asked raw question: {question_raw}")
        if TENDER_QUESTION_HEADER not in question_raw:
            question = TENDER_QUESTION_HEADER + question_raw
            logger.info(f"Amended question: {question}")
        else:
            question = question_raw
        # message = session.ask(question=question, stream=stream)
        json_data = {"question": question, "stream": stream, "session_id": session.id}
        res = session.post(
            f"/chats/{session.chat_id}/completions", json_data, stream=stream
        )
        logger.info(f"Response status: {res.status_code}")
        if res.status_code == 200:
            output.append([question_raw, res.json()])

    return output


def parse_answer(responses: List) -> dict:
    logger.info(f"responses: {responses}")
    output = {
        "Requirement": [],
        "Supplier explanation / comments": [],
        "Reference": [],
    }
    if responses:
        for parsed_answer in responses:
            question = parsed_answer[0]
            answer = parsed_answer[1]["data"]["answer"]
            reference = (
                parsed_answer[1]["data"].get("reference", {}).get("doc_aggs", "")
            )
            output["Requirement"].append(question)
            output["Supplier explanation / comments"].append(answer)
            output["Reference"].append(reference)
        return output
    else:
        logger.error("Failed to get response from RAG Flow API")
        return {}
