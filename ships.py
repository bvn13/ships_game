
import random
from random import shuffle


SIZE = 10


class Utils(object) :
    def _setUpCells(cells) :
        global SIZE
        for x in range(0, SIZE) :
            for y in range(0, SIZE) :
                cells.append({'x':x,'y':y})
        shuffle(cells)
    
    
    def _copyFieldData(field) :
        data = {}
        for y in field :
            data[y] = {}
            for x in field[y] :
                data[y][x] = field[y][x]
    


##################################################################


class ShipsGame(object) :
    """ SHIPS Game """
    seed = 0
    
    def __init__(self, seed=0) :
        ShipsGame.seed = seed if seed > 0 else random.random() * 99999999
        
        random.seed(ShipsGame.seed)

        self.player = Player()
        self.enemy = Player()
        
        self.lastPlayer = None
        self.winPlayer = None
        self.isEnd = False

        self.enemy.generateShips()

    def makeMove(self, field, pos) :
        ship = field.findShip(pos)
        if (ship) :
            ship.bomb(pos)
            return True
        return False
        
    def letPlayerMove(self, pos) :
        if (not self.lastPlayer or self.lastPlayer == self.enemy) :
            self.makeMove(self.enemy.field, pos)
            isAimedBefore = False
            for aim in self.enemy.aims :
                if (aim.eq(pos)) :
                    isAimedBefore = True
            if (not isAimedBefore) :
                self.enemy.aims.append(pos)
            self.lastPlayer = self.player
            if (self.enemy.isDead()) :
                self.winPlayer = self.player
                self.isEnd = True
            return True
        else :
            return False
    
    def letEnemyMove(self, pos) :
        if (self.lastPlayer == self.player) :
            self.makeMove(self.player.field, pos)
            isAimedBefore = False
            for aim in self.player.aims :
                if (aim.eq(pos)) :
                    isAimedBefore = True
            if (not isAimedBefore) :
                self.player.aims.append(pos)
            self.lastPlayer = self.enemy
            if (self.player.isDead()) :
                self.winPlayer = self.enemy
                self.isEnd = True
            return True
        else :
            return False

    def getResult(self) :
        if (self.winPlayer == self.enemy) :
            return "ENEMY WIN"
        elif (self.winPlayer == self.player) :
            return "PLAYER WIN"
        else :
            return "NOT ENDED?"


class Vector2(object) :
    """ X,Y Coordinates """
    def __init__(self, x=0, y=0) :
        self.x = x
        self.y = y
        self.isDead = False

    def eq(self, pos) :
        return self.x==pos.x and self.y==pos.y

    def set(self, x, y):
        self.x = x
        self.y = y

    def __str__(self, *args, **kwargs):
        return "(x=%d,y=%d)" % (self.x, self.y)


class MoveData(object) :
    def __init__(self, player, pos) :
        self.player = player
        self.pos = pos
    


class Ship(object) :
    """ Ship """
    def __init__(self) :
        self.pos = Vector2()
        self.vector = Vector2(x=1) if random.random() <= 0.5 else Vector2(y=1)
        self.length = 0
        self.data = []

    def _create(length) :
        """ Create ship by length """
        s = Ship()
        s.pos = Vector2()
        s.vector = Vector2(x=1)
        s.length = length
        s.__generateData()
        return s

    def __generateData(self) :
        """ Generates all ship's cells """
        if (len(self.data) != self.length) :
            self.data = []
            for i in range(0, self.length) :
                self.data.append(Vector2(self.pos.x + self.vector.x * i, self.pos.y + self.vector.y * i))
        else :
            for i in range(0, self.length) :
                self.data[i].set(self.pos.x + self.vector.x * i, self.pos.y + self.vector.y * i)
                
                
    def isDead(self) :
        for v in self.data :
            if (not v.isDead) :
                return False
        return True
        
    def bomb(self, pos) :
        for v in self.data :
            if (v.eq(pos)) :
                v.isDead = True
                return True
        return False
        
    def reset(self) :
        """ Resets ship position """
        self.pox = Vector2()
        self.vector = Vector2(x=1)
        self.__generateData()

    def moveTo(self, pos) :
        """ Moves ship to the position """
        self.pos = pos
        self.__generateData()
        
    def turn(self):
        self.vector.x = 1 - self.vector.x
        self.vector.y = 1 - self.vector.y
        self.__generateData()
        
    def isAt(self, pos) :
        """ Check if cell belong to ship """
        for v in self.data :
            if (v.eq(pos)) :
                return True
        return False

    def at(self, pos) :
        for v in self.data :
            if (v.eq(pos)) :
                return v
        return None

    def asFieldPart(self) :
        """ Returns all cells of ship """
        field = {}
        for v in self.data :
            #initing all cells of ship
            Field._createCell(field, v, 1)

            #initing nearest cells
            Field._createCell(field, Vector2(v.x-1, v.y-1), 1)
            Field._createCell(field, Vector2(v.x-1, v.y), 1)
            Field._createCell(field, Vector2(v.x-1, v.y+1), 1)
            
            Field._createCell(field, Vector2(v.x, v.y-1), 1)
            Field._createCell(field, Vector2(v.x, v.y+1), 1)
            
            Field._createCell(field, Vector2(v.x+1, v.y-1), 1)
            Field._createCell(field, Vector2(v.x+1, v.y), 1)
            Field._createCell(field, Vector2(v.x+1, v.y+1), 1)
        return field
    
    def __str__(self, *args, **kwargs):
        return "SHIP %s, len=%d, %s" % (self.pos, self.length, ("H" if self.vector.x > 0 else "V"))
    
    
    
class Field(object) :
    """
    0 or None - empty
    1 - ship
    NOT >1 - ship border
    2 - bombed ship
    3 - failed bombing
    """
    global SIZE

    size = SIZE
    
    def __init__(self, player) :
        global SIZE
        
        self.player = player
        self.data = {}
        self.ships = []
        self.cells = []
        Utils._setUpCells(self.cells)
        

    def putShip(self, ship) :
        """ Puts ship on field """
        if (not Field._valid(Vector2(ship.pos.x + ship.vector.x * ship.length, ship.pos.y + ship.vector.y * ship.length))) :
            return False
        
        for v in ship.data :
            if (self.__contains(v)) :
                return False

        shipCells = ship.asFieldPart()
        for y in shipCells :
            for x in shipCells[y] :
                if (self.__contains(Vector2(x, y))) :
                    return False

        for cell in ship.data :
            Field._createCell(self.data, cell)
            self.data[cell.y][cell.x] = 1


        return True

    def removeShip(self, ship) :
        """ Removes ship from field """
        shipCells = ship.asFieldPart()
        for y in shipCells :
            for x in shipCells[y] :
                if (self.__contains(Vector2(x, y))) :
                    return False

        for y in shipCells :
            for x in shipCells[y] :
                v = Vector2(x, y)
                Field._createCell(self.data, v)
                self.data[y][x] = max(0, 0 if ship.isAt(v) else (self.data[y][x] - 1))

        return True

    def findShip(self, pos) :
        for ship in self.ships :
            if (ship.isAt(pos)) :
                return ship
        return None

    def arrangementShips(self, ships, firstShipIndex) :
        """ Tries to arrangement ships recursively """
        
        if firstShipIndex >= len(ships) :
            return True
         
        for i in range(firstShipIndex, len(ships)) :
            ship = ships[i]

            if (random.random() >= 0.5) :
                ship.turn()

            for cell in self.cells : 
                v = Vector2(cell['x'], cell['y'])
                ship.moveTo(v)
                if (self.putShip(ship)) :
                    if (self.arrangementShips(ships, firstShipIndex+1)) :
                        self.ships.append(ship)
                        return True
                self.removeShip(ship)
                if ship in self.ships :
                    self.ships.remove(ship)
                ship.reset()
        return False

    def _createCell(data, pos, val=0) :
        """ Creates cell into field dictionary """
        if (not Field._valid(pos)) :
            return
        if (not pos.y in data) :
            data.update({pos.y : {}})
        if (not pos.x in data[pos.y]) :
            data[pos.y][pos.x] = val
    
    def _valid(pos) :
        """ Checks if cell is valid into field """
        return (pos.x >=0 and pos.x < Field.size and pos.y >= 0 and pos.y < Field.size)

    def __contains(self, pos) :
        if (pos.y in self.data and pos.x in self.data[pos.y]) :
            return self.data[pos.y][pos.x] > 0
        return False
    
    def __positionIsUnderShip(self, pos) :
        for ship in self.ships :
            if (ship.isAt(pos)) :
                return True
        return False
    
    def prepare(self) :
        """ DOES NOT WORK """
        raise RuntimeError("Method does not work")
        for ship in self.ships :
            shipCells = ship.asFieldPart()
            for y in shipCells :
                for x in shipCells[y] :
                    v = Vector2(x,y)
                    Field._createCell(self.data, v)
                    if (not ship.isAt(v)) :
                        self.data[y][x] = self.data[y][x]+1
        
    
    def __str__(self, *args, **kwargs):
        global SIZE
        str = ""
        for y in range(0, SIZE) :
            line = "("
            for x in range(0, SIZE) :
                pos = Vector2(x,y)
                isUnderShip = False
                for ship in self.ships :
                    if (ship.isAt(pos)) :
                        line += "%s" % ('*' if ship.at(pos).isDead else '1')
                        isUnderShip = True
                if (not isUnderShip) :
                    isBombed = False
                    for v in self.player.aims :
                        if (v.eq(pos)) :
                            line += '+'
                            isBombed = True
                    if (not isBombed) :
                        line += '-'
                        
                #line += "%s" %   #(self.data[y][x] if (y in self.data and x in self.data[y] and self.data[y][x] > 0) else '-', )
            line += ")\n"             
            str += line
        return str
    

class Player(object) :
    def __init__(self) :
        self.field = Field(self)
        self.aims = []

    def isDead(self) :
        for ship in self.field.ships :
            if (not ship.isDead()) :
                return False
        return True

    def generateShips(self) :
        ships = []
        ships.append(Ship._create(4))
        for i in range(0, 2) :
            ships.append(Ship._create(3))
        for i in range(0, 3) :
            ships.append(Ship._create(2))
        for i in range(0, 4) :
            ships.append(Ship._create(1))

        print("Count: %s" % len(ships))

        if (not self.field.arrangementShips(ships, 0)) :
            raise "Could not generate ships with seed %d" % (ShipsGame.seed)
        




if __name__ == '__main__' :
    game = ShipsGame()
    game.player.generateShips()
    
    
    while (not game.isEnd) :
        print("\n\n")
        print("ENEMY")
        print(game.enemy.field)
        print("PLAYER")
        print(game.player.field)
        
        command = input("ENTER MOVE: ")
        pos = None
        print("MOVE: %s" % command)
        try :
            coords = command.split(',')
            x = coords[0].strip()
            y = coords[1].strip()
            pos = Vector2(int(x), int(y))
        except :
            print("WRONG COMMAND!")
            continue
        
        print("PLAYER's BOMBING: %s" % pos)
        game.letPlayerMove(pos)
        
        searching = True
        cells = []
        Utils._setUpCells(cells)
        
        while (searching) :
            pos = cells[int(random.random() * len(cells))]
            pos = Vector2(pos['x'], pos['y'])
            isAimedBefore = False
            for aim in game.enemy.aims :
                if (aim.eq(pos)) :
                    isAimedBefore = True
            if (isAimedBefore) :
                continue
            searching = False
            print("ENEMY's BOMBING: %s" % pos)
            game.letEnemyMove(pos)

    print("ENEMY")
    print(game.enemy.field)
    print("PLAYER")
    print(game.player.field)
    print("%s" % game.getResult())