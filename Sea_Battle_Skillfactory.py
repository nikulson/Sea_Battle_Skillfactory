
#написать свою логику игы у меня не получилось, поэтому шел по вебинару с разбором, помечая для себя важные моменты

from random import randint
#сперва создаем классы исключений
class BoardException(Exception): #родительский класс, содержащий в себе остальные классы исключений
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь вытрелить за доску"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


class Dot: #класс точек на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship: #класс корабль на поле
    def __init__(self, bow, l, o):
        self.bow = bow #точка где размещен нос корабля
        self.l = l #длина корабля
        self.o = o #ориентация корабля(верикальная, горизонтальная)
        self.lives = l #количество жизней

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l): #задаем точку носа корабля
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0: #сдвигаемя по горизонтали
                cur_x += i

            elif self.o == 1: #сдвигаемся по вертикали
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y)) #список точек

        return ship_dots

    def shooten(self, shot): #метод, показывающий, попали мы или нет
        return shot in self.dots


class Board: #класс игрового поля
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        self.count = 0  #переменная с количеством пораженных кораблей

        self.field = [["O"]*size for _ in range(size)] #атрибут хранящий в себе состояние клеток поля

        self.busy = [] # здесь будут храниться занятые кораблем или выстрелом точки
        self.ships = [] # здесь будут храниться корабли

    def __str__(self): #метод выводящий корабли на доску
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid: # параметр отвечающий нужно ли скрывать корабли на доске
            res = res.replace("■", "O")
        return res

    def out(self, d): # метод, проверяющий, находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False): #метод определяющий контур корабля
        near = [
            (-1, -1), (-1, 0) , (-1, 1), #в списке объявлены точки вокруг той, в которой мы находимся (0,0 - сама точка)
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship): #метод добавления корабля на доску

        for d in ship.dots:
            if self.out(d) or d in self.busy: #так же проверяет что точка корабля не выходит за границы и не занята
                raise BoardWrongShipException()
        for d in ship.dots:  #ставим в каждую точку корабля квадрат, и записываем ее в список занятых
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):  #метод, делающий выстрел
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:   #проверяем, принадлежит ли точка кораблю
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"  #если произошло попадание, ставим Х
                if ship.lives == 0: #если корабль уничтожен, добавляем его в счетчик подбитых кораблей, и ставим очки по его контуру
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "." #в случае промаха
        print("Мимо!")
        return False

    def begin(self): #когда начинаем игру, список busy обнуляетя
        self.busy = []


class Player:      #создаем класс игрока
    def __init__(self, board, enemy): #в качестве аргументов передаем две доски
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError() #метод должен быть у потомков класса Player

    def move(self):
        while True:
            try:
                target = self.ask() #просим дать координаты выстрела
                repeat = self.enemy.shot(target) #выполняем выстрел
                return repeat
            except BoardException as e:
                print(e)


class AI(Player): #дочерний класс компьютера
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) #генерируем две случайные точки от 0 до 5 с помощью импортируемой функции randint
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player): ##дочерний класс пользователя
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1) #возвращаем точки хода с -1, т.к. индексация в спиках с 0


class Game: #класс игры
    def __init__(self, size=6): #конструктор нашей игры, задающий размер доски
        self.size = size
        pl = self.random_board() #генерируем случайную доску игрока
        co = self.random_board() #генерируем случайную доску компьютера
        co.hid = True #скрываем корабли для компьютрера

        self.ai = AI(co, pl) #создаем игроков, передав им сгенерированные доски
        self.us = User(pl, co)

    def random_board(self): #метод, создащий доску
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):  #метод, генерирующий случайную доску
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self): #создаем интерфейс
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self): #игровой цикл
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0: #если номер хода четный, ходит пользователь
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move() #вызываем метод move, который отвечает за ход каждого игрока
            else: #если нечетный, то компьютер
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move() #запиываем результат хода в repeat, и определяем нужно ли повторить ход
            if repeat:
                num -= 1

            if self.ai.board.count == 7: #проверка количества пораженных кораблей компьютера
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7: #проверка количества пораженных кораблей пользователя
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()




