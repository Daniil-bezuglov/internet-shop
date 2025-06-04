import os
import socket

def get_local_ip():
    """Получает локальный IP-адрес компьютера"""
    try:
        # Создаем временное соединение для определения IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000
    
    print(f"\n{'='*50}")
    print(f"Запуск сервера в локальной сети")
    print(f"{'='*50}")
    print(f"\nЛокальный IP-адрес: {local_ip}")
    print(f"Порт: {port}")
    print(f"\nСайт будет доступен по адресам:")
    print(f"- http://{local_ip}:{port}")
    print(f"- http://localhost:{port}")
    print(f"\nДля доступа с других устройств в локальной сети используйте первый адрес")
    print(f"{'='*50}\n")
    
    # Запускаем сервер Django
    os.system(f"python manage.py runserver 0.0.0.0:{port}") 