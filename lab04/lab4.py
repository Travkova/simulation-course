import random
import math
import pandas as pd

class LCG:
    #линейный конгруэнтный генератор (самописный датчик)
    def __init__(self, seed=1):
        self.M = 2**63
        self.beta = 2**32 + 3
        self.state = seed

    def next(self):
        #генерация следующего числа в диапазоне [0, 1)
        self.state = (self.beta * self.state) % self.M
        return self.state / self.M

    def generate_sample(self, n):
        #генерация выборки из n чисел
        return [self.next() for _ in range(n)]

def calculate_stats(data):
    #вычисление выборочного среднего и дисперсии
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n  #дисперсия смещенная, т.к. сравниваем с теоретической дисперсией распределения
    return mean, variance

def main():
    N = 100_000  #размер выборки
    seed = 42    #фиксация зерна для воспроизводимости

    #работа с самописным датчиком (LCG)
    lcg = LCG(seed=seed)
    sample_lcg = lcg.generate_sample(N)
    mean_lcg, var_lcg = calculate_stats(sample_lcg)

    #работа с встроенным генератором
    random.seed(seed)
    sample_builtin = [random.random() for _ in range(N)]
    mean_builtin, var_builtin = calculate_stats(sample_builtin)

    #теоретические значения для U(0, 1)
    theory_mean = 0.5
    theory_var = 1.0 / 12.0

    data = {
        'Параметр': [
            'Среднее', 
            'Дисперсия', 
            'Отклонение среднего', 
            'Отклонение дисперсии'
        ],
        'Теоретическое значение': [
            theory_mean, 
            theory_var, 
            None,
            None
        ],
        'LCG (самописный)': [
            mean_lcg, 
            var_lcg, 
            abs(mean_lcg - theory_mean), 
            abs(var_lcg - theory_var)
        ],
        'Встроенный (random)': [
            mean_builtin, 
            var_builtin, 
            abs(mean_builtin - theory_mean), 
            abs(var_builtin - theory_var)
        ]
    }
    
    df = pd.DataFrame(data)
    print(df.to_string(index=False, float_format='%.6f'))

if __name__ == "__main__":
    main()
