from fastapi import FastAPI, UploadFile, File, Response, HTTPException
import requests
import yaml
import os
from openai import OpenAI
import logging
from logging.config import dictConfig
from dotenv import load_dotenv
from .template import SYSTEM_CONTENT, USER_CONTENT_TEMPLATE
import pandas as pd
from io import BytesIO
from .lib.ragflow import (
    ask_questions_to_chat_assistant,
    get_chat_assistant_session,
    parse_answer,
)


logfile_path = os.path.join(os.path.dirname(__file__), "logging.yaml")


# load the logging configuration from the logging.yaml file
def load_logging_config(logfile_path):
    with open(logfile_path, "r") as f:
        dictConfig(yaml.safe_load(f))


load_logging_config(logfile_path)
logger = logging.getLogger(__name__)


app = FastAPI()

load_dotenv()

PERPLEXITY_API_URL = os.getenv(
    "PERPLEXITY_API_URL", "https://api.perplexity.ai/v1/chat/completions"
)
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "your_api_key_here")
EXPOSED_PORT = os.getenv("EXPOSED_PORT", 11012)


@app.post("/query-perplexity-tender/")
async def query_perplexity_tender(query: str, model="r1-1776"):
    user_query = USER_CONTENT_TEMPLATE.render({"user_content": query})
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "user", "content": user_query},
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
        "top_p": 0.9,
        "search_domain_filter": None,
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "year",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "response_format": None,
    }
    logger.info(f"payload = {payload}")
    logger.info(f"PERPLEXITY_API_KEY: {PERPLEXITY_API_KEY}")
    logger.info(f"PERPLEXITY_API_URL: {PERPLEXITY_API_URL}")
    response = await requests.post(
        PERPLEXITY_API_URL,
        headers={
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    if response.status_code == 200:
        logger.info(f"response.json(): {response.json()}")
        return response.json()
    else:
        logger.error(f"response.status_code={response.status_code}")
        logger.error(f"response.json()={response.json()}")
        return {"error": "Failed to get response from Perplexity API"}


@app.post("/query-perplexity-tender-openai/")
async def query_perplexity_tender_openai(query: str, model="r1-1776"):
    user_query = USER_CONTENT_TEMPLATE.render({"user_content": query})
    messages = [
        {
            "role": "system",
            "content": SYSTEM_CONTENT,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]
    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    # chat completion without streaming
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
    )
    if response:
        logger.info(f"response: {response}")
        return response
    else:
        return {"error": "Failed to get response from Perplexity API"}


@app.post("/process-excel/", response_class=Response)
async def process_excel(file: UploadFile = File(...)) -> Response:
    logger.info(f"file.filename: {file.filename}")
    # Read the uploaded Excel file into a DataFrame
    contents = await file.read()
    input_stream = BytesIO(contents)
    df = pd.read_excel(input_stream)

    # Check if the required column is present
    if "Requirement" not in df.columns:
        return {"error": "Excel file must contain 'Requirement' column"}

    # Extract the requirements
    requirements = df["Requirement"].tolist()

    # Create a new session with the chat assistant
    try:
        session = get_chat_assistant_session()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session with chat assistant: {str(e)}",
        )

    # Get the responses from the chat assistant
    responses = []
    try:
        responses = ask_questions_to_chat_assistant(
            session=session, questions=requirements
        )
        # logger.info(f"RAG responses: {responses}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ask questions to chat assistant: {str(e)}",
        )

    # Extract the answers and references from the responses
    parsed_responses = parse_answer(responses)
    # logger.info(f"parsed_responses: {parsed_responses}")

    # Add the extracted information to the dataframe
    df["Supplier explanation / comments"] = parsed_responses[
        "Supplier explanation / comments"
    ]
    df["Reference"] = parsed_responses["Reference"]
    # logger.info(f"Final response>:\n {df}")

    # Save the new dataframe to an in-memory excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)

    output.seek(0)  # Move the cursor to the beginning

    # Return response with Excel file
    headers = {
        "Content-Disposition": "attachment; filename=SeismaResponse.xlsx",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return Response(
        content=output.getvalue(), headers=headers, media_type=headers["Content-Type"]
    )


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=EXPOSED_PORT, log_level="debug")
