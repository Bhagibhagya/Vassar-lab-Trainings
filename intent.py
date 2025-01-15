import openai
import os


# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')
 # Replace with your OpenAI API key

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

    try:
        # Use the correct chat completion endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can also use "gpt-4" for GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.7
        )

        # Extract the classification result from the response
        intent = response['choices'][0]['message']['content'].strip()
        return intent
    except Exception as e:
        return f"Error: {e}"

# Test the system
user_query = input("Enter a query: ")
result = classify_intent(user_query)
print(f"Intent Classification Result:\n{result}")
