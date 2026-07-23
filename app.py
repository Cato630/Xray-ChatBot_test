"""
Chest X-Ray Report Education Chatbot

This application uses a local Ollama model to explain common
chest X-ray report terminology for educational purposes.
If this is an emergency please dial 911 or your Local emergency hot line and do not utilize this chat bot.
This is not for practical use at all. THis a project built for a masters program.
"""
import re

import gradio as gr
import ollama


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "llama3.2:3b"

DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 500


# ============================================================
# DOMAIN-SPECIFIC SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are X-Ray Education Assistant, an AI chatbot specialized in
chest X-ray report education.

Your purpose is to help users understand terminology and general
statements commonly found in chest X-ray radiology reports.

Follow these rules:

1. Provide educational information only.
2. Do not diagnose diseases or determine whether a person has a condition.
3. Do not recommend medications, treatments, or changes in medical care.
4. Do not replace a radiologist, physician, or other healthcare professional.
5. Explain medical terminology using clear and respectful language.
6. Clearly distinguish between a radiology finding and a confirmed diagnosis.
7. Avoid alarming language and acknowledge uncertainty.
8. Encourage users to discuss their complete report with a qualified provider.
9. Stay focused on chest X-rays, radiology reports, and related education.
10. If asked about an unrelated topic, politely explain the chatbot's scope.
11. Do not claim that you examined an image unless image analysis is explicitly
    supported by the application.
12. If the user describes severe symptoms such as difficulty breathing,
    chest pain, blue lips, confusion, coughing blood, or loss of consciousness,
    advise them to seek immediate emergency assistance.

When explaining a chest X-ray term or statement, organize the response as:

Plain-Language Explanation:
Explain the term simply.

General Context:
Describe what the finding can mean in general without diagnosing the user.

Questions for a Healthcare Provider:
Suggest useful questions the user could ask their provider.

Safety Note:
Remind the user that the explanation is educational and must be interpreted
alongside their symptoms, medical history, and complete examination.
"""

# ============================================================
# RESPONSE MODES
# ============================================================

MODE_INSTRUCTIONS = {
    "Patient-Friendly": """
Use patient-friendly language.

- Explain medical terms using common everyday words.
- Define unavoidable medical terminology.
- Use short paragraphs and bullet points.
- Avoid unnecessary technical detail.
- Keep the tone calm, clear, and reassuring.
- Do not assume the user has medical training.
""",

    "Healthcare Professional / Student": """
Use terminology appropriate for a healthcare professional or medical student.

- Provide more detailed radiology terminology.
- Discuss general clinical and radiographic context.
- Clearly separate findings, impressions, and differential considerations.
- Do not provide a patient-specific diagnosis.
- Do not recommend patient-specific treatment.
- Acknowledge uncertainty and the need for clinical correlation.
"""
}


def build_system_prompt(mode):
    """
    Combine the safety-focused system prompt with mode instructions.
    """

    mode_prompt = MODE_INSTRUCTIONS.get(
        mode,
        MODE_INSTRUCTIONS["Patient-Friendly"]
    )

    return SYSTEM_PROMPT + "\n\n" + mode_prompt



# ============================================================
# CURATED EDUCATIONAL SOURCES
# ============================================================

GENERAL_REPORT_SOURCE = {
    "title": "How to Read Your Chest X-ray Report",
    "organization": "RadiologyInfo.org",
    "url": (
        "https://www.radiologyinfo.org/en/info/"
        "article-chest-xray-report"
    )
}

GENERAL_XRAY_SOURCE = {
    "title": "Chest X-ray (Radiography)",
    "organization": "RadiologyInfo.org",
    "url": "https://www.radiologyinfo.org/en/info/chestrad"
}

TOPIC_SOURCES = [
    {
        "keywords": [
            "cardiomegaly",
            "enlarged heart",
            "cardiac enlargement"
        ],
        "source": {
            "title": "Cardiomegaly",
            "organization": "NCBI Bookshelf",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK542296/"
        }
    },
    {
        "keywords": [
            "pleural effusion",
            "pleural",
            "pleura",
            "pneumothorax"
        ],
        "source": {
            "title": "Pleural Disorders",
            "organization": "MedlinePlus",
            "url": "https://medlineplus.gov/pleuraldisorders.html"
        }
    },
    {
        "keywords": [
            "pneumonia"
        ],
        "source": {
            "title": "About Pneumonia",
            "organization": "Centers for Disease Control and Prevention",
            "url": "https://www.cdc.gov/pneumonia/about/index.html"
        }
    },
    {
        "keywords": [
            "atelectasis"
        ],
        "source": {
            "title": "Atelectasis",
            "organization": "Johns Hopkins Medicine",
            "url": (
                "https://www.hopkinsmedicine.org/health/"
                "conditions-and-diseases/atelectasis"
            )
        }
    },
    {
        "keywords": [
            "lung nodule",
            "pulmonary nodule",
            "lung nodules",
            "pulmonary nodules"
        ],
        "source": {
            "title": "Lung Nodules: Diagnosis and Treatment",
            "organization": "RadiologyInfo.org",
            "url": "https://www.radiologyinfo.org/en/info/lung-nodules"
        }
    },
    {
        "keywords": [
            "pulmonary edema",
            "lung edema"
        ],
        "source": {
            "title": "Pulmonary Edema",
            "organization": "MedlinePlus",
            "url": "https://medlineplus.gov/ency/article/000140.htm"
        }
    },
    {
        "keywords": [
            "radiation",
            "radiation dose",
            "x-ray safety"
        ],
        "source": {
            "title": "Radiation Dose from X-Ray and CT Exams",
            "organization": "RadiologyInfo.org",
            "url": "https://www.radiologyinfo.org/en/info/safety-xray"
        }
    }
]


def build_reference_section(context_text):
    """
    Select verified educational sources based on conversation topics.

    These sources are selected by Python. They are not generated by
    the language model.
    """

    normalized_context = context_text.casefold()

    selected_sources = [GENERAL_REPORT_SOURCE]

    for source_group in TOPIC_SOURCES:
        topic_found = any(
            keyword in normalized_context
            for keyword in source_group["keywords"]
        )

        if topic_found:
            selected_sources.append(source_group["source"])

    # Provide a general chest X-ray source when no topic-specific
    # source was selected.
    if len(selected_sources) == 1:
        selected_sources.append(GENERAL_XRAY_SOURCE)

    # Remove duplicate URLs while preserving their original order.
    unique_sources = []
    used_urls = set()

    for source in selected_sources:
        if source["url"] not in used_urls:
            unique_sources.append(source)
            used_urls.add(source["url"])

    # Keep the reference section short.
    unique_sources = unique_sources[:3]

    source_lines = []

    for source in unique_sources:
        source_lines.append(
            f"- [{source['title']} — "
            f"{source['organization']}]({source['url']})"
        )

    formatted_sources = "\n".join(source_lines)

    return (
        "\n\n---\n\n"
        "### Sources and Further Reading\n\n"
        f"{formatted_sources}\n\n"
        "*These links were selected from a curated source library based "
        "on the conversation topic. The local model did not browse or "
        "directly quote these pages.*"
    )


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

EMERGENCY_PHRASES = [
    "i can't breathe",
    "i cannot breathe",
    "i cannot breath"
    "i cant breathe",
    "i am struggling to breathe",
    "i'm struggling to breathe",
    "im struggling to breathe",
    "i am gasping for air",
    "i'm gasping for air",
    "im gasping for air",
    "i have severe chest pain",
    "i am having severe chest pain",
    "i'm having severe chest pain",
    "im having severe chest pain",
    "my lips are blue",
    "my lips are turning blue",
    "i am coughing up blood",
    "i'm coughing up blood",
    "im coughing up blood",
    "i passed out",
    "someone passed out",
    "someone is unconscious",
    "someone is unresponsive",
    "not breathing",
    "i feel like i am suffocating",
]

PERSONAL_ADVICE_PHRASES = [
    "do i have",
    "diagnose me",
    "what medication should i take",
    "what medicine should i take",
    "what dose should i take",
    "should i stop taking",
    "should i change my medication",
    "what treatment do i need",
    "tell me what treatment",
]

EMERGENCY_RESPONSE = """
🚨 POSSIBLE MEDICAL EMERGENCY

Your message may describe symptoms that require immediate medical attention.

If these symptoms are happening now:

- Call 911 or your local emergency number.
- Do not wait for this chatbot to provide an answer.
- If possible, have another person remain with you.
- Do not rely on an AI chatbot during an emergency.

This message does not provide a diagnosis. It is a safety response based only
on the emergency-related language detected in your message.
""".strip()

PERSONAL_ADVICE_RESPONSE = """
I cannot diagnose you or recommend a medication, dosage, or personal treatment.

I can still help by:

- Explaining chest X-ray terminology
- Describing what a finding can mean in general
- Helping you prepare questions for your healthcare provider
- Explaining the difference between a radiology finding and a diagnosis

Please discuss personal medical decisions with a qualified healthcare
professional who can review your complete history and examination.
""".strip()


def normalize_text(text):
    """
    Normalize text to make phrase detection more consistent.
    """

    normalized = text.casefold().replace("’", "'")
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def detect_emergency(user_message):
    """
    Check for language that may describe an immediate medical emergency.

    This is a conservative keyword-based safety check and is not a
    medical diagnosis or comprehensive risk assessment.
    """

    normalized_message = normalize_text(user_message)

    return any(
        phrase in normalized_message
        for phrase in EMERGENCY_PHRASES
    )


def detect_personal_advice_request(user_message):
    """
    Detect requests for diagnosis, medication, dosage, or treatment advice.
    """

    normalized_message = normalize_text(user_message)

    return any(
        phrase in normalized_message
        for phrase in PERSONAL_ADVICE_PHRASES
    )

# ============================================================
# CHAT FUNCTION
# ============================================================

def generate_response(
    user_message,
    conversation_history=None,
    mode="Patient-Friendly",
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=DEFAULT_MAX_TOKENS
):
    """
    Send a message and conversation history to the local Ollama model.

    Args:
        user_message: The user's current question.
        conversation_history: Previous user and assistant messages.
        temperature: Controls how creative or focused the response is.
        max_tokens: Maximum number of tokens in the response.

    Returns:
        The model's response as a string.
    """

    if not user_message or not user_message.strip():
        return "Please enter a question about chest X-rays."
    
        # Perform rule-based safety checks before calling the AI model.
    if detect_emergency(user_message):
        return EMERGENCY_RESPONSE

    if detect_personal_advice_request(user_message):
        return PERSONAL_ADVICE_RESPONSE

    if conversation_history is None:
        conversation_history = []

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(mode)
        }
    ]

    messages.extend(conversation_history)

    messages.append(
        {
            "role": "user",
            "content": user_message.strip()
        }
    )

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={
                "temperature": float(temperature),
                "num_predict": int(max_tokens)
            }
        )

        '''return response["message"]["content"].strip()'''
        answer = response["message"]["content"].strip()

        # Include previous user questions when selecting sources.
        # This lets a follow-up such as "Explain that again" retain
        # references related to the original topic.
        source_context_parts = [user_message]

        for previous_message in conversation_history:
            if previous_message.get("role") == "user":
                previous_content = previous_message.get("content", "")

                if isinstance(previous_content, str):
                    source_context_parts.append(previous_content)

        source_context = " ".join(source_context_parts)

        reference_section = build_reference_section(source_context)

        return answer + reference_section

    

    except ConnectionError:
        return (
            "Unable to connect to Ollama. Make sure the Ollama "
            "application is running."
        )

    except Exception as error:
        return (
            f"An unexpected error occurred: {error}\n\n"
            f"Confirm that the '{MODEL_NAME}' model is installed."
        )



# ============================================================
# GRADIO CHAT FUNCTIONS
# ============================================================

'''def prepare_model_history(chat_history):
    """
    Convert Gradio's chat history into the format expected by Ollama.

    Args:
        chat_history: Previous messages displayed by the Gradio chatbot.

    Returns:
        A list of user and assistant messages for Ollama.
    """

    model_history = []

    if not chat_history:
        return model_history

    for message in chat_history:
        role = message.get("role")
        content = message.get("content")

        if (
            role in {"user", "assistant"}
            and isinstance(content, str)
        ):
            model_history.append(
                {
                    "role": role,
                    "content": content
                }
            )

    return model_history


def chat_with_model(user_message, chat_history):
    """
    Process a Gradio message, call Ollama, and update the chat display.
    """

    if chat_history is None:
        chat_history = []

    if not user_message or not user_message.strip():
        return "", chat_history

    model_history = prepare_model_history(chat_history)

    answer = generate_response(
        user_message=user_message,
        conversation_history=model_history,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS
    )

    updated_history = list(chat_history)

    updated_history.append(
        {
            "role": "user",
            "content": user_message.strip()
        }
    )

    updated_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return "", updated_history


def clear_conversation():
    """
    Clear the input box and the current Gradio conversation.
    """

    return "", []'''

def chat_with_model(
    user_message,
    chat_history,
    conversation_history,
    mode,
    temperature,
    max_tokens
    
):
    """
    Process a Gradio message while maintaining separate model memory.

    chat_history controls what appears in the interface.
    conversation_history stores the messages sent to Ollama.
    """

    if chat_history is None:
        chat_history = []

    if conversation_history is None:
        conversation_history = []

    if not user_message or not user_message.strip():
        return "", chat_history, conversation_history

    cleaned_message = user_message.strip()

    answer = generate_response(
        user_message=cleaned_message,
        conversation_history=conversation_history,
        mode=mode,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # Create copies so Gradio can detect the state changes.
    updated_chat_history = list(chat_history)
    updated_conversation_history = list(conversation_history)

    # Update the visible Gradio conversation.
    updated_chat_history.append(
        {
            "role": "user",
            "content": cleaned_message
        }
    )

    updated_chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # Update the separate history sent to Ollama.
    updated_conversation_history.append(
        {
            "role": "user",
            "content": cleaned_message
        }
    )

    updated_conversation_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return (
        "",
        updated_chat_history,
        updated_conversation_history
    )


def clear_conversation():
    """
    Clear the input, visible chat, and Ollama conversation memory.
    """

    return "", [], []


# ============================================================
# GRADIO INTERFACE
# ============================================================

with gr.Blocks(
    theme=gr.themes.Soft(),
    title="Chest X-Ray Education Assistant"
) as app:

    gr.Markdown(
        """
        # 🩻 Chest X-Ray Report Education Assistant

        Learn what common chest X-ray report terms mean in plain language.

        > **Educational purposes only:** This application does not diagnose
        > medical conditions or provide personal medical advice. Always discuss
        > your complete report with a qualified healthcare professional.
        """
    )
    # Session-based memory used by Ollama.
    conversation_state = gr.State(value=[])
    
    with gr.Row():

        with gr.Column(scale=3):

            chatbot = gr.Chatbot(
                label="Conversation",
                height=520
            )

            question = gr.Textbox(
                label="Your question",
                placeholder=(
                    "Ask about a term or statement from a chest X-ray report..."
                ),
                lines=3
            )

            with gr.Row():
                submit_button = gr.Button(
                    "Ask the Assistant",
                    variant="primary"
                )

                clear_button = gr.Button(
                    "Clear Conversation"
                )

        with gr.Column(scale=1):

            gr.Markdown(
                """
                ### What this chatbot can do

                - Explain chest X-ray terminology
                - Translate report statements into plain language
                - Provide general educational context
                - Suggest questions for a healthcare provider
                - Remember earlier parts of the conversation

                ### Scope limitations

                This chatbot cannot:

                - Diagnose a condition
                - Interpret an uploaded X-ray image
                - Recommend medication or dosage
                - Prescribe treatment
                - Replace a radiologist or physician
                """
            )

    gr.Markdown("### Example questions")

    gr.Examples(
        examples=[
            ["What does cardiomegaly mean on a chest X-ray report?"],
            ["What does no acute cardiopulmonary abnormality mean?"],
            ["What is a pleural effusion?"],
            ["What does bilateral pulmonary opacity mean?"],
            ["What is the difference between a finding and a diagnosis?"],
        ],
        inputs=question,
        label="Select an example to place it in the question box"
    )

    with gr.Accordion("About this application", open=False):

        gr.Markdown(
            f"""
            ### Domain

            This application specializes in chest X-ray report education.
            It helps patients, students, and other users understand common
            radiology terminology.

            ### Technology

            - **Local model:** `{MODEL_NAME}`
            - **Model runner:** Ollama
            - **Interface:** Gradio
            - **Data processing:** Local computer only

            ### Safety

            The application includes rule-based emergency-language detection
            and blocks requests for personalized diagnosis, medication,
            dosage, or treatment recommendations.

            ### Privacy

            Questions are processed through the locally running Ollama model.
            No cloud AI service or paid API is required.
            """
        )

    gr.Markdown(
        """
        ---
        **Important:** If you believe you are experiencing a medical emergency,
        call 911 or your local emergency number. Do not wait for an AI response.
        """
    )
    
    with gr.Accordion(
                "Response Controls",
                open=True
            ):

                mode_selector = gr.Radio(
                    choices=[
                        "Patient-Friendly",
                        "Healthcare Professional / Student"
                    ],
                    value="Patient-Friendly",
                    label="Response Mode",
                    info=(
                        "Choose the level of terminology used "
                        "in the next response."
                    )
                )

                temperature_slider = gr.Slider(
                    minimum=0.1,
                    maximum=0.8,
                    value=DEFAULT_TEMPERATURE,
                    step=0.1,
                    label="Temperature",
                    info=(
                        "Lower values produce more focused responses. "
                        "Higher values allow more variation."
                    )
                )

                max_tokens_slider = gr.Slider(
                    minimum=200,
                    maximum=800,
                    value=DEFAULT_MAX_TOKENS,
                    step=100,
                    label="Maximum Response Tokens",
                    info=(
                        "Controls the maximum length of the response."
                    )
                )

    # Submit a message by clicking the button.
    submit_button.click(
        fn=chat_with_model,
        inputs=[
            question,
            chatbot,
            conversation_state,
            mode_selector,
            temperature_slider,
            max_tokens_slider
        ],
        outputs=[
            question,
            chatbot,
            conversation_state
        ],
        show_progress="minimal"
    )

    # Submit a message by pressing Enter in the question box.
    question.submit(
        fn=chat_with_model,
        inputs=[
            question,
            chatbot,
            conversation_state,
            mode_selector,
            temperature_slider,
            max_tokens_slider
        ],
        outputs=[
            question,
            chatbot,
            conversation_state
        ],
        show_progress="minimal"
    )

    # Clear both the input and the displayed conversation.
    clear_button.click(
        fn=clear_conversation,
        inputs=None,
        outputs=[
            question,
            chatbot,
            conversation_state
        ],
        queue=False
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CHEST X-RAY REPORT EDUCATION CHATBOT")
    print("=" * 60)
    print(f"Model: {MODEL_NAME}")
    print("Starting local Gradio interface...")
    print("Press Ctrl+C in the terminal to stop the application.")

    app.queue()

    app.launch(
        server_name="127.0.0.1",
        share=False,
        inbrowser=True
    )













'''# ============================================================
# TERMINAL TEST WITH CONVERSATION MEMORY
# ============================================================

def run_terminal_chat():
    """Run a basic terminal chatbot to test the core functionality."""

    conversation_history = []

    print("=" * 60)
    print("CHEST X-RAY REPORT EDUCATION CHATBOT")
    print("=" * 60)
    print("Educational purposes only. No diagnosis or medical advice. If this is an emergency call 911 or your local Emergency Help line!!")
    print("Enter 'exit' to close the chatbot.")

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() in {"exit", "quit"}:
            print("\nChatbot closed.")
            break

        answer = generate_response(
            user_message=user_message,
            conversation_history=conversation_history
        )

        print(f"\nAssistant:\n{answer}")

        conversation_history.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        conversation_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


if __name__ == "__main__":
    run_terminal_chat()'''
