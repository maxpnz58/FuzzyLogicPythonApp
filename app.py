import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
import numpy as np
from typing import Optional
import skfuzzy as fuzz
from matplotlib import pyplot as plt

tip_centroid_base = None
tip_bisector_base = None
tip_MOM_base = None
tip_SOM_base = None
tip_LOM_base = None

class TipCalculator(QWidget):
    def __init__(self):
        super().__init__()
        # Инициализация компонентов интерфейса
        self.initUI()

    def initUI(self):
        self.setWindowTitle("КАЛЬКУЛЯТОР ЧАЕВЫХ МЕТОДАМИ НЕЧЕТКОЙ ЛОГИКИ")

        # Основной вертикальный стек
        main_layout = QVBoxLayout()

        # Горизонтальный стек для кнопок
        button_layout = QHBoxLayout()

        # Поле ввода суммы заказа
        self.order_amount_label = QLabel("СУММА ЗАКАЗА:")
        self.order_amount_input = QLineEdit(self)
        self.order_amount_input.setPlaceholderText("ВВЕДИТЕ СУММУ ЗАКАЗА")

        # Слайдер для качества обслуживания
        self.service_label = QLabel("ОЦЕНИТЕ КАЧЕСТВО ОБСЛУЖИВАНИЯ:")
        self.service_slider = QSlider(Qt.Orientation.Horizontal)
        self.service_slider.setRange(0, 10)
        self.service_slider.setTickInterval(1)
        self.service_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        # Слайдер для качества еды
        self.food_label = QLabel("ОЦЕНИТЕ КАЧЕСТВО ЕДЫ:")
        self.food_slider = QSlider(Qt.Orientation.Horizontal)
        self.food_slider.setRange(0, 10)
        self.food_slider.setTickInterval(1)
        self.food_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        # Кнопка для вычисления чаевых
        self.calculate_button = QPushButton("РАСЧИТАТЬ ЧАЕВЫЕ", self)
        self.calculate_button.clicked.connect(self.calculate_tip)

        # Label методов дефаззификации
        self.defaz_method_label = QLabel("ПОПРОБУЙТЕ РАЗЛИЧНЫЕ МЕТОДЫ ДЕФАЗИФИКАЦИИ НЕЧЕТКОЙ ЛОГИКИ")
        self.defaz_method_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label для отображения результатов
        self.result_label = QLabel("Чаевые: 0.0 ₽")
        font = QFont("Arial", 20, QFont.Weight.Bold)
        self.result_label.setFont(font)

        # Label для дисклеймера
        self.disclamer_label = QLabel("* МАКСИМАЛЬНЫЙ % ЧАЕВЫХ ОТ СУММЫ ЗАКАЗА ОГРАНИЦЕН 15%")

        # Добавляем 4 кнопки в горизонтальный стек
        tip_centroid_button = QPushButton("ЦЕНТРОИД")
        tip_bisector_button = QPushButton("БИССЕКТРОИД")
        tip_MOM_button = QPushButton("MOM")
        tip_SOM_button = QPushButton("SOM")
        tip_LOM_button =  QPushButton("LOM")

        tip_centroid_button.clicked.connect(lambda: self.choose_defaz_method_func(tip_centroid_base))
        tip_bisector_button.clicked.connect(lambda: self.choose_defaz_method_func(tip_bisector_base))
        tip_MOM_button.clicked.connect(lambda: self.choose_defaz_method_func(tip_MOM_base))
        tip_SOM_button.clicked.connect(lambda: self.choose_defaz_method_func(tip_SOM_base))
        tip_LOM_button.clicked.connect(lambda: self.choose_defaz_method_func(tip_LOM_base))

        
        button_layout.addWidget(tip_centroid_button)
        button_layout.addWidget(tip_bisector_button)
        button_layout.addWidget(tip_MOM_button)
        button_layout.addWidget(tip_SOM_button)
        button_layout.addWidget(tip_LOM_button)

        # Зона для вывода графика
        self.picture = QLabel("ПРОИЗВЕДИТЕ РАСЧЕТЫ И ТУТ ПОЯВЯТСЯ ГРАФИКИ", self)
        self.picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picture.setFixedSize(1280, 719)
        self.picture.setStyleSheet("border: 1px solid black;")
        self.picture.setScaledContents(True)

        # Добавление всех элементов в layout
        main_layout.addWidget(self.order_amount_label)
        main_layout.addWidget(self.order_amount_input)
        main_layout.addWidget(self.service_label)
        main_layout.addWidget(self.service_slider)
        main_layout.addWidget(self.food_label)
        main_layout.addWidget(self.food_slider)
        main_layout.addWidget(self.calculate_button)
        main_layout.addWidget(self.defaz_method_label)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.result_label)
        main_layout.addWidget(self.disclamer_label)
        main_layout.addWidget(self.picture, alignment=Qt.AlignmentFlag.AlignCenter)

        # Установка основного layout
        self.setLayout(main_layout)

    def calculate_tip(self):
        # Получение суммы заказа
        try:
            global order_amount
            order_amount = float(self.order_amount_input.text())
        except ValueError:
            self.result_label.setText("Ошибка! Введите корректную сумму.")
            return

        # Получение оценок качества
        service_quality = self.service_slider.value()
        food_quality = self.food_slider.value()

        # Получаем расчетные значения процента чаевых
        global tip_centroid_base, tip_bisector_base, tip_MOM_base, tip_SOM_base, tip_LOM_base
        tip_centroid_base, tip_bisector_base, tip_MOM_base, tip_SOM_base, tip_LOM_base = calculateFuzzy(service_quality, food_quality)

        total_tip_percentage = tip_MOM_base
        total_tip = (total_tip_percentage / 100) * order_amount

        # Вывод результатов
        self.result_label.setText(f"Чаевые: {total_tip:.2f} ₽")

        pixmap = QPixmap("img/solve.png")  # Путь к вашему изображению
        self.picture.setPixmap(pixmap)  # Устанавливаем изображение в QLabel
        self.picture.setText("")

    def choose_defaz_method_func(self, value: Optional[float]):
        if value is None:
            self.result_label.setText("Чаевые: СНАЧАЛА ВВЕДИТЕ СУММУ И НАЖМИТЕ РАСЧИТАТЬ")  # Сообщение о пропущенном значении
            return
        total_tip = (value / 100) * order_amount
        self.result_label.setText(f"Чаевые: {total_tip:.2f} ₽")


def calculateFuzzy(service_score, food_score):
    # Определяем диапазоны для переменных
    x_service = np.arange(0, 10.01, 0.5)
    x_food = np.arange(0, 10.01, 0.5)
    x_tip = np.arange(0, 15.05, .5)

    # Определяем функции принадлежности
    service_low = fuzz.trimf(x_service, [0, 0, 5])
    service_middle = fuzz.trimf(x_service, [0, 5, 10])
    service_high = fuzz.trimf(x_service, [5, 10, 10])

    food_low = fuzz.zmf(x_food, 0, 5)
    food_middle = fuzz.pimf(x_food, 0, 4, 5, 10)
    food_high = fuzz.smf(x_food, 5, 10)

    tip_low = fuzz.trimf(x_tip, [0, 0, 13])
    tip_middle = fuzz.trimf(x_tip, [0, 13, 25])
    tip_high = fuzz.trimf(x_tip, [13, 25, 25])

    # Устанавливаем оценки для качества обслуживания и еды
    service_score = service_score
    food_score = food_score

    # Вычисляем степень принадлежности для каждого значения
    service_low_degree = fuzz.interp_membership(x_service, service_low, service_score)
    service_middle_degree = fuzz.interp_membership(x_service, service_middle, service_score)
    service_high_degree = fuzz.interp_membership(x_service, service_high, service_score)

    food_low_degree = fuzz.interp_membership(x_food, food_low, food_score)
    food_middle_degree = fuzz.interp_membership(x_food, food_middle, food_score)
    food_high_degree = fuzz.interp_membership(x_food, food_high, food_score)

    # Метод Мамдани (max-min) для вычисления степени активации
    low_degree = np.fmax(service_low_degree, food_low_degree)
    middle_degree = service_middle_degree
    high_degree = np.fmax(service_high_degree, food_high_degree)

    activation_low = np.fmin(low_degree, tip_low)
    activation_middle = np.fmin(middle_degree, tip_middle)
    activation_high = np.fmin(high_degree, tip_high)

    # Агрегация с использованием max для случаев "или"
    aggregated = np.fmax(activation_low, np.fmax(activation_middle, activation_high))

    # Дефазификация с помощью различных методов
    tip_centroid = fuzz.defuzz(x_tip, aggregated, 'centroid')
    tip_bisector = fuzz.defuzz(x_tip, aggregated, 'bisector')
    tip_MOM = fuzz.defuzz(x_tip, aggregated, "MOM")
    tip_SOM = fuzz.defuzz(x_tip, aggregated, "SOM")
    tip_LOM = fuzz.defuzz(x_tip, aggregated, "LOM")

    # Выводим результаты
    print(f"Центроид: {tip_centroid}")
    print(f"Биссектор: {tip_bisector}")
    print(f"MOM: {tip_MOM}")
    print(f"SOM: {tip_SOM}")
    print(f"LOM: {tip_LOM}")

    # Настраиваем параметры визуализации холста
    fig_scale_x = 2.0
    fig_scale_y = 1.5
    plt.figure(figsize=(6.4 * fig_scale_x, 4.8 * fig_scale_y))
    row = 2
    col = 3

    # Рисуем график для качества обслуживания 
    plt.subplot(row, col, 1)
    plt.title("Качество обслуживания")
    plt.plot(x_service, service_low, label="низкое", marker=".")
    plt.plot(x_service, service_middle, label="среднее", marker=".")
    plt.plot(x_service, service_high, label="высокое", marker=".")
    plt.plot(service_score, 0.0, label="оценка сервиса", marker="D")
    plt.plot(service_score, service_low_degree, label="низкая степень", marker="o")
    plt.plot(service_score, service_middle_degree, label="средняя степень", marker="o")
    plt.plot(service_score, service_high_degree,label="высокая степень", marker="o")
    plt.legend(loc="upper left")

    # Рисуем график для качества еды 
    plt.subplot(row, col, 2)
    plt.title("Качество еды")
    plt.plot(x_food, food_low, label="низкое", marker=".")
    plt.plot(x_food, food_middle, label="среднее", marker=".")
    plt.plot(x_food, food_high, label="высокое", marker=".")
    plt.plot(food_score, 0.0, label="оценка еды", marker="D")
    plt.plot(food_score, food_low_degree, label="низкая степень", marker="o")
    plt.plot(food_score, food_middle_degree, label="средняя степень", marker="o")
    plt.plot(food_score, food_high_degree, label="высокая степень", marker="o")
    plt.legend(loc="upper left")

    # Рисуем график для чаевых
    plt.subplot(row, col, 3)
    plt.title("Чаевые")
    plt.plot(x_tip, tip_low, label="низкие", marker=".")
    plt.plot(x_tip, tip_middle, label="средние", marker=".")
    plt.plot(x_tip, tip_high, label="высокие", marker=".")
    plt.legend(loc="upper left")

    # Рисуем правила нечеткой логики
    plt.subplot(row, col, 4)
    plt.title("Правила нечеткой логики")
    t = ("плохая еда или сервис <-> плохо\n\n\n" 
        "средний сервис <-> средне\n\n\n"
        "хорошая еда или \n хороший сервис <-> хорошо")
    plt.text(0.1, 0.3, t)

    activation_low = np.fmin(low_degree, tip_low)
    activation_middle = np.fmin(middle_degree, tip_middle)
    activation_high = np.fmin(high_degree, tip_high)

    # Рисуем график активации чаевых методом Мамдани
    plt.subplot(row, col, 5)
    plt.title("Распределение чаевых: Метод Мамдани")
    plt.plot(x_tip, activation_low, label="низкие чаевые", marker=".")
    plt.plot(x_tip, activation_middle, label="средние чаевые", marker=".")
    plt.plot(x_tip, activation_high, label="высокие чаевые", marker=".")
    plt.legend(loc="upper left")
    
    # Рисуем график с финальными значениями
    plt.subplot(row, col, 6)
    plt.title("Агрегация и дефазификация")
    plt.plot(x_tip, aggregated, label="нечеткий результат", marker=".")
    plt.plot(tip_centroid, 0.0, label="центроид", marker="o")
    plt.plot(tip_bisector, 0.0, label="биссектор", marker="o")
    plt.plot(tip_MOM, 0.0, label="MOM", marker="o")
    plt.plot(tip_SOM, 0.0, label="SOM", marker="o")
    plt.plot(tip_LOM, 0.0, label="LOM", marker="o")
    plt.legend(loc="upper left")

    plt.savefig("img/solve")

    return tip_centroid, tip_bisector, tip_MOM, tip_SOM, tip_LOM


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = TipCalculator()
    window.show()

    sys.exit(app.exec())
