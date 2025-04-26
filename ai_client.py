from transformers import pipeline

class AIClient:
    def __init__(self):
        # Initialize a free text-generation model
        self.classifier = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')
        self.generator = pipeline('text-generation', model='distilgpt2')

    def analyze_query(self, query):
        try:
            # Analyze sentiment and context
            sentiment = self.classifier(query)[0]
            
            # Generate enhanced query
            enhanced = self.generator(
                query,
                max_length=50,
                num_return_sequences=1,
                pad_token_id=50256
            )[0]['generated_text']

            return {
                'success': True,
                'enhanced_analysis': enhanced
            }
        except Exception as e:
            print(f"AI Analysis Error: {str(e)}")
            return {
                'success': False,
                'enhanced_analysis': query
            }