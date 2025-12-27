
import asyncio
import os
from bot import PresentationGenerator, OPENROUTER_API_KEY
from templates.template_collection import (
    MinimalistTemplate, BoldModernTemplate, CorporateTemplate,
    CreativeTemplate, ElegantTemplate, GeometricTemplate
)
from templates.modern_template import ModernTemplate

async def generate_test_pres():
    pg = PresentationGenerator(OPENROUTER_API_KEY)
    
    # Test topics
    topics = [
        ("AI in 2024", "modern"),
        ("Clean Energy", "minimal"),
        ("Q4 Financial Results", "corporate"),
        ("Digital Art Trends", "creative"),
        ("Luxury Brand Strategy", "elegant"),
        ("Architecture Styles", "geometric"),
        ("Bold Marketing", "bold")
    ]
    
    print("Generating test presentations...")
    
    async def print_progress(text):
        print(f"  [Progress] {text}")
        
    for topic, template in topics:
        print(f"Generating {template}...")
        try:
            path = await pg.create_presentation(
                topic=topic,
                slide_count=3,
                language="English",
                template_name=template,
                progress_callback=print_progress
            )
            print(f"Created: {path}")
        except Exception as e:
            print(f"Failed {template}: {e}")

if __name__ == "__main__":
    asyncio.run(generate_test_pres())
