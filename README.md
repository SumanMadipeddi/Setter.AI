# Setter.AI - AI-Powered Lead Calling System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

> **Professional AI Voice Agent for Automated Lead Qualification and Meeting Scheduling**

Setter.AI is an intelligent calling system that automatically contacts business leads, qualifies them through natural conversations, and schedules meetings with your sales team. Powered by OpenAI's GPT-4 and Twilio's voice infrastructure.

## 🚀 Features

- **🤖 AI Voice Agent**: Professional female voice (Maayaa) for natural conversations
- **📞 Automated Calling**: Intelligent lead qualification through phone calls
- **🎯 Lead Management**: Integration with GoHighLevel (GHL) CRM
- **📅 Meeting Scheduling**: Automatic calendar coordination
- **📊 Analytics Dashboard**: Real-time call monitoring and reporting
- **🔒 Secure**: Environment-based configuration with API key protection

## 🏗️ Architecture

```
Setter.AI
├── 🤖 AI Logic (OpenAI GPT-4)
├── 📞 Voice System (Twilio)
├── 📊 CRM Integration (GoHighLevel)
├── 🌐 Web Dashboard (Flask)
└── 🗄️ Data Storage (SQLite)
```

## 📋 Prerequisites

- **Python 3.8+**
- **GoHighLevel API Key** & Location ID
- **OpenAI API Key** (GPT-4 access)
- **Twilio Account** (Account SID, Auth Token, Phone Number)

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd setter.ai-v1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required Environment Variables:**
```env
# GHL (GoHighLevel) Configuration
GHL_API_KEY=your_ghl_api_key_here
GHL_LOCATION_ID=your_location_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Webhook Configuration
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

## 🚀 Quick Start

### Run the Application
```bash
# Start the main application
python src/main.py
```

### Access Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

## 🧪 Testing

### Test Configuration
```bash
# Verify all API keys are loaded
python -c "
import sys; sys.path.append('src')
from setter_ai.utils.config import load_config
config = load_config()
print('✅ Configuration loaded successfully!')
"
```

### Test Individual Components
```bash
# Test GHL Integration
cd tests && python test_ghl_leads.py

# Test Twilio Calling
cd tests && python test_twilio_call.py

# Test Voice Conversation
cd tests && python test_voice_conversation.py
```

### Test Dashboard
```bash
# Test web interface
cd tests && python test_dashboard.py
```

## 📁 Project Structure

```
setter.ai-v1/
├── src/                    # Source code
│   ├── setter_ai/         # Main application package
│   │   ├── core/          # AI logic and business rules
│   │   ├── integrations/  # External service integrations
│   │   ├── utils/         # Utilities and helpers
│   │   └── web/           # Web interface and API
│   └── main.py            # Application entry point
├── tests/                  # Test suite
├── data/                   # Database and data files
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
All configuration is managed through environment variables. The system automatically loads from `.env` files and validates required API keys at startup.

### Customization
Modify the `.env` file to customize:
- **Business Hours**: `BUSINESS_HOURS_START`, `BUSINESS_HOURS_END`
- **Voice Settings**: `VOICE_TYPE`, `SPEECH_RATE`, `VOICE_PITCH`
- **AI Behavior**: `AI_MODEL`, `AI_TEMPERATURE`, `AI_MAX_TOKENS`
- **Call Settings**: `MAX_CALL_DURATION`, `RETRY_ATTEMPTS`

## 📊 Usage

### 1. **Lead Import**
- Leads are automatically imported from GoHighLevel
- System checks for new leads every 10 minutes
- Only leads within 24 hours are processed

### 2. **Automated Calling**
- AI agent calls leads during business hours
- Natural conversation flow for qualification
- Automatic meeting scheduling for interested prospects

### 3. **Dashboard Monitoring**
- Real-time call status and analytics
- Lead qualification results
- Meeting scheduling confirmations

## 🔒 Security

- **API Keys**: Stored in `.env` files (never committed to git)
- **Environment Isolation**: Separate configs for development/production
- **Input Validation**: All external inputs are sanitized
- **HTTPS**: Webhook endpoints require secure connections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **Apache License, Version 2.0** - see the [LICENSE](LICENSE) file for details.

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with additional CRMs
- [ ] Machine learning optimization
- [ ] Mobile application
- [ ] API rate limiting and optimization
---

**Built with ❤️ for modern sales teams**
