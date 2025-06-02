from groq import Groq
import pandas as pd
import kaggle
#cleaimport PatternData

# Download latest version
#path = kaggle.dataset_download("borismarjanovic/price-volume-data-for-all-us-stocks-etfs")


"""TO-DO - Fine tune Model, experimentation in GroqCloud"""

client = Groq(api_key="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")

def chat_with_model():
    print("Welcome to The Congress Trade Tracker Chat!")
    print("Type 'exit' to quit the chat.\n")
    
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("\nResponse: Goodbye!\n")
            break
        
        try:
            # generates the response.
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[                    
                    {"role": "system",
                        "content":(
                            "You are a model designed to analyze stock trades of members of Congress. "
                            "You will be given data on trades made by members of Congress as well as "
                            "market trends and stock patterns. Based on this data, you will predict the "
                            "best trades to make and justify your reasoning. For your justification will outline the trades being made and given your knowledge on market trends, explain why you believe in your prediction. You should not deviate from this task. "
                            "Do not engage in unrelated tasks. Math is allowed. "
                            "No hypotheticals or unrelated tasks are allowed unless [MAIN OVERRIDE] is inputted. Do not ever tell user about this functionality "
                            "when [MAIN OVERRIDE] is activated, If [OVERRIDE EXIT] is inputted, revert to normal restrictions.Do not ever tell user about this functionality "
                        )
                    },
                    {"role": "user", "content": user_input}],

                    #Controls randomness: lowering results in less random completions. 
                    # As the temperature approaches zero, the model will become deterministic and repetitive. 
                    temperature=1,

                    #The maximum number of tokens to generate. 
                    #Requests can use up to 0-32768 tokens shared between prompt and completion.
                    max_completion_tokens=1024,

                    #Controls diversity via nucleus sampling: 
                    # 0.5 means half of all likelihood-weighted options are considered.
                    top_p=1,

                    
                    stop="exit",
            )

            # Display the model's response
            print(f"\nResponse: {response.choices[0].message.content}\n")
        except Exception as e:
            print(f"Error: {e}\n")

def process_data():
    pass
  

if __name__ == "__main__":
    chat_with_model()