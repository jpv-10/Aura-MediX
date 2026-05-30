import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("AIzaSyAzf83l4MHLsPSjTvury_hUCPFQdQxphqk"))

model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Say hello in one line as a medical assistant")

print(response.text)