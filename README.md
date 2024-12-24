
# HiMa: Multimodal AI Assistant for New Moms

HiMa is a creative multimodal AI application designed to simplify life for expecting mothers. Powered by Gemini 2.0 and integrated with cutting-edge AI capabilities, HiMa leverages spatial understanding, multimodal reasoning, and external tool automation to deliver a seamless, intuitive experience. With HiMa, users can:

- Identify items in a photo (e.g., taken at a kid's store, maternity store, hospital, etc.)
- Ask follow-up questions about the identified items.
- Perform automated Google searches for grounded responses.
- Generate custom podcasts based on image-based conversations or specified topics.

This project was developed with new moms in mind, aiming to reduce the complexity of their daily tasks while ensuring a safe, responsible AI experience.

---

## Features

1. **Item Identification**:
   - Take a photo of items in a store, and HiMa identifies them with context-specific labels.
   - Outputs are enhanced with bounding boxes drawn over the identified objects.
     
![detect](https://github.com/user-attachments/assets/a1f01cd7-c3d3-42ab-b31a-bc4c9edd1337)

2. **Interactive Conversations**:
   - Users can chat with HiMa about the items identified in the photo.
   - HiMa provides detailed answers and can even conduct Google searches to enrich the responses.
    ![chat](https://github.com/user-attachments/assets/07334ef8-f7db-4d65-a3be-17829d718a3a)


3. **Custom Podcasts**:
   - HiMa generates personalized podcasts based on:
     - Conversations about identified items.
       ![podcast1](https://github.com/user-attachments/assets/9daa8e1e-ad44-47f8-8b83-0f477e45e2b9)

     - User-specified topics.
   - Podcasts include transcripts and audio files.
    ![podcast2](https://github.com/user-attachments/assets/3d9f9204-5256-41e3-86ac-4da8d6fd64fc)


4. **Responsible AI**:
   - Safety settings ensure that content adheres to ethical guidelines, avoiding harmful or sensitive outputs.
   - "Block_Low_and_above" safety level is enforced for responsible content generation.

---

## Getting Started

### Prerequisites

1. **Google Studio API Key**:
   - Follow [this guide](https://medium.com/@turna.fardousi/building-a-multimodal-chatbot-with-gemini-api-8015bfbee538) to create and obtain your API key.

2. **Hugging Face Account**:
   - Sign up on Hugging Face and follow [this guide](https://medium.com/@turna.fardousi/building-a-multimodal-chatbot-with-gemini-api-8015bfbee538) to set up your space.

---

### Usage

1. Create an `app.py` file following the workflow outlined below:

   - Import necessary libraries.
   - Set up the API key and model configuration.
   - Define system instructions for bounding box identification, podcasts, and safety settings.
   - Implement functions for:
     - Parsing generated output into JSON.
     - Drawing bounding boxes on images.
     - Chat functionality with optional Google search.
     - Podcast generation (audio and transcript).
   - Develop a Gradio-based user interface.

2. Commit the changes and deploy:
   ```bash
   git add app.py
   git commit -m "Initial deployment"
   git push origin main
   ```

3. Access your app via the Hugging Face space or local server.

---

## Development Workflow

### System Instructions

- Bounding Box:
  - Context: Maternity and baby-related items.
- Podcast:
  - Duration constraints.
  - Avoids medical diagnosis.
- Safety Settings:
  - "Block_Low_and_above" to ensure responsible AI.

### Key Functions

1. **Output Parsing**:
   - Parses AI output into structured JSON format for better usability.

2. **Bounding Box Drawing**:
   - Draws visual boxes on images around identified items.

3. **User Chat with AI**:
   - Enables dynamic, context-aware conversations.
   - Google search integration for automatic responses.

4. **Podcast Generation**:
   - Produces personalized audio podcasts with optional topic customization.

### User Interface

- Built using **Gradio**, a Python library for creating customizable web interfaces.
- Connects backend functions to provide an intuitive, user-friendly experience.

---

## Deployment

1. Deploy to Hugging Face Spaces:
   - Upload `app.py` and `requirements.txt`.
   - Set your space visibility (private or public).

2. Run the app locally:
   ```bash
   python app.py
   ```

3. Access the app via browser or API endpoint.

---

## Limitations

To manage the limited quota for Gemini 2.0 API usage, the HiMa Space is currently private. However, you can test the application by setting up your own Space on Hugging Face. Follow these steps:

1. **Create a New Space on Hugging Face**:
   - Log in to your Hugging Face account.
   - Navigate to the [Spaces page](https://huggingface.co/spaces) and click on "Create new Space".
   - Fill in the required details:
     - **Owner**: Your Hugging Face username.
     - **Space name**: Choose a relevant name for your Space.
     - **Space SDK**: Select "Gradio" as the SDK.
     - **Template**: Choose "Blank".
     - **Hardware**: Select the appropriate hardware for your application.
     - **Visibility**: Set to "Public" or "Private" as per your preference.
   - Click "Create Space" to initialize your new Space.

2. **Set Your Google API Key as a Secret**:
   - In your newly created Space, go to the "Settings" tab.
   - Scroll down to the "Repository secrets" section.
   - Click on "Add a new secret".
   - Enter a name for your secret (e.g., `GEMINI_API_KEY`) and paste your Google API key as the value.
   - Save the secret. This will store your API key securely and make it accessible as an environment variable within your Space.

3. **Upload the `app.py` and `requirements.txt` Files**:
   - In your Space, click on the "Files and versions" tab.
   - Click on "Add file" and select "Upload file".
   - Upload your `app.py` file.
   - Repeat the process to upload the `requirements.txt` file.
   - Once both files are uploaded, the Space will automatically detect the `app.py` file and start building the application.

4. **Access and Test Your Application**:
   - After the build process completes, navigate to the "App" tab in your Space.
   - You should see your application interface running.
   - Test the features of HiMa as intended.

For more detailed guidance, refer to the [Hugging Face Spaces documentation](https://huggingface.co/docs/hub/spaces-overview).

By following these steps, you can create your own instance of the HiMa application and test its functionalities without being affected by the limitations of the original Space. 
---

## Community Contribution

1. **Fork the Repository**:
   - Feel free to fork and improve the codebase.
   - Please provide credit when sharing updates.

2. **Ideas for Improvement**:
   - Enhance UI/UX.
   - Introduce new features (e.g., multilingual support).
 
3. **Products of HiMA project**:
   - **MommyBird Podcast Youtube:** [Listen at Youtube Podcast](https://youtu.be/nD-2ud0HsAA?si=Jn3fBcl9oj5k-_Nr)
   - **MommyBird Podcast Youtube Music:** [Listen at Youtube Podcast](https://music.youtube.com/playlist?list=PLsOZIEeQQBvMoeme5NKhGum-Iku64es8j&si=JI6zRk9wuX24nNEp)
   - **MommyBird Podcast RSS:**[Listen directly at the RSS Website](https://rss.com/podcasts/mommybird-podcast/)
## License

HiMa is released under the [MIT License](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository). By contributing, you agree to the terms of this license.

---
## Contact

For questions or feedback, please reach out:

- **Email**: rferd068@uottawa.ca
- **GitHub Issues**: Submit issues or feature requests on the [Issues page](https://github.com/turna1/HiMa/issues).

---

Thank you for using HiMa! Together, let's make life easier for moms everywhere.


