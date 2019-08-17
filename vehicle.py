class Vehicle:
    def __init__(self, route=[0], weight=0, cost=0):
        self.route = route
        self.weight = weight
        self.cost = cost
        
    def add_route(self, b):
        if self.route[-1] == b[0]:
            self.route.append(b[1])
        else:
            self.route.append(b[0])
    
    def add_weight(self, weight):
        self.weight+=weight
        
    def add_cost(self, cost):
        self.cost+=cost
