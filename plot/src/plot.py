import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def read_and_plot_data(input_file, output_file):
    # Читаем данные из CSV-файла
    df = pd.read_csv(input_file)

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
    with pd.option_context('mode.use_inf_as_na', True):  # Используем современный подход
        read_and_plot_data(input_file, output_file)
    print("График успешно создан и сохранен.")
