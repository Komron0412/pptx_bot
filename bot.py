
"""
Telegram Bot for PowerPoint Generation
Creates beautiful presentations using OpenRouter AI and python-pptx
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    filters, ContextTypes, ConversationHandler
)
import aiohttp
import json
import asyncio

from image_service import ImageService
from templates.modern_template import ModernTemplate
from templates.styles import ColorScheme
from templates.template_collection import (
    get_random_template, MinimalistTemplate, BoldModernTemplate, 
    CorporateTemplate, CreativeTemplate, ElegantTemplate, 
    GeometricTemplate
)
from user_manager import UserManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
LIBREOFFICE_PATH = os.getenv('LIBREOFFICE_PATH', 'libreoffice') # Default to command names

# Directories
OUTPUT_DIR = Path("generated_presentations")
TEMP_DIR = Path("temp_images")

# AI Models (OpenRouter free tier)
AI_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-27b-it:free",
    "qwen/qwen3-coder:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen-2.5-vl-7b-instruct:free",
    "xiaomi/mimo-v2-flash:free",
    "openchat/openchat-7b:free"
]

# Template Gallery Mapping
TEMPLATE_MAP = {
    'minimal': MinimalistTemplate,
    'bold': BoldModernTemplate,
    'corporate': CorporateTemplate,
    'creative': CreativeTemplate,
    'elegant': ElegantTemplate,
    'geometric': GeometricTemplate,
    'modern': ModernTemplate,
}

# Initialize services
image_service = ImageService(
    unsplash_key=UNSPLASH_ACCESS_KEY,
    pexels_key=PEXELS_API_KEY,
    pixabay_key=PIXABAY_API_KEY
)
user_manager = UserManager()

# Conversation States
LANGUAGE, NAME, PHONE, MAIN_MENU, AWAIT_TOPIC, AWAIT_SLIDE_COUNT, AWAIT_PRES_LANG, AWAIT_OTHER_LANG = range(8)

# UI Text Dictionary
TEXTS = {
    'en': {
        'welcome': "👋 Welcome! Please choose your language:",
        'ask_name': "✍️ What is your full name?",
        'ask_phone': "📱 Please share your phone number:",
        'share_contact': "📞 Share Contact",
        'menu_create': "📝 Create from Topic",
        'menu_templates': "🎨 Templates Gallery",
        'menu_history': "📜 My History",
        'menu_info': "👤 My Info",
        'menu_bot': "ℹ️ Bot Info",
        'menu_create_prompt': "💡 Send me the **topic** (keyword) for your presentation:\n\nExample: *Artificial Intelligence in Healthcare*",
        'menu_title': "🏠 Main Menu",
        'history_title': "📜 *Your Recent Presentations:*",
        'no_history': "📭 You haven't created any presentations yet.",
        'history_item': "• {topic} ({tmpl}) - {date}",
        'reg_complete': "✅ Registration complete! You can now create presentations.",
        'info_template': "👤 *User Profile*\n\nName: {name}\nPhone: {phone}\nLanguage: {lang}",
        'change_info': "🔄 Change Info",
        'ask_slide_count': "📄 How many slides would you like?",
        'invalid_slide_count': "❌ Please select a valid number (1-20).",
        'ask_pres_lang': "🌐 In which language should the presentation be?",
        'ask_other_lang': "✍️ Please type the language name:",
        'pres_lang_btn_other': "🌐 Other",
        'tmpl_minimal': "✨ Minimalist",
        'tmpl_bold': "💪 Bold Modern",
        'tmpl_corporate': "🏢 Corporate",
        'tmpl_creative': "🎨 Creative",
        'tmpl_elegant': "💎 Elegant",
        'tmpl_geometric': "⬡ Geometric",
        'tmpl_modern': "🌟 Modern",
        'tmpl_random': "🎲 Surprise Me!",
        'choose_template': "🎨 Choose a template for *{topic}*:",
        'cancel_msg': "❌ Cancelled. Returning to menu.",
        'cancel_btn': "❌ Cancel",
        'back_btn': "⬅️ Back",
        'creating_msg': "🎨 Creating *{topic}* presentation...\n📊 Slides: {count}\n🌐 Language: {lang}\n✨ Template: *{tmpl}*\n\nThis may take a minute...",
        'success_caption': "📊 Your presentation: *{topic}*\nTemplate: {tmpl}",
        'success_uploading': "✅ Presentation created! Uploading...",
        'error_gen': "❌ Sorry, error generating presentation. Try again later.",
        'btn_get_pdf': "📄 Get PDF Version",
        'converting_pdf': "⏳ Converting to PDF...",
        'whats_next': "What's next?"
    },
    'uz': {
        'welcome': "👋 Xush kelibsiz! Iltimos, tilni tanlang:",
        'ask_name': "✍️ Ismingiz nima?",
        'ask_phone': "📱 Telefon raqamingizni yuboring:",
        'share_contact': "📞 Kontaktni ulashish",
        'menu_create': "📝 Mavzu orqali yaratish",
        'menu_templates': "🎨 Shablonlar galereyasi",
        'menu_history': "📜 Tarixim",
        'menu_info': "👤 Ma'lumotlarim",
        'menu_bot': "ℹ️ Bot haqida",
        'menu_create_prompt': "💡 Taqdimot **mavzusini** yuboring:\n\nMasalan: *Sun'iy intellekt tibbiyotda*",
        'menu_title': "🏠 Asosiy menyu",
        'history_title': "📜 *Sizning oxirgi taqdimotlaringiz:*",
        'no_history': "📭 Siz hali taqdimot yaratmagansiz.",
        'history_item': "• {topic} ({tmpl}) - {date}",
        'reg_complete': "✅ Ro'yxatdan o'tish yakunlandi! Endi taqdimot yaratishingiz mumkin.",
        'info_template': "👤 *Foydalanuvchi profili*\n\nIsm: {name}\nTelefon: {phone}\nTil: {lang}",
        'change_info': "🔄 Ma'lumotni o'zgartirish",
        'ask_slide_count': "📄 Nechta slayd kerak?",
        'invalid_slide_count': "❌ Iltimos, to'g'ri raqam tanlang (1-20).",
        'ask_pres_lang': "🌐 Taqdimot qaysi tilda bo'lsin?",
        'ask_other_lang': "✍️ Iltimos, til nomini yozing:",
        'pres_lang_btn_other': "🌐 Boshqa",
        'tmpl_minimal': "✨ Minimalistik",
        'tmpl_bold': "💪 Dadil Zamonaviy",
        'tmpl_corporate': "🏢 Korporativ",
        'tmpl_creative': "🎨 Ijodiy",
        'tmpl_elegant': "💎 Elegant",
        'tmpl_geometric': "⬡ Geometrik",
        'tmpl_modern': "🌟 Zamonaviy",
        'tmpl_random': "🎲 Meni hayratda qoldiring!",
        'choose_template': "🎨 *{topic}* uchun shablon tanlang:",
        'cancel_msg': "❌ Bekor qilindi. Menyu qaytarilmoqda.",
        'cancel_btn': "❌ Bekor qilish",
        'back_btn': "⬅️ Orqaga",
        'creating_msg': "🎨 *{topic}* taqdimoti yaratilmoqda...\n📊 Slaydlar: {count}\n🌐 Til: {lang}\n✨ Shablon: *{tmpl}*\n\nBu bir daqiqa vaqt olishi mumkin...",
        'success_caption': "📊 Sizning taqdimotingiz: *{topic}*\nShablon: {tmpl}",
        'success_uploading': "✅ Taqdimot yaratildi! Yuklanmoqda...",
        'error_gen': "❌ Kechirasiz, taqdimot yaratishda xatolik. Keyinroq urinib ko'ring.",
        'btn_get_pdf': "📄 PDF variantini olish",
        'converting_pdf': "⏳ PDF-ga o'tkazilmoqda...",
        'whats_next': "Endi nima qilamiz?"
    },
    'ru': {
        'welcome': "👋 Добро пожаловать! Пожалуйста, выберите язык:",
        'ask_name': "✍️ Как вас зовут?",
        'ask_phone': "📱 Пожалуйста, поделитесь номером телефона:",
        'share_contact': "📞 Поделиться контактом",
        'menu_create': "📝 Создать по теме",
        'menu_templates': "🎨 Галерея шаблонов",
        'menu_history': "📜 Моя история",
        'menu_info': "👤 Мои данные",
        'menu_bot': "ℹ️ О боте",
        'menu_create_prompt': "💡 Отправьте **тему** для презентации:\n\nПример: *Искусственный интеллект в медицине*",
        'menu_title': "🏠 Главное меню",
        'history_title': "📜 *Ваши недавние презентации:*",
        'no_history': "📭 Вы еще не создавали презентаций.",
        'history_item': "• {topic} ({tmpl}) - {date}",
        'reg_complete': "✅ Регистрация завершена! Теперь вы можете создавать презентации.",
        'info_template': "👤 *Профиль пользователя*\n\nИмя: {name}\nТелефон: {phone}\nЯзык: {lang}",
        'change_info': "🔄 Изменить данные",
        'ask_slide_count': "📄 Сколько слайдов вы хотите?",
        'invalid_slide_count': "❌ Пожалуйста, выберите правильное число (1-20).",
        'ask_pres_lang': "🌐 На каком языке должна быть презентация?",
        'ask_other_lang': "✍️ Пожалуйста, напишите название языка:",
        'pres_lang_btn_other': "🌐 Другой",
        'tmpl_minimal': "✨ Минимализм",
        'tmpl_bold': "💪 Смелый Модерн",
        'tmpl_corporate': "🏢 Корпоративный",
        'tmpl_creative': "🎨 Креативный",
        'tmpl_elegant': "💎 Элегантный",
        'tmpl_geometric': "⬡ Геометрический",
        'tmpl_modern': "🌟 Модерн",
        'tmpl_random': "🎲 Удиви меня!",
        'choose_template': "🎨 Выберите шаблон для *{topic}*:",
        'cancel_msg': "❌ Отменено. Возврат в меню.",
        'cancel_btn': "❌ Отмена",
        'back_btn': "⬅️ Назад",
        'creating_msg': "🎨 Создание презентации *{topic}*...\n📊 Слайды: {count}\n🌐 Язык: {lang}\n✨ Шаблон: *{tmpl}*\n\nЭто может занять минуту...",
        'success_caption': "📊 Ваша презентация: *{topic}*\nШаблон: {tmpl}",
        'success_uploading': "✅ Презентация создана! Загрузка...",
        'error_gen': "❌ Извините, ошибка создания презентации. Попробуйте позже.",
        'btn_get_pdf': "📄 Получить PDF версию",
        'converting_pdf': "⏳ Конвертация в PDF...",
        'whats_next': "Что дальше?"
    }
}

class PresentationGenerator:
    """Generate presentations using AI and templates"""
    
    def __init__(self, openrouter_key):
        self.api_key = openrouter_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.semaphore = asyncio.Semaphore(3) # Limit to 3 concurrent generations
    
    async def generate_outline(self, topic, slide_count=7, language="English"):
        """Generate presentation outline using OpenRouter AI"""
        task_description = f"create a professional presentation outline about: {topic}"

        prompt = f"""Task: {task_description}
The content MUST be in {language} language.

Generate a JSON response with this structure:
{{
  "title": "Main presentation title",
  "subtitle": "Brief subtitle or tagline",
  "slides": [
    {{
      "title": "Slide title",
      "bullets": ["Point 1", "Point 2", "Point 3"],
      "image_query": "search term for relevant image"
    }}
  ]
}}

Requirements:
- Create {slide_count} content slides
- Each slide should have 3-5 concise bullet points
- Include **DISTINCT and SPECIFIC** image search queries for each slide
- Make it engaging and informative
- Return ONLY valid JSON, no markdown formatting"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/telegram-pptx-bot",
            "X-Title": "Telegram PPTX Bot"
        }
        
        for model in AI_MODELS:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            try:
                # Add timeout to prevent hanging
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(self.api_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data['choices'][0]['message']['content']
                            
                            # Clean up potential markdown formatting
                            content = content.strip()
                            if content.startswith('```json'):
                                content = content[7:]
                            if content.startswith('```'):
                                content = content[3:]
                            if content.endswith('```'):
                                content = content[:-3]
                            content = content.strip()
                            
                            # Parse JSON
                            outline = json.loads(content)
                            logger.info(f"Successfully generated outline using model: {model}")
                            return outline
                        elif response.status == 429:
                            # Rate limited, try next model
                            logger.warning(f"Model {model} is rate-limited, trying next...")
                            await asyncio.sleep(1) # Small delay
                            continue
                        else:
                            response_text = await response.text()
                            logger.error(f"OpenRouter API error with {model}: {response.status} - {response_text}")
                            continue
            except Exception as e:
                logger.error(f"Error with model {model}: {e}")
                continue
        
        # All models failed
        logger.error("All models failed or are rate-limited")
        return None
    
    async def create_presentation(self, topic, slide_count=7, language="English", template_name=None, color_scheme=None, progress_callback=None):
        """Create a complete PowerPoint presentation with progress reporting"""
        async with self.semaphore:
            # Generate outline
            outline = await self.generate_outline(topic, slide_count, language)
            if not outline:
                return None
            
            # Choose color scheme
            if not color_scheme:
                color_scheme = ColorScheme.get_random_scheme()
            
            # Select template based on name
            if template_name == 'random' or template_name is None:
                template_class = get_random_template()
            else:
                template_class = TEMPLATE_MAP.get(template_name, ModernTemplate)
            
            template = template_class(color_scheme=color_scheme)
            
            # Add title slide
            template.add_title_slide(
                title=outline.get('title', topic),
                subtitle=outline.get('subtitle', '')
            )
            
            # Add content slides
            slides_data = outline.get('slides', [])
            total_slides = len(slides_data)
            
            for i, slide_data in enumerate(slides_data):
                title = slide_data.get('title', '')
                bullets = slide_data.get('bullets', [])
                image_query = slide_data.get('image_query', '')
                
                # Fetch image if query provided
                image_path = None
                credit = None
                
                if image_query:
                    # Returns dict with path, credit, download_url
                    image_result = image_service.fetch_image(image_query)
                    
                    if image_result and isinstance(image_result, dict):
                        image_path = image_result.get('path')
                        credit = image_result.get('credit')
                        
                        # Trigger download tracking (Unsplash compliance)
                        if image_result.get('download_url'):
                            image_service.trigger_download(image_result.get('download_url'))
                    elif image_result:
                        # Fallback for string return
                        image_path = image_result
                
                # Add slide with credit
                template.add_content_slide(title, bullets, image_path=image_path, credit=credit)
            
            # Save presentation
            OUTPUT_DIR.mkdir(exist_ok=True)
            
            filename = f"{topic[:30].replace(' ', '_')}.pptx"
            pptx_path = OUTPUT_DIR / filename
            template.save(str(pptx_path))
            
            return str(pptx_path)

    async def convert_to_pdf(self, pptx_path: str):
        """Convert PPTX to PDF using LibreOffice (if available)"""
        output_dir = os.path.dirname(pptx_path)
        
        # Determine the binary to use
        lb_path = LIBREOFFICE_PATH
        
        # Common macOS location fallback if default 'libreoffice' command fails
        common_mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        
        try:
            # Check if current command exists, if not and on Mac, try common path
            import subprocess
            try:
                subprocess.run([lb_path, '--version'], capture_output=True, check=False)
            except FileNotFoundError:
                if os.path.exists(common_mac_path):
                    lb_path = common_mac_path
            
            process = await asyncio.create_subprocess_exec(
                lb_path, '--headless', '--convert-to', 'pdf', 
                '--outdir', output_dir, pptx_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                pdf_path = pptx_path.replace('.pptx', '.pdf')
                if os.path.exists(pdf_path):
                    return pdf_path
            
            logger.error(f"PDF Conversion failed: {stderr.decode()}")
            return None
        except Exception as e:
            logger.error(f"PDF Conversion error: {e}")
            return None


# Initialize generator
presentation_generator = PresentationGenerator(OPENROUTER_API_KEY)


def get_keyboard(lang):
    """Get main menu keyboard based on language"""
    texts = TEXTS.get(lang, TEXTS['en'])
    # Primary Create Row
    keyboard = [
        [KeyboardButton(texts['menu_create'])],
        [KeyboardButton(texts['menu_templates']), KeyboardButton(texts['menu_history'])],
        [KeyboardButton(texts['menu_info']), KeyboardButton(texts['menu_bot'])]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Check registration"""
    user_id = update.effective_user.id
    
    # Check if user exists
    user_data = await user_manager.get_user(user_id)
    
    if user_data:
        # User exists, show menu
        lang = user_data.get('lang', 'en')
        texts = TEXTS.get(lang, TEXTS['en'])
        
        await update.message.reply_text(
            texts['menu_title'],
            reply_markup=get_keyboard(lang)
        )
        return MAIN_MENU
    else:
        # New user, start registration
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O'zbek", callback_data='lang_uz'),
                InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
                InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
            ]
        ]
        await update.message.reply_text(
            TEXTS['en']['welcome'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LANGUAGE

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    context.user_data['lang'] = lang
    texts = TEXTS.get(lang, TEXTS['en'])
    
    await query.edit_message_text(f"Selected: {lang.upper()}")
    await query.message.reply_text(texts['ask_name'])
    
    return NAME

async def name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input"""
    name = update.message.text
    context.user_data['name'] = name
    
    lang = context.user_data.get('lang', 'en')
    texts = TEXTS.get(lang, TEXTS['en'])
    
    # Request phone
    keyboard = [[KeyboardButton(texts['share_contact'], request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(texts['ask_phone'], reply_markup=markup)
    return PHONE

async def phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone input"""
    user_id = update.effective_user.id
    
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
        
    context.user_data['phone'] = phone
    
    # Complete registration
    user_data = {
        'name': context.user_data.get('name'),
        'phone': phone,
        'lang': context.user_data.get('lang', 'en')
    }
    await user_manager.save_user(user_id, user_data)
    
    # Show main menu
    lang = user_data['lang']
    texts = TEXTS.get(lang, TEXTS['en'])
    
    await update.message.reply_text(
        texts['reg_complete'],
        reply_markup=get_keyboard(lang)
    )
    return MAIN_MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu selections"""
    text = update.message.text
    user_id = update.effective_user.id
    user = await user_manager.get_user(user_id)
    
    if not user:
        return await start(update, context)
        
    lang = user.get('lang', 'en')
    texts = TEXTS.get(lang, TEXTS['en'])
    
    if text == texts['menu_create']:
        # Start topic flow
        await update.message.reply_text(
            texts['menu_create_prompt'],
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([[texts['cancel_btn']]], resize_keyboard=True) 
        )
        return AWAIT_TOPIC
        
    elif text == texts['menu_templates']:
        # Show Templates Gallery (Album)
        previews = []
        template_keys = ['minimal', 'bold', 'corporate', 'creative', 'elegant', 'geometric', 'modern']
        for key in template_keys:
            img_path = Path(f"assets/previews/{key}.jpg")
            if img_path.exists():
                previews.append(InputMediaPhoto(open(img_path, 'rb'), caption=texts.get(f'tmpl_{key}', key.title())))
        
        if previews:
            await update.message.reply_text("🖼️ *Template Gallery:*", parse_mode='Markdown')
            await update.message.reply_media_group(previews)
        else:
            await update.message.reply_text("🎨 *Available Styles:* " + ", ".join([k.title() for k in template_keys]))
            
        return MAIN_MENU
        
    elif text == texts['menu_info']:
        # Show profile
        profile = texts['info_template'].format(
            name=user.get('name'),
            phone=user.get('phone'),
            lang=user.get('lang').upper()
        )
        keyboard = [[InlineKeyboardButton(texts['change_info'], callback_data='change_info')]]
        await update.message.reply_text(
            profile,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return MAIN_MENU
        
    elif text == texts['menu_history']:
        # Show recent history from PostgreSQL
        history = await user_manager.get_history(user_id)
        if not history:
            await update.message.reply_text(texts['no_history'], parse_mode='Markdown')
        else:
            msg = texts['history_title'] + "\n\n"
            for row in history:
                date_str = row['created_at'].strftime("%Y-%m-%d %H:%M")
                msg += texts['history_item'].format(
                    topic=row['topic'],
                    tmpl=row['template'].title(),
                    date=date_str
                ) + "\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
        return MAIN_MENU

    elif text == texts['menu_bot']:
        # Show bot info
        await update.message.reply_text(
            "🤖 *Telegram PPTX Bot*\n\nVersion: 1.1.0\nPowered by OpenRouter AI & python-pptx\n🗄️ Database: PostgreSQL",
            parse_mode='Markdown'
        )
        return MAIN_MENU

    return MAIN_MENU

async def topic_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle receiving the topic"""
    topic = update.message.text
    user = await user_manager.get_user(update.effective_user.id)
    lang = user.get('lang', 'en')
    texts = TEXTS.get(lang, TEXTS['en'])

    context.user_data['topic'] = topic
    
    # Ask for slide count
    keyboard = [['5', '8', '10'], ['12', '15', '20'], [texts['back_btn']]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        texts['ask_slide_count'],
        reply_markup=reply_markup
    )
    return AWAIT_SLIDE_COUNT


async def slide_count_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle slide count input"""
    text = update.message.text
    user = await user_manager.get_user(update.effective_user.id)
    lang = user.get('lang', 'en')
    texts = TEXTS.get(lang, TEXTS['en'])
    
    if text == texts['back_btn']:
        await update.message.reply_text(
             texts['menu_create_prompt'],
             parse_mode='Markdown',
             reply_markup=ReplyKeyboardMarkup([[texts['cancel_btn']]], resize_keyboard=True) 
        )
        return AWAIT_TOPIC
    
    try:
        count = int(text)
        if not (1 <= count <= 20):
            raise ValueError()
        context.user_data['slide_count'] = count
    except ValueError:
        await update.message.reply_text(texts['invalid_slide_count'])
        return AWAIT_SLIDE_COUNT
        
    # Ask for Presentation Language
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data='plang_Uzbek'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='plang_Russian')
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='plang_English'),
            InlineKeyboardButton(texts['pres_lang_btn_other'], callback_data='plang_other')
        ],
        [
            InlineKeyboardButton(texts['back_btn'], callback_data='back_to_slide_count')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        texts['ask_pres_lang'],
        reply_markup=reply_markup
    )
    return AWAIT_PRES_LANG

async def pres_lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle presentation language selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = await user_manager.get_user(update.effective_user.id)
    lang = user.get('lang', 'en')
    texts = TEXTS.get(lang, TEXTS['en'])
    
    if data == 'back_to_slide_count':
        # Go back to slide count
        keyboard = [['5', '8', '10'], ['12', '15', '20'], [texts['back_btn']]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await query.message.delete()
        await query.message.reply_text(
            texts['ask_slide_count'],
            reply_markup=reply_markup
        )
        return AWAIT_SLIDE_COUNT

    if data == 'plang_other':
        await query.edit_message_text(texts['ask_other_lang'], reply_markup=ReplyKeyboardMarkup([[texts['back_btn']]], resize_keyboard=True))
        return AWAIT_OTHER_LANG
        
    pres_lang = data.split('_')[1]
    context.user_data['pres_lang'] = pres_lang
    
    # Show template selection
    return await show_template_selection(query, context, texts)

async def other_lang_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom language input"""
    text = update.message.text
    user = await user_manager.get_user(update.effective_user.id)
    lang = user.get('lang', 'en') if user else 'en'
    texts = TEXTS.get(lang, TEXTS['en'])
    
    if text == texts['back_btn']:
        # Go back to Presentation Language selection
        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O'zbek", callback_data='plang_Uzbek'),
                InlineKeyboardButton("🇷🇺 Русский", callback_data='plang_Russian')
            ],
            [
                InlineKeyboardButton("🇬🇧 English", callback_data='plang_English'),
                InlineKeyboardButton(texts['pres_lang_btn_other'], callback_data='plang_other')
            ],
            [
                InlineKeyboardButton(texts['back_btn'], callback_data='back_to_slide_count')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            texts['ask_pres_lang'],
            reply_markup=reply_markup
        )
        return AWAIT_PRES_LANG
    
    context.user_data['pres_lang'] = text
    # Show template selection
    return await show_template_selection(update, context, texts)

async def show_template_selection(update_obj, context, texts):
    """Helper to show template selection buttons"""
    # Robustly get user_id from either Update or CallbackContext
    if hasattr(update_obj, 'effective_user') and update_obj.effective_user:
        user_id = update_obj.effective_user.id
    elif hasattr(update_obj, 'from_user') and update_obj.from_user:
        user_id = update_obj.from_user.id
    else:
        user_id = context._user_id # Fallback
        
    user = await user_manager.get_user(user_id)
    lang = user.get('lang', 'en') if user else 'en'
    topic = context.user_data.get('topic', 'Presentation')
    
    keyboard = [
        [
            InlineKeyboardButton(texts['tmpl_minimal'], callback_data='template_minimal'),
            InlineKeyboardButton(texts['tmpl_bold'], callback_data='template_bold')
        ],
        [
            InlineKeyboardButton(texts['tmpl_corporate'], callback_data='template_corporate'),
            InlineKeyboardButton(texts['tmpl_creative'], callback_data='template_creative')
        ],
        [
            InlineKeyboardButton(texts['tmpl_elegant'], callback_data='template_elegant'),
            InlineKeyboardButton(texts['tmpl_geometric'], callback_data='template_geometric')
        ],
        [
            InlineKeyboardButton(texts['tmpl_modern'], callback_data='template_modern')
        ],
        [
            InlineKeyboardButton(texts['tmpl_random'], callback_data='template_random')
        ],
        [
            InlineKeyboardButton(texts['back_btn'], callback_data='back_to_pres_lang')
        ]
    ]
    
    # Template previews are now in the Main Menu
    # To avoid spamming on 'Back' navigation, we only show buttons here
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = texts['choose_template'].format(topic=topic)
    
    if isinstance(update_obj, Update):
        await update_obj.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else: # CallbackQuery
        await update_obj.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        
    return AWAIT_TOPIC # Still use AWAIT_TOPIC for template callback

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel command"""
    user_id = update.effective_user.id
    user = await user_manager.get_user(user_id)
    lang = user.get('lang', 'en') if user else 'en'
    texts = TEXTS.get(lang, TEXTS['en'])
    
    # Handle both Message and CallbackQuery
    if update.message:
        await update.message.reply_text(
            texts['cancel_msg'],
            reply_markup=get_keyboard(lang)
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(texts['cancel_msg'])
        await update.callback_query.message.reply_text(
            texts['menu_title'],
            reply_markup=get_keyboard(lang)
        )
    return MAIN_MENU

async def template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle template selection from inline buttons"""
    query = update.callback_query
    await query.answer()
    
    # Get template choice
    # Get template choice
    data = query.data
    
    if data == 'back_to_pres_lang':
        # Go back to language selection
        # Get texts again as we might be in a different context
        user_id = query.from_user.id
        user = await user_manager.get_user(user_id)
        lang = user.get('lang', 'en') if user else 'en'
        texts = TEXTS.get(lang, TEXTS['en'])

        keyboard = [
            [
                InlineKeyboardButton("🇺🇿 O'zbek", callback_data='plang_Uzbek'),
                InlineKeyboardButton("🇷🇺 Русский", callback_data='plang_Russian')
            ],
            [
                InlineKeyboardButton("🇬🇧 English", callback_data='plang_English'),
                InlineKeyboardButton(texts['pres_lang_btn_other'], callback_data='plang_other')
            ],
            [
                InlineKeyboardButton(texts['back_btn'], callback_data='back_to_slide_count')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            texts['ask_pres_lang'],
            reply_markup=reply_markup
        )
        return AWAIT_PRES_LANG

    template_name = data.replace('template_', '')
    topic = context.user_data.get('topic', 'Presentation')
    slide_count = context.user_data.get('slide_count', 7)
    language = context.user_data.get('pres_lang', 'English')
    
    # Update message to show generating status
    user_id = query.from_user.id
    user = await user_manager.get_user(user_id)
    lang = user.get('lang', 'en') if user else 'en'
    texts = TEXTS.get(lang, TEXTS['en'])

    await query.edit_message_text(
        texts['creating_msg'].format(
            topic=topic,
            count=slide_count,
            lang=language,
            tmpl=template_name.title()
        ),
        parse_mode='Markdown'
    )
    
    async def update_progress(text):
        try:
            await query.edit_message_text(text, parse_mode='Markdown')
        except Exception:
            pass # Ignore if message is identical or deleted
            
    try:
        # Generate presentation with live progress updates
        filepath = await presentation_generator.create_presentation(
            topic,
            slide_count=slide_count,
            language=language,
            template_name=template_name,
            progress_callback=update_progress
        )
        
        if filepath:
            await query.edit_message_text(texts['success_uploading'])
            
            with open(filepath, 'rb') as pptx_file:
                await query.message.reply_document(
                    document=pptx_file,
                    filename=f"{topic}.pptx",
                    caption=texts['success_caption'].format(
                        topic=topic,
                        tmpl=template_name.title()
                    ),
                    parse_mode='Markdown'
                )
            
            # Store path for possible PDF conversion
            context.user_data['last_pptx'] = filepath
            
            # Record in PostgreSQL
            await user_manager.save_presentation(
                user_id=user_id,
                topic=topic,
                template=template_name,
                slide_count=slide_count,
                language=language
            )

            # Offer PDF version
            pdf_keyboard = [[InlineKeyboardButton(texts['btn_get_pdf'], callback_data=f"get_pdf")]]
            await query.message.reply_text(
                texts['whats_next'], 
                reply_markup=InlineKeyboardMarkup(pdf_keyboard)
            )
            
            # Send main menu again (replacing whats_next text)
            await query.message.reply_text("🏠", reply_markup=get_keyboard(lang))
            
            return MAIN_MENU
        else:
            await query.edit_message_text(texts['error_gen'])
            return MAIN_MENU
            
    except Exception as e:
        logger.error(f"Error in template_callback: {e}")
        await query.edit_message_text(f"❌ An error occurred: {str(e)}")
        return MAIN_MENU

async def pdf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF conversion request"""
    query = update.callback_query
    await query.answer()
    
    user = await user_manager.get_user(query.from_user.id)
    lang = user.get('lang', 'en') if user else 'en'
    texts = TEXTS.get(lang, TEXTS['en'])
    
    pptx_path = context.user_data.get('last_pptx')
    if not pptx_path or not os.path.exists(pptx_path):
        await query.edit_message_text("❌ PPTX file not found. Please generate a new one.")
        return
    
    await query.edit_message_text(texts['converting_pdf'])
    
    pdf_path = await presentation_generator.convert_to_pdf(pptx_path)
    
    if pdf_path:
        # Success
        with open(pdf_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=os.path.basename(pdf_path),
                caption="✅ Here is your PDF version!"
            )
        await query.delete_message()
        # Clean up both files
        try:
            os.remove(pptx_path)
            os.remove(pdf_path)
        except: pass
    else:
        await query.edit_message_text(
            "❌ *PDF conversion failed.*\n\nLibreOffice is required but not found on the server. Please ask the administrator to install it.",
            parse_mode='Markdown'
        )

async def change_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change info request"""
    query = update.callback_query
    await query.answer()
    
    # Restart registration
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data='lang_uz'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')
        ]
    ]
    await query.edit_message_text(
        TEXTS['en']['welcome'],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LANGUAGE

async def post_init(application: Application):
    """Initialize database connection"""
    await user_manager.init()

def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # Define localized cancel strings for filters
    cancel_filter = filters.Regex('^(❌ Cancel|❌ Bekor qilish|❌ Отмена)$') | filters.COMMAND
    
    # Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language_callback, pattern='^lang_')],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~cancel_filter, name_input)],
            PHONE: [MessageHandler((filters.CONTACT | filters.TEXT) & ~filters.COMMAND & ~cancel_filter, phone_input)],
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler),
                CallbackQueryHandler(change_info_callback, pattern='^change_info$')
            ],
            AWAIT_TOPIC: [
                CommandHandler("cancel", cancel),
                MessageHandler(cancel_filter, cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, topic_input),
            ],
            AWAIT_SLIDE_COUNT: [
                MessageHandler(cancel_filter, cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, slide_count_input)
            ],
            AWAIT_PRES_LANG: [
                CallbackQueryHandler(cancel, pattern='^cancel$'),
                CallbackQueryHandler(pres_lang_callback, pattern='^plang_'),
                CallbackQueryHandler(pres_lang_callback, pattern='^back_to_slide_count$')
            ],
            AWAIT_OTHER_LANG: [
                MessageHandler(cancel_filter, cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, other_lang_input)
            ]
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("cancel", cancel),
            MessageHandler(cancel_filter, cancel),
            CallbackQueryHandler(template_callback, pattern='^(template_|back_to_pres_lang$)'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(pdf_callback, pattern='^get_pdf$')
        ]
    )
    
    application.add_handler(conv_handler)
    
    logger.info("Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
