import logging
from app.main import query_perplexity_tender_openai
from app.lib.ragflow import (
    get_chat_assistant_session,
    get_chat_assistant,
    ask_questions_to_chat_assistant,
    parse_answer,
)


logger = logging.getLogger(__name__)


def _test_query_perplexity_tender_valid_input():
    result = query_perplexity_tender_openai(
        "How many phases are proposed for VicScreen regarding "
        "architecture activities?"
    )
    # result = query_perplexity_tender_openai("Where are Seisma Group's offices located?")
    # result = query_perplexity_tender_openai(
    #     "How many phases are proposed for VicScreen regarding "
    #     "architecture activities?",
    #     model="sonar-pro"
    # )
    # result = query_perplexity_tender_openai(
    #     "How many phases are proposed for VicScreen regarding architecture activities?",
    #     model="sonar"
    # )
    # result = query_perplexity_tender_openai(
    #     "How many phases are proposed for VicScreen regarding architecture activities?",
    #     model="sonar-deep-research"
    # )
    assert result is not None
    # assert isinstance(result, dict)
    # assert "perplexity" in result


def test_ragflow_create_session():
    session = get_chat_assistant_session()
    assert session is not None
    # delete the session
    assistant = get_chat_assistant()
    assistant.delete_sessions(ids=[session.id])


def test_ragflow_ask_questions():
    session = get_chat_assistant_session()
    questions = [
        (
            "Privileged users are required to authenticate using Multi-Factor Authentication (MFA) "
            "or implement an alternative compensatory control to access the solution."
        ),
        (
            "All modifications to the solution must undergo testing and receive approval "
            "in a test environment before deployment to production."
        ),
    ]
    qanda = ask_questions_to_chat_assistant(
        session=session,
        questions=questions,
    )
    assert qanda is not None
    for parsed_answer in qanda:
        assert parsed_answer is not None
        logger.info("############################################")
        logger.info(f"input question: {parsed_answer[0]}")
        # logger.info(f"parsed_raw: {parsed_answer[1]}")
        logger.info(f"parsed_answer: {parsed_answer[1]['data']['answer']}")
        logger.info(
            f"reference document: {parsed_answer[1]['data']['reference']['doc_aggs']}"
        )
    result = parse_answer(qanda)
    assert result is not None
    logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    logger.info(f"parsed result: {result}")

    """# delete the session
    assistant = get_chat_assistant()
    assistant.delete_sessions(ids=[session.id])"""
