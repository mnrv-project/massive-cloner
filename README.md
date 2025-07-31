# TG Cloner

A modern web application for cloning Telegram channels with an intuitive interface and real-time progress tracking.

## Features

- **User-friendly Interface**: Clean, modern dark-mode design
- **Telegram Authentication**: Secure login with phone number and 2FA support
- **Channel Selection**: Browse and select from your available channels
- **Smart Cloning**: Clone to new channels or existing ones
- **Real-time Progress**: Live status updates during cloning process
- **Media Support**: Preserves text formatting, images, videos, and documents
- **Rate Limiting**: Built-in delays to avoid Telegram restrictions
- **Error Handling**: Robust error management with user feedback

## Prerequisites

- Python 3. or higher
- Telegram API credentials (API ID and API Hash)
- A Telegram account

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DevHuney/tg-cloner
   cd tg-cloner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   SESSION_STRING=  # Will be generated during first login
   ```

   To get your API credentials:
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API Development Tools"
   - Create a new application to get API_ID and API_HASH

## Usage

1. **Start the application**
   ```bash
   uvicorn main:app
   ```

2. **Open your browser**
   
   Navigate to `http://localhost:8000`

3. **First-time setup**
   - Enter your phone number in international format (+1234567890)
   - Enter the verification code sent to your Telegram
   - If you have 2FA enabled, enter your password

4. **Clone channels**
   - Select a source channel from your list
   - Choose to create a new channel or select an existing destination
   - Click "Start Cloning" and monitor the real-time progress

## How It Works

1. **Authentication**: Uses Telethon library to authenticate with Telegram
2. **Channel Discovery**: Fetches all channels you're a member of
3. **Message Processing**: Iterates through messages in batches of 10
4. **Content Preservation**: Maintains original formatting, media, and structure
5. **Progress Tracking**: Updates status in real-time via JSON file
6. **Rate Limiting**: Random delays (1-5 seconds) between messages to avoid restrictions

## Security Features

- Session strings are stored locally in `.env`
- No passwords or sensitive data stored in plain text
- Automatic session management and cleanup
- Error handling prevents data leaks

## Technical Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Telegram API**: Telethon library
- **Styling**: Custom CSS with modern dark theme
- **Real-time Updates**: Polling-based status checking

## File Structure

```
tg-cloner/
├── main.py              # FastAPI application and core logic
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (create this)
├── .gitignore          # Git ignore rules
├── templates/          # HTML templates
│   ├── signup.html     # Authentication page
│   ├── home.html       # Channel selection and cloning setup
│   └── cloning.html    # Real-time progress page
└── README.md           # This file
```

## API Endpoints

- `GET /` - Root redirect to appropriate page
- `GET /home` - Main application page
- `GET /signup` - Authentication page
- `GET /cloning` - Progress monitoring page
- `POST /api/signup/tglogin/number` - Send verification code
- `POST /api/signup/tglogin/code` - Verify code
- `POST /api/signup/tglogin/pwd` - Two-factor authentication
- `GET /api/tginfo` - Get user channels and cloning status
- `POST /api/start` - Start cloning process
- `GET /api/cloning_status` - Get real-time cloning progress

## Troubleshooting

**Common Issues:**

- **"User not authorized"**: Re-authenticate through `/signup`
- **Rate limiting errors**: The app handles these automatically with delays
- **Session expired**: Delete the `SESSION_STRING` from `.env` and re-login
- **No channels showing**: Ensure you're a member of at least one channel

**Development Mode:**
```bash
uvicorn main:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect Telegram's Terms of Service and use responsibly.

## Disclaimer

This tool is designed for legitimate use cases such as backing up your own channels or migrating content you own. Always ensure you have proper permissions before cloning any channel content.