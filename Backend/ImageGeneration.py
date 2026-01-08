import requests
import os
from datetime import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")

# API endpoint for Stable Diffusion or similar models
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Ensure Images directory exists
if not os.path.exists("Images"):
    os.makedirs("Images")

def GenerateImage(prompt, filename=None):
    """
    Generate an image using Hugging Face's Inference API
    
    Args:
        prompt (str): The text prompt for image generation
        filename (str): Optional custom filename
    
    Returns:
        str: Status message with file path or error
    """
    try:
        if not HuggingFaceAPIKey:
            return "Error: HuggingFace API key not found in .env file"
        
        headers = {
            "Authorization": f"Bearer {HuggingFaceAPIKey}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "options": {
                "wait_for_model": True
            }
        }
        
        print(f"🎨 Generating image for: '{prompt}'")
        print("⏳ This may take a moment...")
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join("Images", filename)
            
            # Save the image
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return f"✅ Image generated successfully and saved to: {filepath}"
        
        elif response.status_code == 503:
            return "⚠️ Model is loading. Please try again in a few moments."
        
        elif response.status_code == 401:
            return "❌ Error: Invalid API key. Please check your HuggingFace API key."
        
        else:
            error_msg = response.json().get('error', 'Unknown error')
            return f"❌ Error generating image: {error_msg}"
    
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. The model might be busy. Please try again."
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def GenerateImageWithRetry(prompt, filename=None, max_retries=3):
    """
    Generate an image with retry logic for model loading
    
    Args:
        prompt (str): The text prompt
        filename (str): Optional custom filename
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        str: Status message
    """
    import time
    
    for attempt in range(max_retries):
        result = GenerateImage(prompt, filename)
        
        if "Model is loading" in result and attempt < max_retries - 1:
            print(f"🔄 Retry attempt {attempt + 1}/{max_retries}...")
            time.sleep(10)  # Wait 10 seconds before retrying
            continue
        
        return result
    
    return "❌ Failed to generate image after multiple attempts. Please try again later."

# Alternative: Using Pollinations.ai (Free, no API key required)
def GenerateImageFree(prompt, filename=None):
    """
    Generate an image using Pollinations.ai (Free alternative)
    
    Args:
        prompt (str): The text prompt
        filename (str): Optional custom filename
    
    Returns:
        str: Status message
    """
    try:
        # Pollinations.ai endpoint
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        
        print(f"🎨 Generating image for: '{prompt}'")
        print("⏳ Downloading...")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join("Images", filename)
            
            # Save the image
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return f"✅ Image generated successfully and saved to: {filepath}"
        else:
            return f"❌ Error: Failed to generate image (Status: {response.status_code})"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    print("=" * 70)
    print("AI Image Generation System")
    print("=" * 70)
    print("\nOptions:")
    print("1. Use HuggingFace API (requires API key in .env)")
    print("2. Use Pollinations.ai (Free, no API key required)")
    print("=" * 70)
    
    while True:
        print("\nCommands:")
        print("- Enter a prompt to generate an image")
        print("- Type 'free <prompt>' to use the free service")
        print("- Type 'exit' to quit")
        print("-" * 70)
        
        user_input = input("\nEnter prompt: ").strip()
        
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            print("⚠️  Please enter a valid prompt")
            continue
        
        # Check if user wants to use free service
        if user_input.lower().startswith("free "):
            prompt = user_input[5:].strip()
            result = GenerateImageFree(prompt)
        else:
            # Use HuggingFace with retry
            result = GenerateImageWithRetry(user_input)
        
        print(f"\n{result}\n")