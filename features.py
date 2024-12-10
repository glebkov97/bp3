import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

# Создаем бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0] - 1)

        # Получаем текущую дату и время для генерации уникального идентификатора
        current_time = datetime.now()
        message_id = int(current_time.timestamp())

        # Создаем подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаем очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаем очередь features
        channel.queue_declare(queue='features')

        # Генерируем сообщение для очереди y_true
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }

        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true))
        print(f'Сообщение с правильным ответом (ID: {message_id}) отправлено в очередь y_true')

        # Генерируем сообщение для очереди features
        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }

        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features))
        print(f'Сообщение с вектором признаков (ID: {message_id}) отправлено в очередь features')

        # Закрываем подключение
        connection.close()

        # Добавляем задержку в 10 секунд между итерациями
        time.sleep(10)

    except Exception as e:
        print(f'Не удалось подключиться к очереди или произошла ошибка: {str(e)}')
