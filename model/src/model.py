import numpy as np
import pika
import pickle
import json

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    # Создаём подключение по адресу rabbitmq:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    # Объявляем очередь features
    channel.queue_declare(queue='features')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')


    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f'Получен вектор признаков {body}')

        # Десериализуем JSON-строку в словарь
        features_dict = json.loads(body)

        # Получаем массив признаков из словаря
        features_array = np.array(features_dict['body'])

        pred = regressor.predict(features_array.reshape(1, -1))

        # Создаем ответ в формате словаря
        response = {
            'id': features_dict['id'],
            'body': pred[0].tolist()
        }

        # Отправляем ответ в очередь y_pred
        channel.basic_publish(exchange='',
                              routing_key='y_pred',
                              body=json.dumps(response))

        print(f'Предсказание {pred[0]} отправлено в очередь y_pred')


    # Извлекаем сообщение из очереди features
    # on_message_callback показывает, какую функцию вызвать при получении сообщения
    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )

    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()

except Exception as e:
    print(f'Не удалось подключиться к очереди: {e}')
