import numpy as np
import matplotlib.pyplot as plt

def plot_iu_graph(filename):
    U = []
    I = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():             
                u, i = line.split()      
                U.append(float(u))
                I.append(float(i))

    plt.figure(figsize=(8, 6))
    
    R_diff, b = np.polyfit(U, I, 1)
    U_fit = np.linspace(min(U), max(U), 100)
    I_fit = R_diff * U_fit + b
    plt.plot(U_fit, I_fit, 'b-', linewidth=2, label=f'y = {R_diff:.2f}x + {b:.2f}')
    
    plt.xlabel('Напряжение U, В')
    plt.ylabel('Ток I, мА')
    plt.title('Вольт-амперная характеристика диода')
    plt.grid(True)
    plt.legend()
    plt.savefig('U(I).jpg', dpi=300, bbox_inches='tight')
    plt.show()

    return R_diff

print(plot_iu_graph('1.txt'))