# 🎨 Telegram PowerPoint Generator Bot

A Telegram bot that creates beautiful PowerPoint presentations using AI. Simply provide a topic, and the bot will generate a professionally designed presentation with relevant images.

## ✨ Features

- **AI-Powered Content**: Uses OpenRouter API (Meta Llama 3.1) to generate presentation outlines
- **Beautiful Designs**: Modern templates with gradient backgrounds, custom color schemes, and professional typography
- **Automatic Images**: Fetches relevant images from Unsplash (with fallback to Picsum)
- **Easy to Use**: Just send `/create [topic]` and get your presentation

## 🚀 Quick Start

### 1. Clone and Install

```bash
cd telegram-pptx-bot
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENROUTER_API_KEY=your_openrouter_api_key

# Optional (for better images)
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
```

#### Getting API Keys

1. **Telegram Bot Token**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the prompts
   - Copy the token provided

2. **OpenRouter API Key**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Go to Keys section
   - Create a new API key

3. **Unsplash Access Key** (Optional)
   - Sign up at [Unsplash Developers](https://unsplash.com/developers)
   - Create a new application
   - Copy your Access Key

### 3. Run the Bot

```bash
python bot.py
```

You should see:
```
Bot started! Press Ctrl+C to stop.
```

## 📱 Usage

1. **Start the bot**
   ```
   /start
   ```

2. **Create a presentation**
   ```
   /create Climate Change Solutions
   ```
   or
   ```
   /create Introduction to Machine Learning
   ```

3. **Wait for your presentation**
   - The bot will generate content using AI (takes ~30-60 seconds)
   - You'll receive a `.pptx` file
   - Download and open in PowerPoint, Google Slides, or any compatible software

## 🎨 Available Color Schemes

The bot randomly selects from 5 modern color schemes:

- **Vibrant**: Purple and pink gradients
- **Professional**: Blue and orange business theme
- **Nature**: Green and yellow earth tones
- **Tech**: Blue and purple tech theme
- **Sunset**: Red and orange warm colors

## 📁 Project Structure

```
telegram-pptx-bot/
├── bot.py                  # Main bot application
├── image_service.py        # Image fetching from Unsplash/Picsum
├── templates/
│   ├── modern_template.py  # PowerPoint template generator
│   └── styles.py           # Color schemes and typography
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Technical Details

- **Framework**: python-telegram-bot 20.7
- **AI Model**: Meta Llama 3.1 8B (via OpenRouter)
- **Presentation**: python-pptx 0.6.23
- **Images**: Unsplash API + Picsum fallback
- **Async**: aiohttp for non-blocking API calls

## 🐛 Troubleshooting

### Bot doesn't respond
- Check your `TELEGRAM_BOT_TOKEN` is correct
- Ensure the bot is running (`python bot.py`)

### Presentations have no content
- Verify your `OPENROUTER_API_KEY` is valid
- Check the console for error messages

### No images in slides
- Add `UNSPLASH_ACCESS_KEY` to `.env` for better images
- The bot will use fallback images if Unsplash is not configured

### "Module not found" error
```bash
pip install -r requirements.txt
```

## 📝 Example Output

When you run `/create Digital Marketing Strategy`, the bot generates:
- Title slide with gradient background
- 5-7 content slides with:
  - Professional bullet points
  - Relevant images
  - Consistent color scheme and typography

## 🤝 Contributing

Feel free to fork and improve! Some ideas:
- Add more color schemes
- Support for different slide layouts
- Custom templates
- Multi-language support

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Credits

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [python-pptx](https://github.com/scanny/python-pptx)
- [OpenRouter](https://openrouter.ai/)
- [Unsplash](https://unsplash.com/)

---

Made with ❤️ using AI and Python
