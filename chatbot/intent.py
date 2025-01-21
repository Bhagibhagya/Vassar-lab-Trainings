<<<<<<< HEAD
import requests
import os

# Set Groq API Key
api_key = os.getenv("GROQ_API_KEY")  # Ensure your Groq API key is set as an environment variable
=======
import openai
import os

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure your API key is set as an environment variable
>>>>>>> e927348dffe8d5e0652ed1bf11c3588bd1af679a

# Define the few-shot prompt for intent classification
FEW_SHOT_PROMPT = """
You are an AI assistant trained to classify user queries into specific intents. The intents are:
- Booking: Queries about reservations.
- Cancel: Queries about cancellations.
- Feedback: Queries about sharing opinions.

Examples:
1. User Query: "I want to book a hotel."
   Intent: Booking

2. User Query: "Can you cancel my flight?"
   Intent: Cancel

3. User Query: "Your service is excellent."
   Intent: Feedback

Now, classify the following user query:
User Query: {query}
Intent:
"""

def classify_intent(user_query):
    # Format the prompt with the user query
    prompt = FEW_SHOT_PROMPT.format(query=user_query)

<<<<<<< HEAD
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the request payload
    data = {
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.7
    }

    try:
        # Send the request to the Groq API (URL will be handled externally)
        response = requests.post("https://api.groq.com/v1/classify-intent", json=data, headers=headers)  # Replace <GROQ_API_URL> with your actual URL

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            intent = result.get("choices", [{}])[0].get("text", "").strip()
            return intent
        else:
            return f"Error: API request failed with status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Test the system
if __name__ == "__main__":
    user_query = input("Enter a query: ")
    result = classify_intent(user_query)
    print(f"Intent Classification Result:\n{result}")
=======
    try:
        # Use the correct completion endpoint
        response = openai.Completion.create(
            model="text-davinci-003",  # Use the appropriate model, "text-davinci-003" is an excellent choice for completions
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )

        # Extract the classification result from the response
        intent = response.choices[0].text.strip()
        return intent
    except Exception as e:
        return f"Error: {e}"

# Test the system
user_query = input("Enter a query: ")
result = classify_intent(user_query)
print(f"Intent Classification Result:\n{result}")
>>>>>>> e927348dffe8d5e0652ed1bf11c3588bd1af679a
