import tkinter as tk
import random
import math

CELL_SIZE = 8
GRID_WIDTH = 80
GRID_HEIGHT = 80
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 280
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 40

# Цветовая схема
COLORS = {
    'bg': '#2E3440',        # Темный фон
    'panel': '#3B4252',      # Панель управления
    'empty': '#D8DEE9',      # Пустая клетка (светло-серый)
    'tree': '#A3BE8C',       # Здоровое дерево (зеленый)
    'burning': '#BF616A',    # Горящее дерево (красный)
    'ash': '#4C566A',        # Пепел (темно-серый)
    'water': '#88C0D0',      # Вода (голубой)
    'road': '#434C5E',       # Дорога (темно-серый)
    'text': '#ECEFF4',       # Светлый текст
}

# Состояния клеток
EMPTY = 0
TREE = 1
BURNING = 2
ASH = 3
WATER = 4
ROAD = 5

# Фиксированные параметры
GROWTH_PROB = 0.01          # 1% вероятность роста
LIGHTNING_PROB = 0.0005     # 0.05% вероятность молнии

class ForestFireModel:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        
        # ПРАВИЛО 2: Глобальная влажность (ползунок)
        self.humidity = 0.3  # 30% по умолчанию
        
        # Сетки данных
        self.grid = [[EMPTY for _ in range(width)] for _ in range(height)]
        self.water_map = [[False for _ in range(width)] for _ in range(height)]
        self.road_map = [[False for _ in range(width)] for _ in range(height)]
        
        # Статистика
        self.stats = {'trees': 0, 'burning': 0, 'ash': 0, 'water': 0, 'road': 0}
        
        # Инициализация
        self._init_landscape()
        self._init_forest()
    
    def _init_landscape(self):
        """Создание рек и дорог (ПРАВИЛА 1 и 3)"""
        
        # ПРАВИЛО 1: Создаем извилистую реку
        river_y = self.height // 2
        for x in range(self.width):
            offset = int(5 * math.sin(x / 20))
            for dy in range(-2, 3):
                y = river_y + offset + dy
                if 0 <= y < self.height:
                    self.water_map[y][x] = True
                    self.grid[y][x] = WATER
        
        # ПРАВИЛО 3: Создаем дороги
        # Горизонтальная дорога
        road_y = self.height // 4
        for x in range(0, self.width, 2):
            if 0 <= road_y < self.height:
                self.road_map[road_y][x] = True
                self.grid[road_y][x] = ROAD
                if x + 1 < self.width:
                    self.road_map[road_y][x+1] = True
                    self.grid[road_y][x+1] = ROAD
        
        # Вертикальная дорога
        road_x = self.width // 4
        for y in range(0, self.height, 2):
            if 0 <= road_x < self.width:
                self.road_map[y][road_x] = True
                self.grid[y][road_x] = ROAD
                if y + 1 < self.height:
                    self.road_map[y+1][road_x] = True
                    self.grid[y+1][road_x] = ROAD
    
    def _init_forest(self, density=0.6):
        """Создание леса (не на воде и дорогах)"""
        for i in range(self.height):
            for j in range(self.width):
                if not self.water_map[i][j] and not self.road_map[i][j]:
                    if random.random() < density:
                        self.grid[i][j] = TREE
    
    def get_neighbors(self, i, j):
        """Получение соседей"""
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.append((ni, nj, di, dj))
        return neighbors
    
    def count_water_neighbors(self, i, j):
        """Подсчет количества соседних клеток с водой (ПРАВИЛО 1)"""
        count = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    if self.water_map[ni][nj]:
                        count += 1
        return count
    
    def is_road_between(self, i1, j1, i2, j2):
        """Проверка, есть ли дорога между двумя клетками (ПРАВИЛО 3)"""
        if abs(i1 - i2) > 1 or abs(j1 - j2) > 1:
            return False
        return self.road_map[i1][j1] or self.road_map[i2][j2]
    
    def step(self):
        """Один шаг симуляции"""
        new_grid = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        # Копируем воду и дороги (они не меняются)
        for i in range(self.height):
            for j in range(self.width):
                if self.water_map[i][j]:
                    new_grid[i][j] = WATER
                elif self.road_map[i][j]:
                    new_grid[i][j] = ROAD
        
        # Обнуляем статистику
        self.stats = {'trees': 0, 'burning': 0, 'ash': 0, 'water': 0, 'road': 0}
        
        for i in range(self.height):
            for j in range(self.width):
                # Пропускаем воду и дороги
                if self.water_map[i][j]:
                    self.stats['water'] += 1
                    continue
                if self.road_map[i][j]:
                    self.stats['road'] += 1
                    continue
                
                state = self.grid[i][j]
                
                # Горящее => пепел
                if state == BURNING:
                    new_grid[i][j] = ASH
                    self.stats['ash'] += 1
                
                # Пепел => пусто
                elif state == ASH:
                    if random.random() < 0.1:
                        new_grid[i][j] = EMPTY
                    else:
                        new_grid[i][j] = ASH
                        self.stats['ash'] += 1
                
                # Пусто => дерево
                elif state == EMPTY:
                    if random.random() < GROWTH_PROB:
                        new_grid[i][j] = TREE
                    else:
                        new_grid[i][j] = EMPTY
                
                # Дерево
                elif state == TREE:
                    self.stats['trees'] += 1
                    
                    # Молния
                    if random.random() < LIGHTNING_PROB * (1 - self.humidity * 0.5):
                        new_grid[i][j] = BURNING
                        self.stats['burning'] += 1
                        continue
                    
                    # Огонь от соседей
                    fire = False
                    for ni, nj, di, dj in self.get_neighbors(i, j):
                        if self.grid[ni][nj] == BURNING:
                            prob = 0.5  # Базовая вероятность
                            
                            # ПРАВИЛО 1: Влияние воды
                            water_neighbors = self.count_water_neighbors(i, j)
                            if water_neighbors > 0:
                                prob *= (1 - water_neighbors * 0.2)
                            
                            # ПРАВИЛО 2: Влияние влажности
                            prob *= (1 - self.humidity * 0.7)
                            
                            # ПРАВИЛО 3: Влияние дорог
                            if self.is_road_between(i, j, ni, nj):
                                prob *= 0.3
                            
                            prob = max(0.01, min(0.99, prob))
                            
                            if random.random() < prob:
                                fire = True
                                break
                    
                    if fire:
                        new_grid[i][j] = BURNING
                        self.stats['burning'] += 1
                        self.stats['trees'] -= 1
                    else:
                        new_grid[i][j] = TREE
        
        self.grid = new_grid
        return self.grid
    
    def add_fire(self, i=None, j=None):
        """Добавление огня (только на деревья)"""
        if i is None:
            i = random.randint(0, self.height - 1)
        if j is None:
            j = random.randint(0, self.width - 1)
        
        if self.grid[i][j] == TREE:
            self.grid[i][j] = BURNING
            return True
        return False
    
    def reset(self, density=0.6):
        """Сброс"""
        self.grid = [[EMPTY for _ in range(self.width)] for _ in range(self.height)]
        
        # Восстанавливаем воду и дороги
        for i in range(self.height):
            for j in range(self.width):
                if self.water_map[i][j]:
                    self.grid[i][j] = WATER
                elif self.road_map[i][j]:
                    self.grid[i][j] = ROAD
        
        self._init_forest(density)
        self.stats = {'trees': 0, 'burning': 0, 'ash': 0, 'water': 0, 'road': 0}
    
    def get_color(self, i, j):
        """Цвет клетки для отображения"""
        state = self.grid[i][j]
        if state == EMPTY:
            return COLORS['empty']
        elif state == TREE:
            return COLORS['tree']
        elif state == BURNING:
            return COLORS['burning']
        elif state == ASH:
            return COLORS['ash']
        elif state == WATER:
            return COLORS['water']
        elif state == ROAD:
            return COLORS['road']
        return COLORS['empty']

class ForestFireApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование лесных пожаров")
        self.root.configure(bg=COLORS['bg'])
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.model = ForestFireModel()
        self.running = False
        self.speed = 100
        
        self._setup_ui()
        self._draw_grid()
        
        # Горячие клавиши
        self.root.bind('<space>', lambda e: self.toggle())
        self.root.bind('<r>', lambda e: self.reset())
    
    def _setup_ui(self):
        """Создание интерфейса"""
        # Основной контейнер
        main = tk.Frame(self.root, bg=COLORS['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Сетка
        self.canvas = tk.Canvas(
            main,
            width=GRID_WIDTH * CELL_SIZE,
            height=GRID_HEIGHT * CELL_SIZE,
            bg=COLORS['panel']
        )
        self.canvas.pack(side=tk.LEFT)
        
        # Возможность кликать для добавления огня
        self.canvas.bind('<Button-1>', self._on_click)
        
        # Панель управления
        panel = tk.Frame(main, bg=COLORS['panel'], width=220)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        panel.pack_propagate(False)
        
        # Заголовок
        tk.Label(
            panel, text="УПРАВЛЕНИЕ",
            bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 14, 'bold')
        ).pack(pady=15)
        
        # ПРАВИЛО 2: Единственный ползунок - ВЛАЖНОСТЬ
        tk.Label(
            panel, text="ВЛАЖНОСТЬ",
            bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 11, 'bold')
        ).pack(pady=(10, 0))
        
        self.humidity_var = tk.DoubleVar(value=self.model.humidity * 100)
        
        # Ползунок влажности
        humidity_slider = tk.Scale(
            panel, from_=0, to=100, variable=self.humidity_var,
            orient=tk.HORIZONTAL, bg=COLORS['panel'], fg=COLORS['text'],
            highlightthickness=0, length=180,
            command=lambda v: setattr(self.model, 'humidity', float(v)/100)
        )
        humidity_slider.pack(pady=5)
        
        # Подпись под ползунком
        tk.Label(
            panel, 
            text="0% - сухо (огонь быстро)\n100% - влажно (огонь медленно)",
            bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 8)
        ).pack()
        
        # Разделитель
        tk.Frame(panel, height=1, bg=COLORS['text']).pack(fill=tk.X, pady=15)
        
        # Информация о правилах
        tk.Label(
            panel, text="ПРАВИЛА",
            bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 11, 'bold')
        ).pack()
        
        rules_text = """
ЛКМ - добавить огонь

ПРАВИЛО 1: ВОДА
  •Не горит
  • Каждая соседняя клетка
    с водой снижает риск на 20%

ПРАВИЛО 2: ВЛАЖНОСТЬ
  • Влияет на всё
  • Регулируется ползунком

ПРАВИЛО 3: ДОРОГИ
  • Не растут деревья
  • Преграда для огня
  • Шанс перехода 30%
        """
        
        tk.Label(
            panel,
            text=rules_text,
            bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 8), justify=tk.LEFT
        ).pack(pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(panel, bg=COLORS['panel'])
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(btn_frame, text="СТАРТ", command=self.toggle,
                                   bg='#88C0D0', width=15, height=2,
                                   font=('Arial', 10, 'bold'))
        self.start_btn.pack(pady=3)
        
        tk.Button(btn_frame, text="СБРОС", command=self.reset,
                 bg='#BF616A', width=15, height=2,
                 font=('Arial', 10, 'bold')).pack(pady=3)
        
        # Легенда
        self._add_legend(panel)
        
        # Статус
        self.status = tk.Label(
            self.root, text="", bg=COLORS['panel'], fg=COLORS['text'],
            font=('Arial', 10)
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _add_legend(self, parent):
        """Добавление легенды"""
        legend = tk.Frame(parent, bg=COLORS['panel'])
        legend.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        tk.Label(legend, text="ЛЕГЕНДА", bg=COLORS['panel'], fg='white',
                font=('Arial', 10, 'bold')).pack(anchor='w')
        
        items = [
            (COLORS['tree'], 'Дерево'),
            (COLORS['burning'], 'Горит'),
            (COLORS['ash'], 'Пепел'),
            (COLORS['water'], 'Вода'),
            (COLORS['road'], 'Дорога'),
            (COLORS['empty'], 'Пусто')
        ]
        
        for color, text in items:
            row = tk.Frame(legend, bg=COLORS['panel'])
            row.pack(anchor='w')
            
            tk.Frame(row, bg=color, width=15, height=15).pack(side=tk.LEFT, padx=2)
            tk.Label(row, text=text, bg=COLORS['panel'], fg='white').pack(side=tk.LEFT)
    
    def _draw_grid(self):
        """Отрисовка сетки"""
        self.cells = []
        for i in range(GRID_HEIGHT):
            row = []
            for j in range(GRID_WIDTH):
                x1, y1 = j * CELL_SIZE, i * CELL_SIZE
                rect = self.canvas.create_rectangle(
                    x1, y1, x1+CELL_SIZE, y1+CELL_SIZE,
                    fill=self.model.get_color(i, j), outline=COLORS['panel']
                )
                row.append(rect)
            self.cells.append(row)
    
    def _update_grid(self):
        """Обновление цветов"""
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                self.canvas.itemconfig(
                    self.cells[i][j], 
                    fill=self.model.get_color(i, j)
                )
        
        # Обновление статуса
        s = self.model.stats
        self.status.config(
            text=f"Деревья: {s['trees']}  |  Горит: {s['burning']}  |  Пепел: {s['ash']}  |  "
                 f"Вода: {s['water']}  |  Дороги:️ {s['road']}  |   Влажность: {self.model.humidity*100:.0f}%"
        )
    
    def _on_click(self, event):
        """Обработка клика по сетке - добавление огня"""
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            if self.model.add_fire(y, x):
                self._update_grid()
    
    def toggle(self):
        """Старт/пауза"""
        self.running = not self.running
        self.start_btn.config(text="ПАУЗА" if self.running else "СТАРТ")
        if self.running:
            self._step()
    
    def _step(self):
        """Шаг симуляции"""
        if self.running:
            self.model.step()
            self._update_grid()
            self.root.after(self.speed, self._step)
    
    def reset(self):
        """Сброс"""
        self.running = False
        self.start_btn.config(text="СТАРТ")
        self.model.reset()
        self._update_grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = ForestFireApp(root)
    root.mainloop()
