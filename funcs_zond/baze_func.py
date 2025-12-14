import numpy as np
import pandas as pd
from funcs_zond.grafics import *
import math
import pyperclip
import io
import sys
import re



def avg(mas):
    return sum(mas)/len(mas)

def approx_line(x, y, apr_line = True):
    x = np.asarray(x)
    y = np.asarray(y)
    k = (avg(x*y) - avg(x)*avg(y))/(avg(x*x) - avg(x)**2)
    b = avg(y) - k * avg(x)
    n = len(x)
    delta_y = [(i - avg(y))**2 for i in y]
    delta_x = [(i - avg(x)) ** 2 for i in x]
    sigma2 = math.fabs(avg(delta_y)/avg(delta_x) - k**2)#Погрешность в квадрате
    sigma2 = sigma2/(n-2)
    sigma_k = math.sqrt(sigma2)
    sigma_b =  sigma_k * math.sqrt(avg(x*x) - avg(x)*avg(x))

    #постройка аппроксимируемой линии
    if apr_line == True:
        x_apr = np.linspace(min(x), max(x), 30)
        y_apr = k * x_apr + b
        plt.plot(x_apr, y_apr, **aprox_params)

    #Вычесление инструментальной погрешности путем проведение прямой с максимальным и минимальным наклонами
    return k, sigma_k, b, sigma_b
  



#def rand_err(x, y):

def mnk(y):
    y_avg = avg(y)
    n = len(y)
    sum_1 = 0
    for v in y:
        delta = v - y_avg
        sum_1 += delta ** 2
    if n >= 10:
        sigma = math.sqrt(sum_1/n)
    else:
        sigma = math.sqrt(sum_1 / (n-1))
    return sigma

def comma_to_point(data):
    if type(data) == str:
        str_new = data.replace(',', '.')
        mas_str = str_new.split()
        mas_str = list(map(float, mas_str))
        return "np.asarray(" + f"{mas_str}" + ")"
    elif isinstance(data, np.ndarray):
        str_new = ''
        for i in data:
            str_new += f'\n{i}'
        str_new = str_new.replace(".", ",")
        return str_new
    else: return 0

def accumulated_ammount(list1):
    if type(list1) == str:
        list1 = comma_to_point(list1)
    elif isinstance(list1, np.ndarray) or type(list1) == list: list1 = np.asarray(list1)
    else:return 0
    l1 = np.array([])
    sum_am = 0
    for i in list1:
        sum_am += i
        l1 = np.append(l1, sum_am)
    return l1

#Удобный вывод списка для LaTex файла(copy list to Latex)
def clL(list):
    if type(list) == str:
        list = comma_to_point(list)
    elif isinstance(list, np.ndarray):
        list = list
    else: return 0
    str_1 = ''
    for i in list:
        str_1 += f'\n{i}'
    return str_1

#Удобный вывод списка для LaTex файла(copy list to Google table)
def clGT(list):
    if type(list) == str:
        list = list
    elif isinstance(list, np.ndarray):
        list = comma_to_point(list)
    else: return 0

    return list

#print в буфер обмена
def print1(str, b = True):
    output_buffer = io.StringIO()
    sys.stdout = output_buffer  # перенаправляем стандартный вывод
    if isinstance(str, np.ndarray) and b:
        print(str.tolist())
    else: print(str)
    sys.stdout = sys.__stdout__
    program_output = output_buffer.getvalue()
    pyperclip.copy(program_output)

#convert pd.dataframe or dictionary to LaTex table
def table(data, n = 1):
    df = pd.DataFrame(data)
    numbers = f"%.{n}f"
    latex_table = df.to_latex(
        index=False,
        escape=False,
        column_format="|c" * len(df.columns) + "|",
        float_format=numbers  # Устанавливаем формат с двумя знаками после запятой
    )
    latex_table = latex_table.replace(r'\\', r'\\ \hline')

    # Добавление верхней и нижней линии таблицы
    pattern = r"(\|c)+"
    latex_str = r'''\begin{tabular}
    \hline'''
    latex_table = re.sub(pattern, r"\g<0> \\hline", latex_table)
    latex_table = latex_table.replace(r" \hline|}", "|} \n\hline")
    latex_table = "\\begin{table}\n\\centering\n" + latex_table
    latex_table = latex_table + "\\end{table}"
    latex_table = latex_table.replace(r"\midrule", "")
    latex_table = latex_table.replace(r"\toprule", "")
    latex_table = latex_table.replace(r"\bottomrule", "")
    latex_table = "\n".join(line for line in latex_table.splitlines() if line.strip())
    return latex_table

def show_table(df):
    fig, ax = plt.subplots(figsize=(8, len(df) + 2))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    plt.show()

#Передается функции масив или матрица значений и погрешности. Он возвращает список строк в котором представлено в виде "300 \pm 1"
def uni(k, sigma, n):
    k = [round(i, n) for i in k]
    sigma = [round(i, n) for i in sigma]
    l = [fr"{k[i]} $\pm$ {sigma[i]}" for i in range(len(k))]
    return l

def approx_poly(x, y, deg):
    coeffs = np.polyfit(x, y, deg=deg)  # коэффициенты полинома
    poly = np.poly1d(coeffs)  # сам полином

    # значения аппроксимирующей кривой
    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = poly(x_fit)
    line = plt.plot(x_fit, y_fit)
    return line

#Функция перегоняет числа из одого формата в другой
#source откуда берутся данные: list (массив в питоне), google_table, latex. exit - куда они уходят
def comfort_format(source, lists, exit):
        str_out= ''
        if source == "list" and exit == "latex":
            if type(source) == list:
                source = np.asarray(source)
            str_out = ""
            for i in lists:
                i = str(i)
                str_out += f"{i} + \t"
        if source == 'google_table' and exit == 'list':
            1+1
        return str_out

# n = np.array([1, 2, 3, 4, 5, 6 , 7])
# arr_K = np.array([0.556, 0.167, 0.094, 0.066, 0.051, 0.059, 0.039])
# plt.scatter(n, arr_K,**scatter_params)
# plt.ylabel(r"$K_n$")
# plt.xlabel(r"$n$")
# plt.show()
#формула персеваля
