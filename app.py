import os
import gradio as gr
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
import json
import tempfile
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
from typing import List, Tuple, Optional
import time
from gtts import gTTS
from pydub import AudioSegment


# Initialize Google Gemini client
client = genai.Client(api_key=os.getenv("GEM_API_KEY"))
MODEL_ID = "gemini-2.0-flash-exp"

bounding_box_system_instructions = """
    Return bounding boxes as a JSON array with labels in the context of maternity and baby. Never return masks or code fencing. Limit to 25 objects.
    If an object is present multiple times, name them according to their unique characteristic (colors, size, position, unique characteristics, usage etc..).
"""

additional_colors = [colorname for (colorname, colorcode) in ImageColor.colormap.items()]

def parse_json(json_output):
    """
    Parse JSON output from the Gemini model.
    """
    lines = json_output.splitlines()
    for i, line in enumerate(lines):
        if line == "```json":
            json_output = "\n".join(lines[i+1:])  # Remove everything before "```json"
            json_output = json_output.split("```")[0]  # Remove everything after the closing "```"
            break
    return json_output

def plot_bounding_boxes(im, bounding_boxes):
    """
    Plots bounding boxes on an image with labels.
    """
    im = im.copy()
    width, height = im.size
    draw = ImageDraw.Draw(im)
    colors = [
        'red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 'cyan',
        'lime', 'magenta', 'violet', 'gold', 'silver'
    ] + additional_colors

    try:
        font = ImageFont.load_default()

        bounding_boxes_json = json.loads(bounding_boxes)
        for i, bounding_box in enumerate(bounding_boxes_json):
            color = colors[i % len(colors)]
            abs_y1 = int(bounding_box["box_2d"][0] / 1000 * height)
            abs_x1 = int(bounding_box["box_2d"][1] / 1000 * width)
            abs_y2 = int(bounding_box["box_2d"][2] / 1000 * height)
            abs_x2 = int(bounding_box["box_2d"][3] / 1000 * width)

            abs_x1, abs_x2 = min(abs_x1, abs_x2), max(abs_x1, abs_x2)
            abs_y1, abs_y2 = min(abs_y1, abs_y2), max(abs_y1, abs_y2)

            draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)
            if "label" in bounding_box:
                draw.text((abs_x1 + 8, abs_y1 + 6), bounding_box["label"], fill=color, font=font)
    except Exception as e:
        print(f"Error drawing bounding boxes: {e}")

    return im

def predict_bounding_boxes(image, prompt):
    """
    Process the image and prompt through Gemini and draw bounding boxes.
    """
    try:
        image = image.resize((1024, int(1024 * image.height / image.width)))
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[prompt, image],
            config=GenerateContentConfig(
                system_instruction=bounding_box_system_instructions,
                temperature=0.5,
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_ONLY_HIGH",
                    )
                ],
            )
        )

        print("Gemini response:", response.text)

        bounding_boxes = parse_json(response.text)
        if not bounding_boxes:
            raise ValueError("No bounding boxes returned.")

        result_image = plot_bounding_boxes(image, bounding_boxes)
        return result_image, response.text
    except Exception as e:
        print(f"Error during processing: {e}")
        return image, f"Error: {e}"

def google_search_query(question, use_web_search):
    """
    Perform a Google search query if enabled, or generate a response using Gemini.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=question,
        )
        ai_response = response.text

        if use_web_search:
            google_search_tool = Tool(google_search=GoogleSearch())
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=question,
                config=GenerateContentConfig(tools=[google_search_tool]),
            )
            search_results = response.candidates[0].grounding_metadata.search_entry_point.rendered_content
        else:
            search_results = "Web search not used."

        return ai_response, search_results
    except Exception as e:
        return f"Error: {str(e)}", ""

def update_chatbot(question, response_text, use_web_search, chat_log):
    """
    Update chatbot conversation based on bounding box response and question.
    """
    try:
        # Use bounding box JSON in the question
        full_question = f"{question}. Objects detected: {response_text}"
        ai_response, search_results = google_search_query(full_question, use_web_search)

        chat_log.append(("You", question))
        chat_log.append(("🤰HiMa", ai_response))
        if use_web_search:
            chat_log.append(("👩‍🍼HiMa➕", search_results))
        return chat_log
    except Exception as e:
        chat_log.append(("System", f"Error: {str(e)}"))
        return chat_log


system_instruction_podcast = """
You are MommyBird, host of Nesting with MommyBird, a short and friendly podcast answering questions from new and expecting mothers.
    -You must avoid any text other than the podcast script like okay, here's the podcast. never use cues this will be input text directly to a gtts function)
    - Start by introducing you as mommybird - the host of the show (never use cues this will be input text directly to a gtts function)
    - Each episode is inspired by a question submitted by a listener, which you answer directly with practical tips and relatable advice.
    - Speak in a warm, nurturing tone as if you’re chatting with a fellow mom over tea, sharing insights that are helpful and easy to apply.
    - Use an engaging and conversational style to connect with your audience, sprinkling in light humor or personal anecdotes when relevant.
    - Conclude each episode with a positive affirmation.
    - Keep episodes concise, under 120 seconds, and introduce yourself as MommyBird, host of Nesting with MommyBird.
    - Use a casual, friendly flow with natural pauses, avoiding formal language or background music for a personal touch.
    - Speak casually and empathetically, with light humor or relatable anecdotes when appropriate.
    - Avoid overly technical language; prioritize practicality over scientific jargon.
    - Acknowledge user emotions and provide comforting responses when addressing concerns or challenges.
    - Avoid offering medical diagnoses or replacing professional medical advice; instead, encourage users to consult a healthcare provider when necessary.
"""



# Generate podcast script
def generate_podcast(response_text: str) -> str:
    """
    Generate a podcast script using the Gemini model.
    """
    prompt = f"Based on the key topic of : {response_text}, create a podcast script as MommyBird for a maternity podcast."
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction_podcast,
            temperature=0.5,
            safety_settings=[
                genai.types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                genai.types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                genai.types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                ),
                genai.types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_LOW_AND_ABOVE",
                )
            ]
        )
    )
    return response.text.strip()


# Convert podcast script to audio
def gtpodcast_script_to_audio(script: str) -> str:
    """
    Convert the podcast script to audio.
    """
    if not script.strip():
        raise ValueError("No script provided for audio conversion.")

    # Generate TTS audio
    tts = gTTS(text=script, lang="en")
    temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    tts.save(temp_audio_path)

    # Adjust pitch using AudioSegment
    audio = AudioSegment.from_file(temp_audio_path)
  #  lowered_pitch_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1)})
   # lowered_pitch_audio = lowered_pitch_audio.set_frame_rate(audio.frame_rate)

    # Export the modified audio
    podcast_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    audio.export(podcast_path, format="mp3")

    return podcast_path

# Generate and play podcast
def generate_and_play_podcast(response_text: str) -> Tuple[str, str]:
    """
    Generate a podcast script and convert it to audio.
    """
    script = generate_podcast(response_text)
    audio_path = gtpodcast_script_to_audio(script)
    return script, audio_path

with gr.Blocks(theme=gr.themes.Glass(secondary_hue="violet")) as app:
    # App Header
    gr.HTML(
        """
        <div style="text-align: center; margin-top: 20px;">
            <img src="https://huggingface.co/spaces/Rahatara/Gemini2_Spatial/resolve/main/Mommy.gif" alt="Mommy" style="display: block; margin: 0 auto; width: 200px; height: auto; margin-bottom: 20px;">
            <h1>🤰🤰🏼🤰🏽🤰🏿HiMa</h1>
            <p style="font-size: 18px; font-weight: bold;">Your Maternity Learning Assistant</p>
        </div>
        """
    )
    # Tab 1: Detect Items
    with gr.Tab("🤰🔎Detect"):
        gr.Markdown("# 👩‍🍼 Learn about maternity items or processes from images")

        with gr.Row():
            input_image = gr.Image(type="pil", label="Input Image")
            input_prompt = gr.Textbox(
                lines=2, 
                label="Your Query", 
                placeholder="Describe what to detect, e.g., 'Categorize and label nursing items.'"
            )
            submit_button = gr.Button("Submit➡️")
        with gr.Row():
            output_image = gr.Image(type="pil", label="Labelled Image")
            response_text = gr.Textbox(label="Generated Text", placeholder="Bounding box results will appear here.")

        submit_button.click(
            fn=predict_bounding_boxes,
            inputs=[input_image, input_prompt],
            outputs=[output_image, response_text]
        )

        # Add Gr.Examples for Detection Prompts
        gr.Examples(
            examples=[
                ["Categorize and label all the nursing items in the image."],
                ["Detect toys in the image and categorize them by age group."],
                ["Identify each object in the image and label them clearly."],
                ["Locate feeding-related items like bottles, bowls, and spoons."],
                ["Detect and group clothing items such as onesies, socks, and hats."],
                ["Identify safety items such as baby monitors and baby gates."],
                ["Detect maternity items and categorize them as essentials or accessories."],
                ["Find baby furniture like cribs, changing tables, and high chairs."],
            ],
            inputs=[input_prompt],  # Correct input mapping
            outputs=[],  # No outputs directly from the example selection
            label="Example Prompts"
        )

    # Tab 2: Chat about Detected Items
    
    # Tab 2: Chat about Detected Items
    with gr.Tab("🧑‍🍼 💬Chat"):
        gr.Markdown("# 🤰 Chat about the detected items")

        with gr.Row():
            chatbot = gr.Chatbot(label="HiMa says")
        with gr.Row():
            question_input = gr.Textbox(
                lines=2, 
                label="Ask a Question", 
                placeholder="Ask about the detected objects, e.g., 'What age group is suitable for this toy?'"
            )
            web_search_checkbox = gr.Checkbox(label="Enhance with Web Search", value=False)
            chat_button = gr.Button("Submit")

        chat_button.click(
            fn=update_chatbot,
            inputs=[question_input, response_text, web_search_checkbox, chatbot],
            outputs=[chatbot]
        )

        # Add Gr.Examples for Chat Questions
        gr.Examples(
            examples=[
                ["What age group is suitable for this toy?"],
                ["Where can I buy this?"],
                ["Which one will be the cheapest?"],
                ["Compare the items based on current price and review if available."],
                ["What is the best way to organize these nursing items?"],
                ["Are these items safe for newborns?"],
                ["What is the purpose of the detected objects?"],
                ["Can you suggest alternative products for this item?"],
                ["What are the safety guidelines for using these items?"],
                ["How should I clean and maintain these objects?"],
                ["Can I repurpose any of these items for toddlers?"],
            ],
            inputs=[question_input],  # Correct input mapping
            outputs=[],  # No outputs directly from the example selection
            label="Example Questions"
        )
        
    with gr.Tab("🎙️📻 Podcast"):
        gr.Markdown("# 🎙️ MommyBird's Podcast")

        with gr.Row():
           podcast_button = gr.Button("Generate Podcast 🎧")
        with gr.Row():
           custom_topic_input = gr.Textbox(
           label="Custom Topic (Optional)",
           placeholder="Enter your topic here, e.g., 'Benefits of baby monitors.'"
          )
        with gr.Row():
            podcast_audio_output = gr.Audio(label="Generated Podcast Audio")
            podcast_script_output = gr.Textbox(
            label="Transcript",
            placeholder="Podcast script will appear here."
            )
        

    # Connect the podcast generation and audio functions
        podcast_button.click(
            fn=lambda custom_topic, response_text: (
            generate_podcast(custom_topic if custom_topic.strip() else response_text),
            gtpodcast_script_to_audio(generate_podcast(custom_topic if custom_topic.strip() else response_text))
        ),
        inputs=[custom_topic_input, response_text],
        outputs=[podcast_script_output, podcast_audio_output]
    )  
# Launch the app
app.launch()
