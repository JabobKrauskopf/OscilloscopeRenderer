class Coordinate:

    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y


class Edge:

    def __init__(self, first: int, second: int, weight: float, firstCoordinate: Coordinate, secondCoordinate: Coordinate):
        super().__init__()
        self.first = first
        self.second = second
        self.firstCoordinate = firstCoordinate
        self.secondCoordinate = secondCoordinate
        self.weight = weight

    # def __getitem__(self, weight):
    #     return self.weight

    def other(self, v):
        if self.first == v:
            return self.second
        else:
            return self.first


class EdgeWeightedGraph:

    def __init__(self, V: int, sizeX: int, sizeY: int):
        super().__init__()
        if (V < 0):
            raise ValueError('The Number of vertices must be non negative')
        self.V = V
        self.E = 0
        self.adj = [[]] * V
        self.coords = [Coordinate(0, 0)] * V

    def __validateVertex(self, v: int):
        if v < 0 or v >= self.V:
            raise ValueError('Vertex ' + str(v) + " is not between 0 and " + str(self.V - 1))

    def addEdge(self, e: Edge):
        self.__validateVertex(e.first)
        self.__validateVertex(e.second)
        self.coords[e.first] = e.firstCoordinate
        self.coords[e.second] = e.secondCoordinate
        self.adj[e.first].append(e)
        self.adj[e.second].append(e)
        self.E += 1

    def shortestCylce(self):
        path = []
        foundstuff = self.V
        lastIndex = 0
        marked = [False] * self.V
        while foundstuff > 0:
            path.append([self.coords[lastIndex].x, self.coords[lastIndex].y])
            marked[lastIndex] = True
            foundstuff -= 1
            self.adj[lastIndex].sort(key=lambda x: x.weight)
            for edge in self.adj[lastIndex]:
                if not marked[edge.other(lastIndex)]:
                    lastIndex = edge.other(lastIndex)
                    break
        return path
