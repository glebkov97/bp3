import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime


def read_and_plot_data(file_path, output_file):
    # Читаем данные из CSV-файла
    df = pd.read_csv(file_path)

    # Выбираем столбец с абсолютными ошибками
    absolute_errors = df['absolute_error']

    # Создаем график
    plt.figure(figsize=(10, 6))
    sns.histplot(data=absolute_errors, kde=True)

    # Добавляем заголовок и метки осей
    plt.title('Распределение абсолютных ошибок')
    plt.xlabel('Абсолютная ошибка')
    plt.ylabel('Частота')

    # Сохраняем график в файл
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_file)


if __name__ == "__main__":
    input_file = './logs/metric_log.csv'
    output_file = './logs/error_distribution.png'

    print(f"Создание графика распределения абсолютных ошибок...")
    read_and_plot_data(input_file, output_file)
    print("График успешно создан и сохранен.")
