import os
from openai import OpenAI
from typing import List, Dict, Any

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze user query to extract relevant metrics and time ranges."""
        system_prompt = """
        You are a Grafana metrics expert. Analyze the user query to identify:
        1. The type of metrics they're looking for (CPU, memory, disk, network, etc.)
        2. Any time range specifications
        3. Specific components or services mentioned
        Format your response as a structured analysis.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            
            # Extract the assistant's response
            analysis = response.choices[0].message.content
            
            # Process the analysis to extract key information
            # This is a simple implementation - you can enhance it based on your needs
            return {
                "original_query": query,
                "enhanced_analysis": analysis,
                "success": True
            }
            
        except Exception as e:
            return {
                "original_query": query,
                "error": str(e),
                "success": False
            }