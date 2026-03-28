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
    f"Act as an expert Frontend Developer. Generate a modern, beautiful, and fully responsive single-page mini website for the topic '{topic}'.\n\n"
    "STRICT RULES:\n"
    "1. Return ONLY the raw HTML code. Do NOT include any markdown formatting (like ```html), explanations, or extra prose.\n"
    "2. Use Tailwind CSS via CDN (<script src=\"[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)\"></script>) for all styling. Do not write raw CSS unless absolutely necessary.\n"
    "3. TYPOGRAPHY & ICONS: Embed the 'Inter' font from Google Fonts and apply it to the body. Include the FontAwesome CDN (<link rel=\"stylesheet\" href=\"[https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css](https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css)\">) and use appropriate icons throughout the UI.\n"
    "4. The UI must be modern: use flexbox/grid, explicit responsive prefixes (sm:, md:, lg:), hover effects, rounded corners, soft shadows, and look great on both mobile and desktop.\n"
    "5. Use Semantic HTML5 tags (<nav>, <header>, <main>, <section>, <footer>) instead of just <div> containers.\n"
    "6. AUTHENTICATED STATE: The header/navbar MUST display a realistic logged-in user state. It must include a user avatar icon, strictly use the Django template tag 'Xin chào {{ user.username }}', and include a 'Đăng xuất' (Logout) button.\n"
    "7. The website content and UI text MUST be in Vietnamese.\n"
    "8. Include embedded JavaScript at the end of the body to make the UI interactive (e.g., handling form submissions with simple alerts, mobile menu toggling, or tabs).\n"
    f"9. DOMAIN SPECIFIC & MOCK DATA: Design UI components AND populate them with realistic mock data based on the topic '{topic}'. For example, if it's 'đặt vé máy bay', you MUST include a search form AND a section displaying mock flight tickets with prices, times, and 'Book' buttons. Make it look like a fully functioning system.\n"
    "10. REALISTIC IMAGES: You MUST include relevant image placeholders to make the UI look complete.\n"
    "   - Use LoremFlickr: [https://loremflickr.com/](https://loremflickr.com/)<width>/<height>/<english_keyword1>,<english_keyword2>\n"
    "   - Generate specific, relevant English keywords for each `<img>` tag to get diverse images. For example, if the topic is 'booking homestay', use keywords like 'bedroom,interior' for one image, and 'resort,nature' for another.\n"
    "   - Ensure all images have responsive Tailwind classes (e.g., w-full, object-cover, rounded-lg) and meaningful Vietnamese `alt` attributes."
)

    response = _call_gemini(prompt, api_key)
    return _normalize_response_text(response)
