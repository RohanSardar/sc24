import google.generativeai as genai

genai.configure(api_key="AIzaSyCqvnmPueyfiB9tCiSGGY6PbkAPctBPakk")

generation_config = {"temperature": 0.4, "top_p": 1, "top_k": 32, "max_output_tokens": 4096, }

safety_settings = [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                   {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                   {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                   {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},]

model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def get_validation(bin):
    image_parts = [{"mime_type": "image/jpeg", "data": bin.getvalue()}, ]

    prompt_parts = [
        "describe only in 'yes' or 'no' whether the picture is depicting something good for the environment",
        image_parts[0], ]

    response = model.generate_content(prompt_parts)
    return response