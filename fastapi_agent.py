import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Load environment variables from .env file ---
# NOTE: In a real-world deployment, you should use environment variables
# configured on the server, not a .env file.
load_dotenv()

# --- Initialize FastAPI App ---
app = FastAPI(title="Wink & Wear Chatbot Agent", description="Backend service for the Oracle chatbot.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic model for the request body ---
class ChatMessage(BaseModel):
    """Represents a chat message sent from the frontend."""
    message: str

# --- The comprehensive knowledge base for the Oracle chatbot ---
# This combines all provided information from the SRS, feasibility study, and website.
knowledge_text = """
Project Name: Wink & Wear - A 3D Social Fashion Metaverse

Slogan: "The next-gen closet is digital."

Purpose: An AI-powered online fashion styling platform that aims to transform online fashion by connecting users with expert stylists and integrating advanced AI and AR technologies. It is the vibrant heart of the metaverse, where users can explore, connect, and define their digital identity.

Key Features
Personalized AI Styling: A smart fashion assistant that uses AI to analyze a user's body type, style preferences, and even the weather to recommend perfect outfits and accessories. It's a hybrid approach that uses both AI and human stylists for the best advice.

Virtual Try-On: A "magical mirror" that uses Augmented Reality (AR) and a webcam to let users see how new clothes would look on them before they buy.

Digital Wardrobe Management: A "digital closet" where users can upload pictures of their clothes. The platform organizes them and uses AI to suggest new outfits by mixing and matching existing items.

AI Chatbot & Real-Time Chat: The "AI Chatbot," known as "The Oracle," is a super-smart robot available 24/7 to help with fashion questions. Users can also use the "Real-time Chat" feature to talk to a real human stylist.

Voice Assistant: A feature that allows users to talk to the platform just like a friend, using their voice to ask for help.

Role-Based Platform: The platform is designed with three different user roles:

Users: The main audience who manages their profile, digital closet, and receives recommendations.

Stylists: Fashion professionals who have a special dashboard to manage clients and provide advice.

Admins: The team that manages the users and stylists to ensure the platform runs smoothly.

Monetization & Subscriptions: The platform offers subscriptions to give users special access to more advanced AI tools and professional stylists. It may also earn money by recommending products from different stores.

Website Navigation & Sections
The platform is organized into six main sections:

The Nexus (Home Page): The central hub where the user's journey begins. From here, they can explore featured collections and their digital closet.

The Atelier (Avatar & Wardrobe): The personal design studio for sculpting an avatar and curating a wardrobe. It includes a "Digital Mirror" and "Customization Tools."

The Runway (Collections & Shop): The section for discovering and acquiring new fashion items. Users can buy both digital and physical versions of items.

Social Lounges: Community spaces for connecting, collaborating, and showing off style. Users can join themed lounges or create private rooms to share digital closets with friends.

Chronos Gallery (About): An interactive data-stream detailing the project's journey, including key milestones and a future vision for a User-Generated Content (UGC) Design Studio.

The Oracle (Chatbot): The contact and support section, where the AI concierge "The Oracle" assists with navigation, avatar customization, and general questions.

Technical & Team Details
Technology Stack: The frontend is built with React.js/Next.js, and the backend uses Python/Django. It relies on a PostgreSQL database, Cloudinary/Firebase for media storage, and key AI/AR services like the Gemini API, Cloud Vision API, and WebAR.js.

Team: The project team, named "Team Shaolins," includes Tanishq Singh (Project Lead), Ayush Aman, Sayan Roy Chowdhury, and Abhijeet Kumar.
"""

# --- System prompt for the Gemini model ---
system_prompt = f"""
You are "Oracle," a helpful, friendly, and knowledgeable AI concierge for the "Wink & Wear" platform. Your role is to interact with users, assist them with navigation, explain features, and answer any questions about the project's vision and roadmap.
Your responses should be concise, encouraging, and based *only* on the information provided in the knowledge base below. Use your AI features in a limited way. If a user asks about a topic irrelevant to the knowledge base, politely state that you can only provide information about the "Wink & Wear" platform and its features.

--- KNOWLEDGE BASE ---
{knowledge_text}
----------------------
"""

# --- API Configuration ---
# NOTE: The API key should be securely stored and not hardcoded.
API_KEY = os.getenv("GOOGLE_API_KEY", "")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# --- API Endpoint to handle chat messages ---
@app.post("/chat")
def chat_with_oracle(message_data: ChatMessage):
    """
    Receives a user message, calls the Gemini API to get a response, and returns it.
    """
    user_message = message_data.message.strip()

    payload = {
        "contents": [
            # The system prompt is included with the 'user' role.
            {"role": "user", "parts": [{"text": system_prompt}]},
            # The user's question is also included with the 'user' role.
            {"role": "user", "parts": [{"text": f"User's question: {user_message}"}]}
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    # Simple retry logic with exponential backoff
    for i in range(3):
        try:
            response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            candidate = result.get("candidates", [])[0]
            text = candidate["content"]["parts"][0]["text"]
            
            return {"message": text}
        except requests.exceptions.HTTPError as errh:
            print(f"Http Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"OOps: Something Else {err}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break # Exit loop for non-request errors

    return {"message": "I'm sorry, I'm having trouble connecting right now. Please try again later."}
