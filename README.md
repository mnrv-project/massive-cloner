# TG-Cloner

### Knowledge should not be a privilege, but a right.

This is a modified fork of **TG-Cloner CLI**, a powerful tool for the liberation and preservation of information. In a world where access to knowledge is often restricted by paywalls and artificial barriers, this script serves as a key to break those chains. It allows you to create an exact copy of any Telegram channel, ensuring that valuable content remains accessible to you, forever.

The modifications made by me krov.sh have transformed this script into a robust and intelligent tool, designed to make the digital archiving process as simple and efficient as possible.

### 🔥 Features

* **Perfect Cloning:** Copies all messages, media, documents, and files from one channel to another, maintaining the original structure.

* **Fault-Tolerant:** If your connection drops or the script is interrupted, you can simply run it again to continue exactly where you left off.

* **Smart Management:** Keeps a record of already cloned channels and doesn't offer them again, saving you time.

* **Interactive Menu:** Start new clones, continue pending ones, or bulk-leave original channels that have been cloned with a simple and direct menu.

* **Automatic Cleanup:** Offers the option to leave the original channels after completion, keeping your chat list organized.

* **Full Compatibility:** Analyzes progress files from older versions of the script and integrates them into the new system.

### 🚀 How to Use

Follow these steps to start liberating knowledge.

#### Prerequisites

* Python 3.x

* A Telegram Account

#### Step 1: Get the Script

Clone this repository to your local machine.

   ´´´pip install -r requirements.txt´´

#### Step 3: Configuration (The Magic Trick)

You need to provide your Telegram API credentials. Don't worry, they stay on your computer.

1. **Create the `.env` file:** In the same folder as the script, create a file named `.env`.

2. **Get `API_ID` and `API_HASH`:**

   * Go to [my.telegram.org](https://my.telegram.org) and log in.

   * Navigate to "API development tools" and fill out the form.

   * You will receive your `api_id` and `api_hash`.

3. **Fill the `.env` file:** Open the `.env` file and add the keys as follows:
   ´´´
   API_ID=1234567
   API_HASH=a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
   SESSION_STRING=generated_automatic
   TG_LANG=EN # Use EN for English or PT for Portuguese
   ´´´

#### Step 4: Run the Liberator!

With everything set up, just run the script.

´´´
python3 main.py
´´´

The first time, it will list all your channels and ask which ones you want to ignore. After that, the magic happens. The next times you run it, it will present an interactive menu for you to decide what to do.

### 🤝 Contributing

The fight for free information is a collective effort. If you find a bug, have an idea to improve the tool, or want to add a new feature, your help is welcome.

* **Report Issues:** Found a problem? Open an issue detailing what happened.

* **Pull Requests:** Have an improvement? Fork the repository, make your changes, and submit a **Pull Request**. All contributions will be reviewed. Together, we make the tool more powerful.

### ⚠️ Disclaimer

This tool is provided for **personal backup and information preservation** purposes. How you use it is your sole responsibility. Remember that knowledge shouldn't have owners, but the law doesn't always agree. Use it wisely.