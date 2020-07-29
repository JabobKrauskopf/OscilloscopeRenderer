from classes.EdgeWeightedGraph import EdgeWeightedGraph, Edge, Coordinate
import numpy as np
import json
import progressbar

with open('data.json', 'r') as f:
    data = json.loads(f.read())

sizeX = data['sizeX']
sizeY = data['sizeY']

pathArray = {'sizeX': sizeX, 'sizeY': sizeY, 'frames': []}


def getDistance(c1, c2):
    tmp = c1 - c2
    sumSquared = np.dot(tmp.T, tmp)
    return float(np.sqrt(sumSquared))


barfirst = progressbar.ProgressBar(maxval=len(data['frames']), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
barfirst.start()
for test in range(len(data['frames'])):
    frame = data['frames'][test]
    if len(frame) > 0:
        graph = EdgeWeightedGraph(2*len(frame), sizeX, sizeY)
        for index in range(0, len(frame)):
            for index2 in range(0, len(frame)):
                if index == index2:
                    graph.addEdge(Edge(index*2, index*2 + 1, 0, Coordinate(frame[index][0][0], frame[index][0][1]), Coordinate(frame[index][1][0], frame[index][1][1])))
                else:
                    angleWeight = np.absolute(frame[index][2] - frame[index2][2]) * 1.5
                    weight1 = getDistance(np.array(frame[index][0]), np.array(frame[index2][0]))
                    graph.addEdge(Edge(index*2, index2*2, angleWeight + weight1, Coordinate(frame[index][0][0], frame[index][0][1]), Coordinate(frame[index2][0][0], frame[index2][0][1])))
                    weight2 = getDistance(np.array(frame[index][0]), np.array(frame[index2][1]))
                    graph.addEdge(Edge(index*2, index2*2 + 1, angleWeight + weight2, Coordinate(frame[index][0][0], frame[index][0][1]), Coordinate(frame[index2][1][0], frame[index2][1][1])))
                    weight3 = getDistance(np.array(frame[index][1]), np.array(frame[index2][0]))
                    graph.addEdge(Edge(index*2 + 1, index2*2, angleWeight + weight3, Coordinate(frame[index][1][0], frame[index][1][1]), Coordinate(frame[index2][0][0], frame[index2][0][1])))
                    weight4 = getDistance(np.array(frame[index][1]), np.array(frame[index2][1]))
                    graph.addEdge(Edge(index*2 + 1, index2*2 + 1, angleWeight + weight4, Coordinate(frame[index][1][0], frame[index][1][1]), Coordinate(frame[index2][1][0], frame[index2][1][1])))
        pathArray['frames'].append(graph.shortestCylce())
    barfirst.update(test)
barfirst.finish()

with open('data2.json', 'w') as f:
    json.dump(pathArray, f)
