import pika
import numpy as np
import json
from sklearn.datasets import load_diabetes
import time
from datetime import datetime

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Загружаем датасет о диабете
        X, y = load_diabetes(return_X_y=True)

        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0] - 1)

        # Создаём подключение по адресу rabbitmq:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')

        # Генерируем уникальный идентификатор
        message_id = datetime.timestamp(datetime.now())

        # Публикуем сообщение в очередь y_true с идентификатором
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps({
                                  'id': message_id,
                                  'body': y[random_row]
                              }))
        print(f'Сообщение с правильным ответом отправлено в очередь (ID: {message_id})')

        # Публикуем сообщение в очередь features с идентификатором
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps({
                                  'id': message_id,
                                  'body': list(X[random_row])
                              }))
        print(f'Сообщение с вектором признаков отправлено в очередь (ID: {message_id})')

        # Закрываем подключение
        connection.close()

        # Добавляем задержку на 10 секунд между итерациями
        time.sleep(10)
    except:
        print('Не удалось подключиться к очереди')
