import pika
import json
import csv
import pandas as pd

# Инициализируем список для хранения данных
data_list = []

# Создаем DataFrame для хранения данных
df = pd.DataFrame(columns=['id', 'y_true', 'y_pred', 'absolute_error'])

# Создаем файл для логирования метрик
with open('./logs/metric_log.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=df.columns.tolist())
    writer.writeheader()


# Функция для расчета абсолютной ошибки
def calculate_absolute_error(df):
    df['absolute_error'] = abs(df['y_true'] - df['y_pred'])
    return df


# Функция для сохранения данных в файл
def save_to_csv(df):
    df.to_csv('./logs/metric_log.csv', index=False)


# Функция для обработки сообщений
def process_messages(messages):
    global data_list
    for message in messages:
        if 'id' in message and 'body' in message:
            data = {
                'id': message['id'],
                'y_true': float(message['body'])
            }
            data_list.append(data)

            # Если у нас есть как y_true, так и y_pred, то можем рассчитать абсолютную ошибку
            if len(data_list) >= 2:
                y_true = data_list[-2]['y_true']
                y_pred = float(message['body'])
                absolute_error = abs(y_true - y_pred)

                # Обновляем данные_list с новой записью
                data_list[-1] = {**data_list[-1], 'absolute_error': absolute_error}

                # Сохраняем данные в CSV-файл
                save_to_csv(pd.DataFrame(data_list))


# Создаем подключение к серверу на локальном хосте
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Объявляем очередь y_true
channel.queue_declare(queue='y_true')
# Объявляем очередь y_pred
channel.queue_declare(queue='y_pred')


# Создаём функцию callback для обработки данных из очереди
def callback(ch, method, properties, body):
    print(f'Из очереди {method.routing_key} получено значение {json.loads(body)}')

    # Вызываем функцию обработки сообщений
    process_messages([json.loads(body)])


# Извлекаем сообщение из очереди y_true
channel.basic_consume(
    queue='y_true',
    on_message_callback=callback,
    auto_ack=True
)

# Извлекаем сообщение из очереди y_pred
channel.basic_consume(
    queue='y_pred',
    on_message_callback=callback,
    auto_ack=True
)

print('...Ожидание сообщений, для выхода нажмите CTRL+C')
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print('Стоппинг...')
finally:
    connection.close()

