from googleapiclient import discovery
import json

API_KEY = 'AIzaSyCOY4EplffIGy2mERdqSZOykQJUbhNWOl8'

analyze_request = {
    'comment': { 'text': 'friendly greetings from python' },
    'requestedAttributes': {'TOXICITY': {}}
    }

def check_toxicity(message: str) -> dict:

    client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
    )

    

    response = client.comments().analyze(body=message).execute()

    # result =  json.dumps(response, indent=2)
   
    toxicity_score = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
    
    return toxicity_score


if __name__ == '__main__':
    print(check_toxicity(analyze_request))