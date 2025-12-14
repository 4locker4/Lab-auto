import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QTableWidgetItem,
    QTextBrowser, QLabel, QPushButton, QTableWidget,
    QSpacerItem, QSizePolicy, QVBoxLayout, QHBoxLayout
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

from PySide6.QtCore import QUrl

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
import numpy as np

from PySide6.QtGui import QDesktopServices

import webbrowser
from PySide6.QtWidgets import QMessageBox

# Импорт для вкладки зонда
from funcs_zond.zond_vac import analis_measure_with_data, show_graph, get_measure
# from func_volt.ignition import found_ignition

from Source_HV import src_hv
from Vlmeter import vi_meter

from Source_HV.src_hv import HV_source

HV_src = src_hv.HV_source("/dev/ttyUSB0")

V1 = vi_meter.VI_meter("AKIP,AKIP-2101/2,NDM36GBD4R0063,3.01.01.07")
A1 = vi_meter.VI_meter("AKIP,AKIP-2101/2,NDM36GBD4R0068,3.01.01.07")

def found_ignition():
    volt_ign, cur_ign = HV_src.stepToCur(300)

    print(f"Ignition: {volt_ign} V, {cur_ign} uA")
    with open("./datas/ignition.txt", "w") as f:
        f.write(f"{volt_ign} {cur_ign}\n")

class GasDischargeApp:
    def __init__(self):
        app = QApplication(sys.argv)

        ui_path = "lab.ui"
        if not os.path.exists(ui_path):
            print(f"[Ошибка] Файл '{ui_path}' не найден!")
            input("Нажмите Enter для выхода...")
            sys.exit(1)

        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"[Ошибка] Не удалось открыть '{ui_path}'")
            input("Нажмите Enter для выхода...")
            sys.exit(1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        if not self.window:
            print("[Ошибка] Не удалось загрузить интерфейс:")
            print(loader.errors())
            input("Нажмите Enter для выхода...")
            sys.exit(1)

        # Commit to start without devices
        # if src_hv.checkPorts() or vi_meter.checkMeters():
        #     QMessageBox.critical(self.window, "Ошибка", "Ports error")
        #     return
        
        # if HV_src.init() != 0:
        #     QMessageBox.critical(self.window, "Ошибка", "Не удалось открыть HV источник")
        #     return

        # if V1.init("V") or A1.init("A"):
        #     QMessageBox.critical(self.window, "Ошибка", "Init meters error")
        #     return
        
        # Подключаем кнопки
        self.window.startButton.clicked.connect(self.on_start_probe_clicked)     # Зонд
        self.window.startButton_IU.clicked.connect(self.on_start_iu_clicked)     # U(I)

        self.window.spinBox_discharge_current.setRange(0, 5000)

        # Добавляем вкладку "Об авторах"
        if hasattr(self.window, 'tabWidget'):
            authors_tab = self.create_authors_tab()
            self.window.tabWidget.addTab(authors_tab, "🎓 Об авторах")

        self.window.setWindowTitle("Лабораторная: Газовый разряд")
        self.window.show()
        sys.exit(app.exec())

    # --- Вкладка: График U(I) ---
    def read_ignition_data(self, filename="./datas/ignition.txt"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
                parts = line.split()
                if len(parts) == 2:
                    U_zag = float(parts[0])
                    I_zag = float(parts[1])
                    return U_zag, I_zag
        except Exception as e:
            print(f"Ошибка чтения ignition.txt: {e}")
        return None, None

    def create_authors_tab(self):
        """Создаёт вкладку 'Об авторах' программно"""
        # Главный виджет вкладки
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Центрируем содержимое
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Центральная колонка
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignTop)

        # Заголовок
        title = QLabel("<h2 style='color:#FFE873; text-align:center;'>Об авторах</h2>")
        title.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(title)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #333333;")
        center_layout.addWidget(line)

        # Текст с авторами (всё в одном QLabel)
        html_text = """
        <style>
            body { font-family:'Segoe UI'; font-size:13pt; color:#ffffff; line-height:1.6; }
            a { color:#FFD700; text-decoration:underline; }
            a:hover { color:#FFE873; }
            h3 { color: #FFE873; margin-top: 20px; margin-bottom: 10px; font-weight:bold; }
        </style>
        <h3>Backend:</h3>
        <p><a href="https://t.me/ProVrestX">Сидоров Андрей Денисович</a>, МФТИ ФРКТ 2025</p>
        <p><a href="https://t.me/EgOuOrio">Ремчуков Егор Тимофеевич</a>, МФТИ ФРКТ 2025</p>
        <p><a href="https://t.me/dalleksvsphysics">Хавронин Иван Евгеньевич</a>, МФТИ ФРКТ 2025</p>
        <p><a href="https://t.me/matarenko">Матаренко Григорий Андреевич</a>, МФТИ ЛФИ 2025</p>
        <p><a href="https://t.me/BahbIch">Бахвалов Андрей Семенович</a>, МФТИ ЛФИ 2025</p>

        <h3>Frontend:</h3>
        <p><a href="https://t.me/EgOuOrio">Ремчуков Егор Тимофеевич</a>, МФТИ ФРКТ 2025</p>

        <h3>Научный руководитель</h3>
        <p>Амброзевич Сергей Александрович, МФТИ</p>
        """

        label = QLabel(html_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setOpenExternalLinks(False)  # важно!
        label.linkActivated.connect(self.on_author_link_clicked)
        label.setStyleSheet("padding: 15px;")
        label.setMinimumWidth(500)

        center_layout.addWidget(label)
        center_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        layout.addLayout(center_layout)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        return tab
    
    def on_author_link_clicked(self, url: str):
        """Обработка клика по ссылке в QLabel"""
        if not url.startswith("https://t.me/"):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self.window, "Ошибка", "Поддерживаются только ссылки на Telegram.")
            return
    
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
    
        success = QDesktopServices.openUrl(QUrl(url))
        if not success:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.window,
                "Ошибка",
                "Не удалось открыть ссылку. Убедитесь, что установлен Telegram или браузер."
            )

    def plot_iu_graph_separate_window(self, U, I):
        try:
            R_diff, b = np.polyfit(U, I, 1)
            U_fit = np.linspace(min(U), max(U), 100)
            I_fit = R_diff * U_fit + b

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(U, I, 'ro', markersize=4, label='Измеренные данные')
            ax.plot(U_fit, I_fit, 'b-', linewidth=2, label=f'y = {R_diff:.2f}x + {b:.2f}')
            ax.set_xlabel('Напряжение U, В')
            ax.set_ylabel('Ток I, мА')
            ax.set_title('Вольт-амперная характеристика')
            ax.grid(True)
            ax.legend()
            plt.show()
        except Exception as e:
            QMessageBox.critical(self.window, "Ошибка графика", str(e))

    def on_start_iu_clicked(self):
        filename = "./datas/data.txt"

        # Снятие показаний
        # Commit to start without devices
        try:    
        #     found_ignition()

        #     HV_src.stepToCur(500)

        #     file = open(filename, "w")
        #     HV_src.stepToCur(4800, file=file, V1=V1, A1=A1)
        #     file.close()

        #     V1.reset()
        #     A1.reset()

        # Чтение данных
            filename = "./datas/data.txt"

            U, I = [], []
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.split()
                        if len(parts) == 2:
                            U.append(float(parts[0]))
                            I.append(float(parts[1]))

        except Exception as e:
            QMessageBox.critical(self.window, "Ошибка", f"Не удалось прочитать {filename}:\n{e}")
            return

        if not U:
            QMessageBox.warning(self.window, "Пусто", "Файл данных пуст.")
            return

        # Заполняем таблицу (на всё левое окно)
        table = self.window.table_points_iu
        table.setRowCount(len(U))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["U, В", "I, мА"])
        table.horizontalHeader().setStretchLastSection(True)

        for i in range(len(U)):
            table.setItem(i, 0, QTableWidgetItem(f"{U[i]:.3f}"))
            table.setItem(i, 1, QTableWidgetItem(f"{I[i]:.3f}"))

        # Читаем Uзажигания и Iзажигания
        U_zag, I_zag = self.read_ignition_data("./datas/ignition.txt")

        # Формируем текст для одного поля
        if U_zag is not None and I_zag is not None:
            text = f"U<sub>зажигания</sub> = {U_zag:.1f} В<br>I<sub>зажигания</sub> = {I_zag:.1f} мА"
        else:
            text = "U<sub>зажигания</sub> = — В<br>I<sub>зажигания</sub> = — мА"

        self.window.textBrowser_U_I_zag.setHtml(f'<html><body><p>{text}</p></body></html>')

        # График в отдельном окне
        self.plot_iu_graph_separate_window(U, I)

    # --- Вкладка: ВАХ зонда ---
    def on_start_probe_clicked(self):
        discharge_current = self.window.spinBox_discharge_current.value()
        u_diap = self.window.spinBox_voltage.value()

        print(f"Ток разряда: {discharge_current} мкА")
        print(f"Диапазон напряжения: {-u_diap} → {u_diap} В")

        if (discharge_current == 0):
            QMessageBox.critical(self.window, "Ошибка", f"Ток разрядки 0")
            return
        if (u_diap == 0):
            QMessageBox.critical(self.window, "Ошибка", f"Диапазон напряжения 0!")
            return
        
        # Снятие показаний
        # Commit to start without devices
        # HV_src.stepToCur(discharge_current)

        get_measure(u_diap * 1000 / 50)
        
        # Расчеты
        result = analis_measure_with_data()
        if result is None:
            return

        volt_data, cur_data, param_dict = result

        # Таблица точек
        table_points = self.window.table_points
        table_points.setRowCount(len(volt_data))
        table_points.setColumnCount(2)
        table_points.setHorizontalHeaderLabels(["U, В", "I, А"])
        table_points.horizontalHeader().setStretchLastSection(True)

        for i in range(len(volt_data)):
            table_points.setItem(i, 0, QTableWidgetItem(f"{volt_data[i]:.3f}"))
            table_points.setItem(i, 1, QTableWidgetItem(f"{cur_data[i]:.2e}"))

        # Таблица параметров
        table_params = self.window.table_params
        keys = list(param_dict.keys())
        table_params.setRowCount(len(keys))
        table_params.setColumnCount(1)
        table_params.setVerticalHeaderLabels(keys)
        table_params.horizontalHeader().setVisible(False)
        table_params.horizontalHeader().setStretchLastSection(True)

        for i, key in enumerate(keys):
            table_params.setItem(i, 0, QTableWidgetItem(str(param_dict[key])))

        show_graph(volt_data, cur_data, param_dict)

def main():
    GasDischargeApp()

if __name__ == "__main__":
    main()