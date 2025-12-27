
import os
from dotenv import load_dotenv
from image_service import ImageService
from templates.modern_template import ModernTemplate

# Load env variables (for API Key)
load_dotenv()

def generate_proof():
    # 1. Initialize Service
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not api_key:
        print("❌ Error: UNSPLASH_ACCESS_KEY not found in .env")
        return

    service = ImageService(unsplash_key=api_key)
    
    print("📸 Fetching image directly from Unsplash (bypassing Pollinations)...")
    
    # 2. Fetch directly from Unsplash to ensure we get the credit object
    # We use "nature" as it usually returns good results
    result = service._fetch_from_unsplash("nature landscape", 1200, 800)
    
    if not result:
        print("❌ Failed to fetch from Unsplash. Quota exceeded or Invalid Key.")
        return

    print(f"✅ Image obtained: {result['path']}")
    print(f"ℹ️  Credit info: {result['credit']}")

    # 3. Simulate Download Trigger (Compliance Check)
    if result.get('download_url'):
        print("🔄 Triggering 'Download' endpoint for compliance...")
        service.trigger_download(result['download_url'])

    # 4. Generate Presentation
    print("📝 Creating proof slide...")
    tmpl = ModernTemplate()
    tmpl.add_title_slide("Unsplash API Verification", "Attribution & Hotlinking Demo")
    
    bullets = [
        "Unsplash API Compliance Demo",
        "1. Image sourced from Unsplash API",
        "2. Attribution visible in bottom-right",
        "3. Download endpoint triggered upon generation"
    ]
    
    # Add slide with explicit credit
    tmpl.add_content_slide(
        "Proper Attribution", 
        bullets, 
        image_path=result['path'], 
        credit=result['credit']
    )
    
    # Save
    if not os.path.exists("generated_presentations"):
        os.makedirs("generated_presentations")
        
    output_path = "generated_presentations/Unsplash_Compliance_Proof.pptx"
    tmpl.save(output_path)
    print(f"\n🎉 Success! Proof generated: {output_path}")
    print("👉 Open this file and screenshot the SECOND slide for your application.")

if __name__ == "__main__":
    generate_proof()
