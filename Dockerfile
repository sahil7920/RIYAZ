# Flutter के लिए बेस इमेज
FROM cirrusci/flutter:latest

# वर्कस्पेस सेट करो
WORKDIR /app

# प्रोजेक्ट की सभी फाइलें कॉपी करो
COPY . .

# सभी फाइल्स एक्सीक्यूटेबल बनाओ (अगर ज़रूरी हो)
RUN chmod +x *

# Flutter dependencies इंस्टॉल करो
RUN flutter pub get

# Python और ज़रूरी डिपेंडेंसी इंस्टॉल करो
RUN apt-get update && apt-get install -y python3 python3-pip

# Python dependencies इंस्टॉल करो
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# अतिरिक्त Python लाइब्रेरी इंस्टॉल करो
RUN pip3 install --no-cache-dir telebot flask aiogram pyTelegramBotAPI python-telegram-bot

# Flutter APK और Python स्क्रिप्ट को एक साथ रन करो
CMD ["bash", "-c", "flutter build apk & python3 m.py"]
