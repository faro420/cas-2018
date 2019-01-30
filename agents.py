import gevent
from gevent.queue import Queue
from gevent import Greenlet
import time
from random import randint
import networkx as nx
import matplotlib.pyplot as plt
import math


class Actor(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def receive(self, message):
        """
        Define in your subclass.
        """
        raise NotImplemented()

    def _run(self):
        self.running = True
        while self.running:
            message = self.inbox.get()
            self.receive(message)

#=============================================================
# class Overmind(Actor):
# 
#     def receive(self, message):
#         if message == 'continue':
#             for i in range(numOfActors):
#                 actors[i].inbox.put('seek')         
#             gevent.sleep(0)
#             self.inbox.put('continue')
#         elif message == 'stop':
#             print("stop")


#=============================================================
class Drone(Actor):

    def __init__(self, position):
        super(Drone, self).__init__()
        self.pos = position
        self.neighbours = []
        self.wealth = [randint(999, 1000), randint(1, 1000)]

    def receive(self, message):
        strings = message.split()
        buffer = [0] * 2
        if strings[0] == 'init':
            self.initializer()
            gevent.sleep(0)  
            return True 
        if strings[0] == 'seek':
            x = randint(0, len(self.neighbours) - 1)
            string = 'recon ' + str(self.wealth[0]) + ' ' + str(self.wealth[1]) + ' ' + str(self.pos)
            actors[self.neighbours[x]].inbox.put(string)
            return True
        elif strings[0] == 'recon':
            buffer[0] = int(strings[1])
            buffer[1] = int(strings[2])
            vermA = self.vermoegen(self.wealth, buffer)
            vermB = self.vermoegen(buffer, self.wealth)
            ow = self.Zow(self.wealth, buffer) 
            Zv = randint(0, int(vermA + vermB))
            if Zv >= vermA:
                p = randint(0, 100) / 100.0
                z = randint(0, len(self.neighbours) - 1)
                x = int(strings[3])
                if p < ow:
                    string = 'add ' + ' ' + str(z)
                    try:
                        G.add_edge(x, z)
                    except nx.exception.NetworkXError:
                        pass
                    actors[x].inbox.put(string)
                    string = 'add ' + ' ' + str(x)
                    actors[z].inbox.put(string)
                elif p > ow:
                    string = 'destroy ' + ' ' + str(z)
                    try:
                        G.remove_edge(x, z)
                    except nx.exception.NetworkXError:
                        pass
                    actors[x].inbox.put(string)
                    string = 'destroy ' + ' ' + str(x)
                    actors[z].inbox.put(string)
        elif strings[0] == 'add':
            z = int(strings[1])
            if self.neighbours.__contains__(z) != True and z != self.pos:
                self.neighbours.append(z)
        elif strings[0] == 'destroy':
            z = int(strings[1])
            if self.neighbours.__contains__(z) == True and z != self.pos:
                self.neighbours.remove(z)
        else:
            print("Error!")

#==============================================================
    # initializes vertices and edges of an actor
    def initializer(self):
        if self.pos == 0:
            self.neighbours.append(1)
            G.add_edge(0, 1)
            self.neighbours.append(numOfActors - 1)
            G.add_edge(0, numOfActors - 1)
            return True
        elif self.pos == numOfActors - 1:
            self.neighbours.append(0)
            G.add_edge(0, numOfActors - 1)
            self.neighbours.append(numOfActors - 2)
            G.add_edge(numOfActors - 2, numOfActors - 1)
            return True
        else:
            self.neighbours.append(self.pos - 1)
            G.add_edge(self.pos - 1, self.pos)
            self.neighbours.append(self.pos + 1)
            G.add_edge(self.pos, self.pos + 1)
            return True
        print(self.neighbours)   

#==============================================================
    # calculates Orientierungswert
    def Zow(self, listA, listB):
        result = 0
        normA = 0
        normB = 0
        # skalarprodukt
        for i in range(len(listA)):
            result = result + listA[i] * listB[i]
            normA = normA + listA[i] * listA[i]
            normB = normB + listB[i] * listB[i]
        normA = math.sqrt(normA)
        normB = math.sqrt(normB)
        result = result / float(normA * normB)
        return result

    # calculates wealth
    def vermoegen(self, listA, listB):
        result = 0
        # skalarprodukt
        for i in range(len(listA)):
            result = result + listA[i] * 0.5 * (listA[i] + listB[i])
        return result

        
print("Start : %s" % time.ctime())
G = nx.Graph()
numOfActors = 100
numOfRuns = 98
actors = []
for i in range(numOfActors):
    actors.append(Drone(i))
    G.add_node(i)
    actors[i].start()
    actors[i].inbox.put('init')
#===================================
# simulation starts now
for j in range(numOfRuns):
    for i in range(numOfActors):
        actors[i].inbox.put('seek')         
        gevent.sleep(0)
# simulation ends here
#===================================
try:
    gevent.joinall(actors)
except gevent.exceptions.LoopExit:
    print("Yay baby!")
averageN = 0
edge_list = []
for i in range(numOfActors):
    edge_list.append(len(actors[i].neighbours))
    averageN = averageN + edge_list[i]
edge_list.sort()
index = int(numOfActors / 2)
median = (edge_list[index - 1] + edge_list[index]) / 2.0
print("average number of edges: " + str(averageN / float(numOfActors)))
print("min: " + str(edge_list[0]))
print("max: " + str(edge_list[numOfActors - 1]))
print("median: " + str(median))
print("End : %s" % time.ctime())
nx.draw_circular(G)
plt.show()
# plt.plot([1,2,3,4], [1,4,9,16])
# plt.axis([0, 6, 0, 20])
# plt.show()
