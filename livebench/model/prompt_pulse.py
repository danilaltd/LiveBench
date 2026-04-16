import requests
import os

def chat_completion_prompt_pulse(model, messages, api_dict, **kwargs):
    api_key = os.environ.get("LIVEBENCH_API_KEY") or api_dict.get("api_key")
    base_url = api_dict.get("api_base")
    print(f"model is {model}")
    if not base_url or base_url == "None":
        base_url = "https://llm-manager.etacar.io/api/external"
    base_url = base_url.rstrip('/')

    headers = {
        "x-api-token": api_key,
        "Content-Type": "application/json"
    }

    target_model_name = "google:gemini-3-pro-preview"
    agent_id = None

    try:
        agent_id = os.getenv("LIVEBENCH_AGENT_ID")
        
        payload = {
            "title": f"LiveBench {target_model_name}",
            "model": target_model_name
        }

        if "orion" in model:
            payload["aiSuperAgent"] = '6943f4cdf708b1d719faf764'
            print(f"--- [DEBUG] Mode: Agentic (orion) ---")
        elif "elen" in model:
            payload["aiSuperAgent"] = '6970986b4e761c9b775f86c6'
            print(f"--- [DEBUG] Mode: Agentic (elen) ---")

        conv_res = requests.post(f"{base_url}/conversations", headers=headers, json=payload, timeout=30)
        
        if not conv_res.ok:
            print(f"Server rejected conversation creation: {conv_res.status_code} - {conv_res.text}")
            conv_res.raise_for_status()

        conv_data = conv_res.json()
        conv_id = conv_data.get('_id')
        
        if not conv_id:
            raise Exception(f"Missing _id in response: {conv_data}")

        prompt = messages[-1]['content']
        msg_res = requests.post(
            f"{base_url}/conversations/{conv_id}/messages", 
            headers=headers, 
            json={"message": prompt}, 
            timeout=300
        )
        msg_res.raise_for_status()
        
        res_json = msg_res.json()
        content = res_json['assistantMessage']['content']
        
        return content, 0 

    except Exception as e:
        print(f"Error in PromptPulse API: {e}")
        raise e