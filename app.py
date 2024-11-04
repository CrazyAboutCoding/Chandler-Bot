# Imports
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import discord
from transformers import pipeline

# Set up Flask for WhatsApp integration
app = Flask(__name__)

# Load the Hugging Face model for text generation
# You may want to replace "gpt2" with a fine-tuned model if you've trained it
chandler_bot = pipeline("text-generation", model="gpt2")

# Define a function to generate Chandler-style responses
def generate_chandler_response(user_message):
    # Craft a response prompt that might align with Chandler’s tone
    prompt = f"Respond sarcastically like Chandler Bing to: '{user_message}'"
    response = chandler_bot(prompt, max_length=50, num_return_sequences=1)
    chandler_reply = response[0]["generated_text"]
    return chandler_reply

# WhatsApp Bot Route using Twilio
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    user_message = request.form.get("Body")
    bot_reply = generate_chandler_response(user_message)
    
    # Set up Twilio's response format
    twilio_response = MessagingResponse()
    twilio_response.message(bot_reply)
    return str(twilio_response)

# Discord Bot Setup
client = discord.Client()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore messages from the bot itself

    # Check if the message is a command for Chandler Bot
    if message.content.startswith("!chandler"):
        user_message = message.content[len("!chandler "):]
        bot_reply = generate_chandler_response(user_message)
        await message.channel.send(bot_reply)

# Running both bots based on environment
if __name__ == "__main__":
    # Retrieve environment variables
    run_mode = os.getenv("RUN_MODE", "whatsapp")  # Default to WhatsApp

    if run_mode == "whatsapp":
        # Start Flask app for Twilio integration (WhatsApp bot)
        app.run(host="0.0.0.0", port=5000, debug=True)
    elif run_mode == "discord":
        # Start Discord client (Discord bot)
        discord_token = os.getenv("DISCORD_TOKEN")
        client.run(discord_token)
    else:
        print("Invalid RUN_MODE specified. Use 'whatsapp' or 'discord'.")
