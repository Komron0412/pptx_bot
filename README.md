# 📊 AI Telegram PowerPoint Bot

A powerful and intuitive Telegram bot that generates professional PowerPoint presentations (`.pptx`) from a simple topic or keyword. Powered by OpenRouter AI (LLMs) and `python-pptx`.

## ✨ Key Features

- **🚀 AI-Powered Content**: Automatically generates structured outlines, bullet points, and speaker notes based on any topic.
- **🖼️ Smart Image Integration**: 10-stage fallback system ensures every slide has a relevant, high-quality image.
  - *Sources*: Unsplash, Pexels, Pixabay, Wikimedia, Pollinations AI, and local high-quality placeholders.
- **🎨 7+ Professional Templates Gallery**: Choose from Minimalist, Bold Modern, Corporate, Creative, Elegant, Geometric, and Modern styles.
- **📄 PDF Export**: Convert your generated presentations to PDF format with a single click.
- **📜 Generation History**: Access your recent presentations and download them again at any time.
- **🗄️ Robust Persistence**: PostgreSQL integration for reliable user data and history management.
- **🌐 Multi-Language Support**: English, Uzbek, and Russian interface and presentation generation.

## 🛠️ Prerequisites

- **Python 3.9+**
- **LibreOffice** (Required for PDF conversion)
  - *macOS*: `brew install --cask libreoffice`
  - *Ubuntu/Debian*: `sudo apt install libreoffice`
- **PostgreSQL** (Optional, falls back to local JSON if not available)
- **OpenRouter API Key** (Required for AI generation)
- **Optional API Keys**: Unsplash, Pexels, Pixabay (for better image results)

## 🚀 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/telegram-pptx-bot.git
   cd telegram-pptx-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## ⚙️ Configuration (.env)

| Variable | Description | Requirement |
|----------|-------------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot API token | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key for AI generation | Required |
| `DATABASE_URL` | PostgreSQL connection string | Optional (Falls back to JSON) |
| `LIBREOFFICE_PATH` | Path to LibreOffice binary (`soffice`) | Optional (For PDF) |
| `UNSPLASH_ACCESS_KEY` | Unsplash API Access Key | Optional |
| `PEXELS_API_KEY` | Pexels API Key | Optional |
| `PIXABAY_API_KEY` | Pixabay API Key | Optional |

## 🐳 Deployment with Docker (Recommended)

The easiest way to deploy the bot is using Docker, as it bundles all dependencies (LibreOffice, PostgreSQL, Fonts).

1. **Install Docker & Docker Compose** on your server.
2. **Configure your `.env`**:
   ```bash
   cp .env.example .env
   # Set your TELEGRAM_BOT_TOKEN and OPENROUTER_API_KEY
   # Set DATABASE_URL=postgresql://postgres:postgres@db:5432/pptx_bot
   ```
3. **Deploy**:
   ```bash
   docker-compose up -d --build
   ```

The bot will automatically restart if the system reboots. Use `docker-compose logs -f bot` to check the logs.

## 📁 Project Structure

- `bot.py`: Main bot logic and Presentation Generator.
- `user_manager.py`: Database and user session management.
- `image_service.py`: Multi-source image fetching and caching.
- `templates/`: Modular PPTX templates with different styles.
- `assets/placeholders/`: Local fallback images for offline/service failures.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
