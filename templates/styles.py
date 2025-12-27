"""
Modern color schemes and design styles for PowerPoint presentations
"""

from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor

class ColorScheme:
    """Color palette for presentations"""
    
    VIBRANT = {
        'primary': RGBColor(138, 43, 226),  # Blue Violet
        'secondary': RGBColor(255, 20, 147),  # Deep Pink
        'accent': RGBColor(0, 191, 255),  # Deep Sky Blue
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(20, 20, 40),  # Dark Navy
    }
    
    PROFESSIONAL = {
        'primary': RGBColor(41, 128, 185),  # Professional Blue
        'secondary': RGBColor(52, 73, 94),  # Dark Gray Blue
        'accent': RGBColor(230, 126, 34),  # Carrot Orange
        'text': RGBColor(44, 62, 80),  # Midnight Blue
        'background': RGBColor(236, 240, 241),  # Light Gray
    }
    
    NATURE = {
        'primary': RGBColor(39, 174, 96),  # Emerald Green
        'secondary': RGBColor(22, 160, 133),  # Green Sea
        'accent': RGBColor(241, 196, 15),  # Sun Flower
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(44, 62, 80),  # Midnight Blue
    }
    
    TECH = {
        'primary': RGBColor(52, 152, 219),  # Dodger Blue
        'secondary': RGBColor(155, 89, 182),  # Amethyst
        'accent': RGBColor(26, 188, 156),  # Turquoise
        'text': RGBColor(236, 240, 241),  # Clouds
        'background': RGBColor(44, 62, 80),  # Wet Asphalt
    }
    
    SUNSET = {
        'primary': RGBColor(231, 76, 60),  # Alizarin
        'secondary': RGBColor(192, 57, 43),  # Pomegranate
        'accent': RGBColor(243, 156, 18),  # Orange
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(44, 62, 80),  # Midnight Blue
    }
    
    OCEAN = {
        'primary': RGBColor(0, 119, 182),  # Deep Ocean Blue
        'secondary': RGBColor(0, 180, 216),  # Bright Teal
        'accent': RGBColor(127, 219, 255),  # Light Cyan
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(11, 37, 69),  # Deep Navy
    }
    
    FOREST = {
        'primary': RGBColor(34, 87, 50),  # Forest Green
        'secondary': RGBColor(76, 129, 68),  # Sage Green
        'accent': RGBColor(212, 175, 55),  # Gold
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(40, 54, 44),  # Dark Forest
    }
    
    BERRY = {
        'primary': RGBColor(142, 68, 173),  # Purple
        'secondary': RGBColor(204, 87, 166),  # Magenta
        'accent': RGBColor(255, 118, 194),  # Pink
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(44, 27, 63),  # Dark Purple
    }
    
    MONOCHROME = {
        'primary': RGBColor(60, 60, 60),  # Dark Gray
        'secondary': RGBColor(100, 100, 100),  # Medium Gray
        'accent': RGBColor(180, 180, 180),  # Light Gray
        'text': RGBColor(240, 240, 240),  # Off White
        'background': RGBColor(20, 20, 20),  # Almost Black
    }
    
    WARM = {
        'primary': RGBColor(230, 126, 34),  # Orange
        'secondary': RGBColor(211, 84, 0),  # Dark Orange
        'accent': RGBColor(255, 195, 0),  # Yellow
        'text': RGBColor(255, 255, 255),  # White
        'background': RGBColor(61, 43, 31),  # Dark Brown
    }
    
    @staticmethod
    def get_random_scheme():
        """Get a random color scheme"""
        import random
        schemes = [
            ColorScheme.VIBRANT,
            ColorScheme.PROFESSIONAL,
            ColorScheme.NATURE,
            ColorScheme.TECH,
            ColorScheme.SUNSET,
            ColorScheme.OCEAN,
            ColorScheme.FOREST,
            ColorScheme.BERRY,
            ColorScheme.MONOCHROME,
            ColorScheme.WARM
        ]
        return random.choice(schemes)


class Typography:
    """Typography scale for presentations"""
    
    TITLE_FONT = 'Montserrat'
    BODY_FONT = 'Open Sans'
    
    # Font sizes - Reduced to prevent overflow
    HERO_SIZE = Pt(54)     # Was 60
    TITLE_SIZE = Pt(36)    # Was 44
    SUBTITLE_SIZE = Pt(24) # Was 28
    HEADING_SIZE = Pt(28)  # Was 32
    BODY_SIZE = Pt(16)     # Was 18
    CAPTION_SIZE = Pt(12)  # Was 14


class Layout:
    """Layout dimensions and spacing"""
    
    # Margins
    MARGIN_TOP = Inches(0.5)
    MARGIN_BOTTOM = Inches(0.5)
    MARGIN_LEFT = Inches(0.5)
    MARGIN_RIGHT = Inches(0.5)
    
    # Spacing
    SPACING_SMALL = Inches(0.2)
    SPACING_MEDIUM = Inches(0.5)
    SPACING_LARGE = Inches(1.0)
    
    # Standard dimensions
    SLIDE_WIDTH = Inches(10)
    SLIDE_HEIGHT = Inches(7.5)
