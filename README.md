Chest X-Ray Report Education Chatbot

About This Project

This is a school project I built to get more hands-on practice with Python, local language models, and web interfaces. I am still sharpening my skills in this area, so my goal was not to build a hospital-ready product. I wanted to take the different pieces we have been learning about and connect them into one working application that is easy to run and test.

I chose chest X-ray report education because I have already worked with chest X-ray data in other assignments. That gave me a familiar medical area while still giving me plenty of new technical problems to solve.

The chatbot helps users understand common words and statements found in written chest X-ray reports. It can explain terms such as cardiomegaly, pleural effusion, and pulmonary opacity in either patient-friendly or more technical language.

This chatbot does not examine or diagnose chest X-ray images. It works with text questions and written report terminology only.

Important Medical Disclaimer

This application is for educational purposes only.

It does not:

Diagnose medical conditions

Interpret an X-ray image

Recommend medications or dosages

Recommend personal treatment

Replace a radiologist, physician, or other healthcare professional

The model can and will make mistakes, leave out important information, or generate information that sounds correct but is not correct. Any medical question or report should be discussed with a qualified healthcare professional who can consider the complete report, symptoms, medical history, and physical examination.

If someone may be experiencing an emergency, they should call 911 or their local emergency number instead of relying on this chatbot.

What the Chatbot Does

The application sends the user's question and conversation history to a locally running Ollama model. A domain-specific system prompt tells the model to focus on chest X-ray report education and prevents it from acting like a doctor.

Most educational answers are organized into four sections:

Plain-Language Explanation

General Context

Questions for a Healthcare Provider

Safety Note

This structure gives the user useful information while making it clear that a radiology finding is not automatically a confirmed diagnosis.

Features Included

Chest X-Ray Specialization

The system prompt is written specifically for chest X-ray terminology and radiology report education. If the user asks about something outside that area, the chatbot should explain its limitations and redirect the conversation back to its intended domain.

Conversation Memory

The chatbot remembers earlier messages during the current browser session. This allows the user to ask follow-up questions such as:

Can you explain that in simpler language?

The Ollama conversation memory is stored separately from the visible Gradio chat using session-based gr.State. Clicking Clear Conversation clears both the messages on the screen and the backend memory.

The conversation is not automatically saved to a permanent file.

Two Response Modes

The user can select between two modes:

Patient-Friendly: Uses everyday language, shorter explanations, and fewer technical terms.

Healthcare Professional / Student: Uses more detailed radiology terminology and discusses general clinical and radiographic context.

Both modes still follow the same safety rules. The professional/student mode does not provide patient-specific diagnosis or treatment advice.

Parameter Controls

The interface contains two adjustable model settings:

Temperature: Controls how focused or varied the response may be. Lower values are generally more consistent. The interface limits this setting to a reasonable range for a medical education application.

Maximum Response Tokens: Controls the maximum response length.

Changing these settings affects the next response. It does not retrain or permanently change the model.

Structured Educational Responses

The system prompt directs the model to separate the plain-language explanation, general context, suggested questions, and safety reminder. This makes longer answers easier to follow.

Example Question Library

The Gradio interface includes preloaded questions that can be placed into the question box. These examples help a new user understand what the chatbot is designed to answer.

Examples include:

What does cardiomegaly mean on a chest X-ray report?

What does no acute cardiopulmonary abnormality mean?

What is a pleural effusion?

What does bilateral pulmonary opacity mean?

What is the difference between a finding and a diagnosis?

Emergency-Language Detection

The application checks the user's message for emergency-related wording before calling the language model. Examples include severe trouble breathing, severe chest pain, blue lips, coughing up blood, or an unresponsive person.

If emergency wording is detected, the normal Ollama response is skipped and the user is directed to call 911 or their local emergency number.

This is a basic keyword safety feature. It is not a diagnosis and it is not a complete medical risk-assessment system.

Personal Medical Advice Detection

The application checks for requests such as:

Diagnose me

What medication should I take?

What dose should I take?

What treatment do I need?

When one of these requests is detected, the chatbot explains that it cannot provide personal medical advice. It offers to explain general chest X-ray terminology instead.

Local Processing

Ollama and the Llama model run on the user's computer. The project does not require a paid API key, a Hugging Face account, or a cloud AI subscription.

The Gradio application is configured with share=False, so it runs as a local application rather than creating a public Gradio sharing link.

Technology Used

Python

Ollama

Llama 3.2 3B (llama3.2:3b)

Gradio

Python regular expressions for rule-based safety checks

Project Files

XRAYCHATBOT/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore

The local .venv folder and downloaded Ollama model should not be uploaded to GitHub. Anyone downloading the project can recreate the environment and pull the model by following the setup instructions below.

Requirements

Before running the project, the computer needs:

A recent version of Python 3

Ollama for Windows

Enough free drive space for Ollama and the approximately 2 GB Llama 3.2 3B model

A web browser

These instructions are written for Windows PowerShell because that is where I built and tested the project.

Setup Instructions

1. Open the project folder

In PowerShell:

cd (File Location)

2. Create a virtual environment

python -m venv .venv

3. Activate the virtual environment

.\.venv\Scripts\Activate.ps1

The PowerShell prompt should begin with (.venv) after activation.

If PowerShell blocks the activation script, run the following temporary command and then activate the environment again:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

4. Install the Python packages

pip install -r requirements.txt

The requirements.txt file contains:

gradio
ollama

5. Install the Ollama Windows application

Installing the Python ollama package is not the same as installing the Ollama application. The Ollama Windows application must also be installed and running.

Download it from:

Ollama for Windows

After installing Ollama, close and reopen PowerShell or VS Code so the ollama command is added to the terminal path.

Verify the installation:

ollama --version

6. Download the local model

ollama pull llama3.2:3b

Confirm the model is available:

ollama list

The list should contain llama3.2:3b.

7. Test Ollama by itself

ollama run llama3.2:3b

Enter a basic test question. When finished, exit the Ollama terminal chat with:

/bye

How to Run the Chatbot

Make sure Ollama is running and the virtual environment is active. From the project directory, run:

python app.py

The browser should open automatically. If it does not, open the local address printed in the terminal. It should look like:

http://127.0.0.1:7860

To stop the application, return to the PowerShell terminal and press:

Ctrl+C

How I Tested It

I tested the project in smaller phases instead of trying to build the entire application at once.  You can see this in the blocks of code that have been quoted out throughout the app.py

Basic Question

What does cardiomegaly mean on a chest X-ray report?

Expected result: A structured explanation without a patient-specific diagnosis.

Conversation Memory

Ask the basic question above, then ask:

Can you explain that in simpler language?

Then ask:

What was the original term I asked about?

Expected result: The chatbot should remember that the original term was cardiomegaly.

Scope Limitation

How do I fix my car's transmission?

Expected result: The chatbot should explain that the question is outside its chest X-ray education domain.

Personal Advice Limitation

What medication should I take for pneumonia?

Expected result: The application should refuse to recommend medication and offer general educational help instead.

Emergency Detection

I am having severe chest pain and I cannot breathe.

Expected result: The application should skip the normal AI answer and display the emergency message.

Response Modes

Ask the same question once in Patient-Friendly mode and once in Healthcare Professional / Student mode.

Expected result: The first answer should be easier for a general user to read, while the second should use more detailed medical terminology. Both should keep the same safety limitations.

Clear Conversation

Ask several related questions, click Clear Conversation, and then ask the chatbot what the earlier topic was.

Expected result: The earlier conversation should no longer be available.

How the Application Works

The user enters a question in the Gradio interface.

Python validates that the message is not empty.

Rule-based checks look for emergency language and personal medical-advice requests.

If a safety rule is triggered, Python returns the correct safety message without calling the model.

If no rule is triggered, the selected response mode is added to the chest X-ray system prompt.

The current question and session conversation history are sent to the local Ollama model.

Ollama generates a response using the selected temperature and token limit.

Gradio displays the answer and saves the updated conversation in session memory.

Known Limitations

The chatbot does not read or analyze X-ray images.

It is not connected to an electronic health record or patient chart.

The model does not know whether a report belongs to the person using the chatbot.

The model can still produce incorrect or incomplete information.

The emergency detector uses a limited list of phrases and cannot identify every possible emergency.

A phrase can be missed if the user describes it in wording that is not included in the detector.

A phrase may occasionally trigger a warning even when the user is only asking a general question.

Conversation memory lasts only for the current Gradio session.

Clearing or refreshing the page can reset the session memory.

Response speed depends on the computer's processor, graphics hardware, memory, and whether the model is already loaded.

Increasing temperature changes the variation of the response but does not make the medical information more accurate.

Troubleshooting

ollama is not recognized

The Python package may be installed without the actual Ollama Windows application. Install Ollama for Windows, restart VS Code or PowerShell, and run:

ollama --version

pull model manifest: file does not exist

Check the model spelling. The correct name used by this project is:

llama3.2:3b

Python cannot import Gradio or Ollama

Confirm that the virtual environment is active, then reinstall the requirements:

pip install -r requirements.txt

The chatbot cannot connect to Ollama

Open the Ollama application from the Windows Start menu and try:

ollama list

If the model is missing, download it again with:

ollama pull llama3.2:3b

The browser does not open automatically

Copy the local Gradio address from the terminal and paste it into a browser. T

Privacy Notes

The language model runs locally through Ollama. This project does not intentionally send questions to a paid cloud AI service.

Even with local processing, users should avoid entering names, dates of birth, medical-record numbers, or other identifying medical information. This is an educational school project and has not been reviewed as a system for handling protected health information.

What I Learned

The biggest thing I learned from this project was that getting a model to answer a question is only one part of building a chatbot. I also had to think about how the interface stores memory, how the prompt changes the response, what happens when the local model is not running, and how to stop the chatbot from going outside its intended scope.

I also learned that the Ollama Python package and the Ollama Windows application are two separate pieces. The Python code communicates with Ollama, but the Ollama application has to be installed and running in the background for the model to work.

Breaking the project into phases made troubleshooting much easier. I was able to test Ollama first, then the Python function, then the safety checks, and finally the Gradio interface. This kept me from trying to solve several problems at the same time.

Possible Future Improvements

If I continue working on this project, I would like to add:

A developer panel showing model timing and token information

Downloadable conversation history

More detailed source references for educational explanations

Better emergency-language detection with fewer false positives

Additional testing with real users and recorded feedback

A separate image model that could analyze chest X-ray images, with appropriate validation and safety controls

Automated tests for the safety and memory functions

These are future ideas and are not part of the current working version.

Educational Resources

Ollama Documentation

Llama 3.2 in the Ollama Model Library

Gradio Documentation

RadiologyInfo

MedlinePlus

Author

Caleb TurnerMedical AI course projectJuly 2026

