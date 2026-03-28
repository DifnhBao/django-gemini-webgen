import os

from django.conf import settings

_genai = None
_legacy_genai = None
_legacy_client = None

try:
    import google.genai as _genai
except ImportError:
    try:
        from google import genai as _genai
    except ImportError:
        _genai = None

if _genai is None:
    try:
        import google.generativeai as _legacy_genai
        try:
            import google.generativeai.client as _legacy_client
        except ImportError:
            _legacy_client = None
    except ImportError:
        _legacy_genai = None
        _legacy_client = None

if _genai is None and _legacy_genai is None:
    raise ImportError(
        'A Gemini client library is required. Install `google-genai` with `pip install google-genai`.'
    )


def _normalize_response_text(response):
    if response is None:
        return ''

    if hasattr(response, 'text'):
        return response.text

    if isinstance(response, dict):
        if 'output' in response:
            output = response['output']
            if isinstance(output, list) and output:
                first = output[0]
                if isinstance(first, dict) and 'content' in first:
                    return first['content']
                return str(first)
        if 'content' in response:
            return response['content']
        return str(response)

    if hasattr(response, 'outputs'):
        outputs = getattr(response, 'outputs')
        if outputs:
            first = outputs[0]
            if hasattr(first, 'content'):
                return first.content
            if hasattr(first, 'text'):
                return first.text
            return str(first)

    return str(response)


def _call_gemini(prompt: str, api_key: str):
    if api_key:
        os.environ['GOOGLE_API_KEY'] = api_key
        os.environ['GOOGLE_GEMINI_API_KEY'] = api_key
        os.environ['GOOGLE_API_KEY'] = api_key

    last_exception = None

    if _genai is not None:
        if hasattr(_genai, 'configure'):
            _genai.configure(api_key=api_key)

        try:
            if hasattr(_genai, 'Client'):
                client = _genai.Client(api_key=api_key)
                if hasattr(client, 'chats') and hasattr(client.chats, 'create'):
                    chat = client.chats.create(model='gemini-2.5-flash')
                    return chat.send_message(prompt)
                if hasattr(client, 'responses') and hasattr(client.responses, 'create'):
                    return client.responses.create(model='gemini-2.5-flash', input=prompt)

            if hasattr(_genai, 'TextGenerationClient'):
                client = _genai.TextGenerationClient()
                return client.generate_text(model='gemini-2.5-flash', prompt=prompt)

            if hasattr(_genai, 'ResponsesClient'):
                client = _genai.ResponsesClient()
                return client.generate_text(model='gemini-2.5-flash', prompt=prompt)

            if hasattr(_genai, 'generate_text'):
                return _genai.generate_text(model='gemini-2.5-flash', prompt=prompt)

            if hasattr(_genai, 'responses') and hasattr(_genai.responses, 'create'):
                return _genai.responses.create(model='gemini-2.5-flash', input=prompt)
        except Exception as e:
            last_exception = e

    if _legacy_genai is not None:
        try:
            if hasattr(_legacy_genai, 'configure'):
                _legacy_genai.configure(api_key=api_key)

            if hasattr(_legacy_genai, 'generate_text'):
                return _legacy_genai.generate_text(model='gemini-1.0', prompt=prompt)

            if hasattr(_legacy_genai, 'responses') and hasattr(_legacy_genai.responses, 'create'):
                return _legacy_genai.responses.create(model='gemini-1.0', input=prompt)
        except Exception as e:
            last_exception = e

        if _legacy_client is not None and hasattr(_legacy_client, 'get_default_generative_client'):
            if hasattr(_legacy_client, 'configure'):
                _legacy_client.configure(api_key=api_key)
            client = _legacy_client.get_default_generative_client()
            try:
                from google.ai.generativelanguage_v1beta.types import content as content_types

                content_obj = content_types.Content(
                    role='input',
                    parts=[
                        content_types.Part(text=prompt),
                    ],
                )
                return client.generate_content(
                    model='models/gemini-2.5-flash',
                    contents=[content_obj],
                )
            except Exception as e:
                last_exception = e

            try:
                from google.ai.generativelanguage_v1beta.types import content as content_types

                content_obj = content_types.Content(
                    role='input',
                    parts=[
                        content_types.Part(text=prompt),
                    ],
                )
                return client.generate_content(
                    model='models/gemini-2.0-flash-001',
                    contents=[content_obj],
                )
            except Exception as e:
                last_exception = e


    if last_exception is not None:
        raise last_exception
    raise RuntimeError(
        'Unable to invoke Gemini API with the installed client library. '
        'Install `google-genai` and use a supported Gemini package version.'
    )


def generate_website_with_gemini(topic: str) -> str:
    
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured in Django settings.')

    prompt = (
        f"Generate a complete mini website in raw HTML/CSS/JS only for the topic '{topic}'. "
        "Do not include any markdown, explanation, or extra prose. "
        "The output must be plain HTML, CSS, and JavaScript code only. "
        "Include a welcoming greeting that uses the Django template tag {{ user.username }} in the HTML output. "
        "Design a UI for the requested topic. For example, if the topic is 'flight booking', include a ticket pricing search form. "
        "Use inline or embedded CSS and JavaScript as needed for a functional mini website. "
        "Return only the raw page content, not JSON or markdown wrappers."
    )

    response = _call_gemini(prompt, api_key)
    return _normalize_response_text(response)
