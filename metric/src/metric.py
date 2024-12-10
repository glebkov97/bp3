import pika
import json
import pandas as pd
import csv

# Инициализируем DataFrame для хранения сообщений
df = pd.DataFrame(columns=['id', 'y_true', 'y_pred'])

try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Объявляем очереди y_true и y_pred
    channel.queue_declare(queue='y_true')
    channel.queue_declare(queue='y_pred')

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        message = json.loads(body)
        message_id = message['id']
        value = message['body']  # Изменено с 'value' на 'body'

        if method.routing_key == 'y_true':
            df.loc[message_id, 'y_true'] = value
        elif method.routing_key == 'y_pred':
            df.loc[message_id, 'y_pred'] = value

        # Если есть и y_true, и y_pred, рассчитываем абсолютную ошибку
        if message_id in df.index and not pd.isnull(df.loc[message_id, 'y_true']) and not pd.isnull(df.loc[message_id, 'y_pred']):
            y_true = df.loc[message_id, 'y_true']
            y_pred = df.loc[message_id, 'y_pred']
            absolute_error = abs(y_true - y_pred)

            # Записываем данные в CSV файл
            with open('./logs/metric_log.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([message_id, y_true, y_pred, absolute_error])

            # Удаляем запись из DataFrame после записи в CSV
            df.drop(message_id, inplace=True)

    # Извлекаем сообщения из очередей y_true и y_pred
    channel.basic_consume(queue='y_true', on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue='y_pred', on_message_callback=callback, auto_ack=True)

    # Запускаем режим ожидания прихода сообщений
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
    channel.start_consuming()
except Exception as e:
    print(f'не удалось подключиться к очереди: {e}')