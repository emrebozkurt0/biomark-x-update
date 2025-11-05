# Logger module for the server
import logging
import os
from datetime import datetime

# 1. Önce log dosyasının adını belirleyin
LOG_FILE_NAME = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# 2. Logların saklanacağı DİZİNİ (klasörü) belirleyin
LOGS_DIR = os.path.join(os.getcwd(), "logs")

# 3. O DİZİNİ oluşturun
os.makedirs(LOGS_DIR, exist_ok=True)

# 4. Log dosyasının tam YOLUNU belirleyin (Dizin + Dosya Adı)
LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE_NAME)

# 5. Logging'i bu YOL ile yapılandırın
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)