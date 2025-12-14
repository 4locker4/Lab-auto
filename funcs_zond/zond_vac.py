import matplotlib
import numpy as np

matplotlib.use('qtagg') 

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt

import matplotlib.animation as animation
from funcs_zond.power_unit import*
from funcs_zond.baze_func import*
from scipy.optimize import curve_fit
from uncertainties import ufloat
from uncertainties.umath import *
from uncertainties import unumpy as unp
import glob

def write_cmd(cmd, dev_name):
    try:
        with open(dev_name, "w") as dev:
            dev.write(cmd)

    except Exception as e:
        print(f"Общая ошибка: {e}")

    finally:
        return


def model_func(U, I_in, A1, A2, b, c):
    return I_in * np.tanh(A1 * (U + b)) + A2 * (U + b) + c

def read_cmd(dev_name):
    res = ""
    try:
        with open(dev_name, "r") as dev:
            while True:
                symb = dev.read(1)
                if symb == '\n':
                    break
                res += symb

    except Exception as e:
        print(f"Общая ошибка: {e}")

    finally:
        return res

def readVal(dev_name):
    write_cmd("READ?", dev_name)
    sleep(0.01)
    val = round(float(read_cmd(dev_name)), 10)
    return val

def getId(dev_name):
    write_cmd("*IDN?", dev_name)
    sleep(0.01)
    id = read_cmd(dev_name)
    print(id)
    return id

def setVoltMode(dev_name):
    write_cmd("CONF:VOLT:DC", dev_name)

def setCurMode(dev_name):
    write_cmd("CONF:CURR:DC", dev_name)

def rst(dev_name):
    write_cmd("*CLS", dev_name)
    sleep(0.01)
    write_cmd("*RST", dev_name)

def raschet(I_in, A1, A2):
    l = 5.2e-3
    d = 0.2e-3
    e = 1.6e-19
    k = 1.38e-23
    kT_e = e / (2 * A1)
    T_e = kT_e / k
    m_i = 22 * 1.66e-27  # В кг
    S = np.pi * d * l
    n_e = unp.sqrt(m_i / (2 * kT_e)) * I_in / (0.4 * e * S)
    m_e = 9.1e-31  # в кг
    omega_e = unp.sqrt(n_e) * 5.6e1
    T_i = 300
    e_0 = 8.85e-12
    r_d = unp.sqrt(k * T_i * e_0 / (n_e * e**2))
    P = (2 / 768) * 10**(5)
    n = P / (k * T_i)
    alpha = n_e / n
    N_D = (4 / 3) * np.pi * r_d**3 * n_e
    return kT_e, T_e, n_e, omega_e, r_d, N_D, alpha

def plot_fit(U, I_in, A1, A2, b, c, ax=None):
    U_sorted = np.sort(U)
    I = I_in * np.tanh(A1 * (U_sorted + b)) + A2 * (U_sorted + b) + c
    if ax is None:
        import matplotlib.pyplot as plt
        plt.plot(U_sorted, I, color="black", label="Аппроксимация")
    else:
        ax.plot(U_sorted, I, color="black", label="Аппроксимация")

def show_graph(volt_data, cur_data, param_dict):
    """Показывает отдельное окно с графиком."""
    import matplotlib
    matplotlib.use('qtagg')
    import matplotlib.pyplot as plt

    popt, pcov = curve_fit(model_func, volt_data, cur_data, maxfev=10000)
    errors = np.sqrt(np.diag(pcov))

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(volt_data, cur_data, label="Измеренные данные", color='tab:blue')
    plot_fit(volt_data, popt[0], popt[1], popt[2], popt[3], popt[4], ax=ax)

    ax.set_title("Зондовая характеристика", fontsize=14)
    ax.set_xlabel("Напряжение U, В", fontsize=12)
    ax.set_ylabel("Ток I, А", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    plt.show()

def analis_measure_with_data():
    try:
        data = np.loadtxt("./datas/output.txt", delimiter=",", skiprows=2, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            data = np.loadtxt("/datas/output.txt", delimiter=",", skiprows=2, encoding='cp1251')
        except Exception as e2:
            print(f"Ошибка загрузки файла output.txt: {e2}")
            return None
    except Exception as e:
        print(f"Ошибка загрузки файла output.txt: {e}")
        return None

    if len(data) == 0:
        print("Файл output.txt пуст!")
        return None

    volt_data = data[:, 1]
    cur_data = data[:, 2]

    try:
        popt, pcov = curve_fit(model_func, volt_data, cur_data, maxfev=10000)
        errors = np.sqrt(np.diag(pcov))
    except Exception as e:
        print(f"Ошибка аппроксимации: {e}")
        return None

    I_in = ufloat(popt[0], errors[0])
    A1_opt = ufloat(popt[1], errors[1])
    A2_opt = ufloat(popt[2], errors[2])
    b = ufloat(popt[3], errors[3])
    c = ufloat(popt[4], errors[4])

    kT_e, T_e, n_e, omega_e, r_D, N_d, alpha = raschet(I_in, A1_opt, A2_opt)

    param_dict = {
        "Ток зонда I_in": f"{I_in * 1e6:.3uS} мкА",
        "kT_e": f"{kT_e / 1.6e-19:.3uS} эВ",
        "T_e": f"{T_e / 1e4:.3uS} ×10⁴ К",
        "n_e": f"{n_e * 1e-16:.3uS} ×10¹⁰ см⁻³",
        "ω_e": f"{omega_e * 1e-9:.3uS} ×10⁹ рад/с",
        "r_D": f"{r_D * 1e6:.3uS} ×10⁻⁴ см",
        "N_d": f"{N_d:.3uS}",
        "α": f"{alpha * 1e7:.3uS} ×10⁻⁷",
    }

    return volt_data, cur_data, param_dict

def get_new_data(dev_voltmetr, dev_ampermetr):
    volt = readVal(dev_voltmetr)
    cur = readVal(dev_ampermetr)
    sleep(0.1)
    return volt, cur

def plot_fit(U, I_in, A1, A2, b, c, ax=None):
    U_sorted = np.sort(U)
    I = I_in * np.tanh(A1 * (U_sorted + b)) + A2 * (U_sorted + b) + c
    if ax is None:
        plt.plot(U_sorted, I, color="black", label="Аппроксимация")
    else:
        ax.plot(U_sorted, I, color="black", label="Аппроксимация")

def update_plot(i, step, dev_voltmetr, dev_ampermetr, fig, ax, volt_data, cur_data, start_time, times, output, power):
    print(f"update_plot i: {i}")

    if i < 50:
        power.set_voltage(i * step)
        sleep(0.5)
        volt, cur = get_new_data(dev_voltmetr, dev_ampermetr)
        current_time = time() - start_time
        output.write(f"{current_time},{volt},{cur}\n")
        output.flush()

        volt_data.append(volt)
        cur_data.append(cur)
        times.append(current_time)

        # Очистка и рисование
        ax.clear()
        ax.scatter(volt_data, cur_data, color='blue', label='Измеренные данные')
        ax.set_title("Зондовая характеристика")
        ax.set_xlabel("V, В")
        ax.set_ylabel("I, A")
        ax.grid(True)
        ax.legend()

        fig.canvas.draw()

    elif i == 50:
        power.set_voltage(0)
        sleep(1)
        show_instruction_dialog()

    elif i > 50 and i < 99:
        i_new = i - 50
        power.set_voltage(i_new * step)
        sleep(0.5)
        volt, cur = get_new_data(dev_voltmetr, dev_ampermetr)
        current_time = time() - start_time
        output.write(f"{current_time},{volt},{cur}\n")
        output.flush()

        volt_data.append(volt)
        cur_data.append(cur)
        times.append(current_time)

        ax.clear()
        ax.scatter(volt_data, cur_data, color='blue', label='Измеренные данные')
        ax.set_title("Зондовая характеристика")
        ax.set_xlabel("V, В")
        ax.set_ylabel("I, A")
        ax.grid(True)
        ax.legend()

        fig.canvas.draw()

    elif i == 99:
        power.set_voltage(0)

    return ax.lines
    
def get_measure(U_diap):
    volt_data = []
    cur_data = []
    times = []
    start_time = time()

    # Найти приборы
    id_voltmetr = "AKIP,AKIP-2101/2,NDM36GBQ4R0035,3.01.01.07"
    id_ampermetr = "AKIP,AKIP-2101/2,NDM36GBD4R0067,3.01.01.0.07"

    dev_voltmetr = dev_ampermetr = ""
    for device in glob.glob("/dev/usbtmc*"):
        if getId(device) == id_voltmetr:
            dev_voltmetr = device
        if getId(device) == id_ampermetr:
            dev_ampermetr = device

    if not dev_voltmetr or not dev_ampermetr:
        print("Не найдены измерительные приборы!")
        return [], []

    setVoltMode(dev_voltmetr)
    setCurMode(dev_ampermetr)

    power = PowerUnit(0)
    power.set_remote()
    sleep(0.5)
    power.set_max_voltage(28000)
    sleep(0.5)
    power.set_output(True)
    sleep(0.5)

    # Создаём фигуру для анимации
    fig, ax = plt.subplots()
    plt.ion()  # включаем интерактивный режим

    with open("./datas/output.txt", "w") as output:
        output.write("Измерение Вольт-Амперной характеристики \n")
        output.write("Time, s; Voltage, V; Current, A\n")

        ani = animation.FuncAnimation(
            fig, update_plot,
            fargs=(U_diap, dev_voltmetr, dev_ampermetr, fig, ax, volt_data, cur_data, start_time, times, output, power),
            frames=range(100), interval=50, blit=False, repeat=False
        )

        # Показываем анимацию (non-blocking в qtagg)
        plt.show()

        # Ждём завершения анимации (~100 * 50 мс = 5 сек + накладные)
        total_duration_ms = 100 * 50
        sleep(total_duration_ms / 1000.0 + 2)  # +2 сек на задержки

        # Закрываем анимационное окно
        plt.close(fig)

    # Возвращаем собранные данные
    return volt_data, cur_data

def show_instruction_dialog():
    """Показывает модальное окно 'Переключите тумблер' и ждёт нажатия 'Сделано'."""
    app = QApplication.instance()
    if app is None:
        # На случай, если вызывается вне GUI
        input("Чтобы продолжить, переключите П_2 в '-' и нажмите Enter")
        return

    dialog = QDialog()
    dialog.setWindowTitle("Инструкция")
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.setFixedSize(500, 120)

    layout = QVBoxLayout()
    label = QLabel("Переключите тумблер в положение П₂")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 14pt; font-weight: bold;")

    button = QPushButton("Сделано")
    button.clicked.connect(dialog.accept)
    button.setStyleSheet("""
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #1abc9c);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #16a085);
        }
    """)

    layout.addWidget(label)
    layout.addWidget(button)
    dialog.setLayout(layout)
    dialog.exec()  # Блокирующий вызов

def main():
    try:
        print("Start")

        sleep(1)

    except Exception as e:
        print(f"Общая ошибка: {e}")

    finally:
        print("End")


if __name__ == "__main__":
    main()
