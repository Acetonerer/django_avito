import os
import subprocess
import shutil

# Настройки
DOMAIN = "widgets-tema.ru"
CERT_DIR = f"/etc/letsencrypt/live/{DOMAIN}"
PROJECT_CERT_DIR = "/django_avito/certs"  # Укажите путь к папке с сертификатами в проекте


# Функция для обновления сертификатов
def update_certificates():
    try:
        # Обновление сертификатов с помощью Certbot
        subprocess.run(["sudo", "certbot", "certonly", "--standalone", "-d", DOMAIN], check=True)

        # Копирование обновленных сертификатов в директорию проекта
        shutil.copy(os.path.join(CERT_DIR, "fullchain.pem"), os.path.join(PROJECT_CERT_DIR, "fullchain.pem"))
        shutil.copy(os.path.join(CERT_DIR, "privkey.pem"), os.path.join(PROJECT_CERT_DIR, "privkey.pem"))

        print("Certificates updated and copied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during certificate update: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    update_certificates()