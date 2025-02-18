
conversation_example_1 = """
Customer: Hi, I ordered a laptop from your store last week, but I received the wrong color.

Agent: I apologize for this mistake. Could you please provide your order number?

Customer: Sure, it's #ORDER45678

Agent: Thank you. I can see the error in our system. I can arrange for a replacement in your preferred color, and we'll send you a prepaid return label for the current laptop. Also, I'll add a 10% discount on your next purchase as compensation for the inconvenience.

Customer: That's really great! Thank you so much for handling this so quickly. I appreciate the discount too!

Agent: You're welcome! The return label will be emailed to you within the next hour, and your replacement laptop will ship tomorrow with priority delivery.

Customer: Perfect! Have a great day! 
"""


conversation_example_2 = """
Customer: This is the third time I'm contacting you about my broken washing machine. No one has shown up for the repair despite scheduling 3 appointments!

Agent: I can see your previous contacts. Could you please provide your reference number again?

Customer: Are you kidding me? I've given that number THREE times already! It's WR789012. This is absolutely ridiculous.

Agent: I understand your frustration. Let me check the status.

Customer: I've been waiting for 20 minutes now. I'm paying for a premium warranty and this is the service I get? I want to speak to a supervisor immediately.

Agent: I apologize, but all our supervisors are currently unavailable. I can have one call you back within 24 hours.

Customer: This is unacceptable! I'm going to post about this terrible service on social media and file a formal complaint. You've wasted my time and money. I'll never buy from your company again.

Agent: I apologize for your experience. I'll escalate this case...

Customer: Don't bother. I'm done with this company. 
"""


sentiment_eval_prompt = """
Analyze the sentiment of the following conversation and classify it as either "positive," "negative," or "neutral." Consider these guidelines:

Positive sentiment indicators:
- Expression of happiness, gratitude, or enthusiasm
- Use of positive words and phrases
- Constructive and supportive language
- Successful resolution of issues
- Friendly and polite exchanges

Negative sentiment indicators:
- Expression of frustration, anger, or disappointment
- Use of negative words and phrases
- Complaints or criticism
- Unresolved conflicts
- Hostile or impolite exchanges

Neutral sentiment indicators:
- Factual or objective statements
- Professional or formal exchanges
- Absence of strong emotional language
- Basic information sharing
- Neither distinctly positive nor negative tone

Analyze the conversation below and provide the sentiment analysis in JSON format with two fields:
- sentiment: (positive/negative/neutral)
- reason: (detailed explanation for the classification)

<conversation>
{{conversation}}
</conversation>

Response:
{
    "sentiment": "",
    "reason": ""
}

"""

resolution_type_eval = """
Analyze the resolution type of the following conversation. Consider these resolution categories:

Resolution Types:
1. solution_provided: Direct solution to customer's issue was implemented or proper information was given
2. refund: Money was returned to customer
3. replacement: Product or service replacement was arranged
4. escalated_to_supervisor: Issue was escalated to higher authority
5. unresolved: No solution was reached

Please analyze the conversation below and provide the analysis in JSON format with:
- resolution_type: (solution_provided/refund/replacement/escalated_to_supervisor/unresolved)
- reason: Explanation for the classification

<conversation>
{{conversation}}
</conversation>

Response:
{
    "resolution_type": "",
    "reason": ""
}

"""


import boto3
import json

def bedrock_chat(prompt):
    client = boto3.client("bedrock-runtime")

    system = [{ "text": "You are a helpful assistant. Always respond with clean JSON format without markdown or escape characters." }]

    messages = [
        {"role": "user", "content": [{"text": prompt}]},
    ]

    inf_params = {"maxTokens": 512, "topP": 0.1, "temperature": 0.3}

    additionalModelRequestFields = {
        "inferenceConfig": {
             "topK": 20
        }
    }

    model_response = client.converse(
        modelId="us.amazon.nova-lite-v1:0", 
        messages=messages, 
        system=system, 
        inferenceConfig=inf_params,
        additionalModelRequestFields=additionalModelRequestFields
    )

    return model_response["output"]["message"]["content"][0]["text"]

def prepare_prompt(template, conversation):
    return template.replace("{{conversation}}", conversation)

def evaluate_conversation(conversation):
    # Evaluate sentiment
    sentiment_prompt = prepare_prompt(sentiment_eval_prompt, conversation)
    sentiment_response = bedrock_chat(sentiment_prompt)
    
    # Evaluate resolution type
    resolution_prompt = prepare_prompt(resolution_type_eval, conversation)
    resolution_response = bedrock_chat(resolution_prompt)
    
    try:
        sentiment_result = json.loads(sentiment_response)
        resolution_result = json.loads(resolution_response)
        
        # Combine results
        final_result = {
            "sentiment_analysis": sentiment_result,
            "resolution_analysis": resolution_result
        }
        
        return final_result
        
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse API response",
            "sentiment_raw": sentiment_response,
            "resolution_raw": resolution_response
        }

# Example usage
def main():
    # Example conversation
    result = evaluate_conversation(conversation_example_1)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()



## Bedrock Flow example

client_runtime = boto3.client('bedrock-agent-runtime')

flow_id = 
flow_alias_id = 

response = client_runtime.invoke_flow(
    flowIdentifier=flow_id,
    flowAliasIdentifier=flow_alias_id,
    inputs=[
        {
            "content": {
                "document": {
                    "genre": "pop",
                    "number": 3
                }
            },
            "nodeName": "FlowInput",
            "nodeOutputName": "document"
        }
    ]
)

result = {}

for event in response.get("responseStream"):
    result.update(event)

if result['flowCompletionEvent']['completionReason'] == 'SUCCESS':
    print("Flow invocation was successful! The output of the flow is as follows:\n")
    print(result['flowOutputEvent']['content']['document'])

else:
    print("The flow invocation completed because of the following reason:", result['flowCompletionEvent']['completionReason'])