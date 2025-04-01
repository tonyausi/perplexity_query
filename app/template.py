from jinja2 import Template

# flake8: noqa: E501
template = Template(
    """
{
    "model": "{{ model }}",
    "messages": [
        {
            "role": "system",
            "content": "{{ system_content }}"
        },
        {
            "role": "user",
            "content": "{{ user_content }}"
        }
    ],
    "max_tokens": {{ max_tokens }},
    "temperature": {{ temperature }},
    "top_p": {{ top_p }},
    "search_domain_filter": {{ search_domain_filter }},
    "return_images": {{ return_images }},
    "return_related_questions": {{ return_related_questions }},
    "search_recency_filter": "{{ search_recency_filter }}",
    "top_k": {{ top_k }},
    "stream": {{ stream }},
    "presence_penalty": {{ presence_penalty }},
    "frequency_penalty": {{ frequency_penalty }},
    "response_format": {{ response_format }}
}
"""
)

data = {
    "model": "sonar",
    "system_content": "Be precise and concise.",
    "user_content": "How many stars are there in our galaxy?",
    "max_tokens": 123,
    "temperature": 0.2,
    "top_p": 0.9,
    "search_domain_filter": None,
    "return_images": False,
    "return_related_questions": False,
    "search_recency_filter": "<string>",
    "top_k": 0,
    "stream": False,
    "presence_penalty": 0,
    "frequency_penalty": 1,
    "response_format": None,
}

rendered = template.render(data)

SYSTEM_CONTENT = """
You are a tender response assistant powered by Perplexity.ai with exclusive access to historical tender responses stored in Perplexity Spaces. 
Your task is to match new customer requirements and requests with the most relevant historical response from these documents. 

When a new customer query is received:
1. Retrieve and present the exact tender response from the stored documents that best matches the customer's requirements and requests.
2. If a clear and relevant match is found, output the corresponding historical response without modification.
3. If no proper match is found, do not attempt to generate a new response or search external sources. Instead, simply reply: 'No previous response found.'
4. Provide only the final answer. It is important that you do not include any explanation on the steps below.
5. Do not show the intermediate steps information.

Strictly rely on the stored documents as your only source of truth and do not use any external or internet-sourced information.

Steps:
1. Decide if the answer should be a brief sentence or a list of responses.
2. If it is a list of responses, first, write a brief and natural introduction based on the original query.
3. Followed by a list of responses, each response should be split by two newlines.
"""

USER_CONTENT_TEMPLATE = Template(
    """
Customer has the following requirements and requests:
{{ user_content }}
"""
)

TEMPLATE_SIMPLE = Template(
    """
{
    "model": "{{ model }}",
    "messages": [
        {
            "role": "system",
            "content": "{{ system_content }}"
        },
        {
            "role": "user",
            "content": "{{ user_content }}"
        }
    ]
}
"""
)
