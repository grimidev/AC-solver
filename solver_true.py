import abc, math, numpy as np

id_counter = 0


class Variable:

    def __init__(self, domain):
        global id_counter
        self.domain = domain  # list of allowed values for this variable
        self.type = type(domain[0])
        self.delta = []
        self.id = id_counter
        id_counter += 1

    """
    Returns true if a is removed from domain.
    """

    def remove_value(self, a, P):
        if self.is_in_domain(a):
            self.domain.pop(self.domain.index(a))
            self.delta.append(a)
            P.enqueue(self)
            return True
        return False

    def is_in_domain(self, a):
        if a in self.domain:
            return True
        return False

    def delta_is_empty(self):
        return len(self.delta) == 0

    def reset_delta(self):
        self.delta = []


class Propagation:

    def __init__(self, constrains):
        self.queue = []  # contains constraints to parse
        self.graph = {}  # constraints' graph i.e. for each variable the set of constraints with regard to it

        for c in constrains:
            if c.x.id not in self.graph:
                self.graph[c.x.id] = []

            if c.y.id not in self.graph:
                self.graph[c.y.id] = []

            self.graph[c.x.id].append(c)
            self.graph[c.y.id].append(c)

    """
    Add constraint (x,y) into queue whether not present
    """

    def enqueue(self, vars):
        for x in vars:
            if x not in self.queue:
                self.queue.append(x)

    def dequeue(self):
        return self.queue.pop(0)

    def run(self):
        # before starting run() method, all variable must be enqueued by user
        # loop through all variables in queue
        while len(self.queue) > 0:
            x = self.dequeue()
            for c in self.graph[x.id]:
                if not c.filter_from(x, self):
                    return False
            x.reset_delta()
        return True


"""
exp must be a STRING formatted as an aritmetic valid expression in which:
- "x" stands for the first variable
- "y" stands for the second variable
- all constants are allowed
- all comparison operator are allowed (>, <, >=, <=, =, !=)
- all aritmetic operators are allowed (+, -, *, /, %)
- all python aritmetic function are allowed (e.g. "math.pow()", "math.floor()", etc...)
- other python functions, symbols, variables can potentially break the computation, so they're not allowed 
"""


def tableFromExp(X, Y, exp):
    table = []
    for i in range(len(X.domain)):
        x = X.domain[i]
        table.append([])
        for j in range(len(Y.domain)):
            y = Y.domain[j]
            table[i].append(eval(exp))
    return table


def tableFromSet(X, Y, allowedValueSet):
    table = []
    for i in range(len(X.domain)):
        x = X.domain[i]
        table.append([])
        for j in range(len(Y.domain)):
            y = Y.domain[j]
            table[i].append((x, y) in allowedValueSet)
    return table


class GraphTable:
    def __init__(self):
        self.struct = {}
        self.constrains = {}
        self.variables = []
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass


class Constraint:
    def __init__(self, x, y, table):
        self.x = x
        self.y = y
        self.table = {}
        for i in range(len(table)):
            for j in range(len(table[i])):
                if table[i][j]:
                    a = self.x.domain[i]
                    b = self.y.domain[j]
                    if not a in self.table:
                        self.table[a] = {}
                    self.table[a][b] = True

    def consistent(self, a, b):
        if a in self.table:
            if b in self.table[a]:
                return True
        return False

    @abc.abstractmethod
    def filter_from(self, var, P):
        pass


class AC3Constraint(Constraint):
    def __init__(self, x, y, table):
        Constraint.__init__(self, x, y, table)

    """
    Let x be the argument variable.
    Let y be the second variable with regards to the constraint.
    A constraint is a set of pairs (x,y).
    Let C(x,y) : D(x) x D(y) -> {True, False} be a function s.t.
        C(x,y) = True iff (x,y) is an allowed value for the constraint
        C(x,y) = False otherwise
    Then this method returns:
    - True if for all x, exists at least on y s.t. C(x,y) is true
    - False if exists at least one x s.t. for all y, C(x,y) == False
    """

    def filter_from(self, var, P):
        if var.id == self.x.id:
            main_var = self.y
            supp_var = self.x
        elif var.id == self.y.id:
            main_var = self.x
            supp_var = self.y
        else:
            raise Exception("Error in filter_from: filtering from a variable that doesn't belong to the constraint")

        value_to_pop = []

        for i in range(len(main_var.domain)):
            a = main_var.domain[i]
            found = False
            for j in range(len(supp_var.domain)):
                b = supp_var.domain[j]

                if main_var == self.x:
                    found = self.consistent(a, b)
                else:
                    found = self.consistent(b, a)

                if found:
                    break
            if not found:
                value_to_pop.append(a)

        for val in value_to_pop:
            main_var.remove_value(val, P)

        return len(main_var.domain) > 0


class AC4Constraint(Constraint):
    def __init__(self, x, y, table):
        Constraint.__init__(self, x, y, table)

        self.S = {
            "x": {},
            "y": {}
        }

        for a in list(self.table.keys()):
            for b in list(self.table[a].keys()):
                self.S["x"][a].append(b)
                self.S["y"][b].append(a)

    """
    Let x be the argument variable.
    Let y be the second variable with regards to the constraint.
    A constraint is a set of pairs (x,y).
    Let C(x,y) : D(x) x D(y) -> {True, False} be a function s.t.
        C(x,y) = True iff (x,y) is an allowed value for the constraint
        C(x,y) = False otherwise
    Then this method returns:
    - True if for all x, exists at least on y s.t. C(x,y) is true
    - False if exists at least one x s.t. for all y, C(x,y) == False
    """

    def filter_from(self, var, P):
        ret = True

        if var.id == self.x.id:
            considered_var = self.x
            considered_var.tag = "x"
            other_var = self.y
            other_var.tag = "y"
        elif var.id == self.y.id:
            considered_var = self.y
            considered_var.tag = "y"
            other_var = self.x
            other_var.tag = "x"
        else:
            raise Exception("Error in filter_from: filtering from a variable that doesn't belong to the constraint")

        domain_index_to_pop = []

        for a in considered_var.delta:
            for b in self.S[considered_var.tag][a]:
                self.S[other_var.tag][b].remove(a)
                if len(self.S[other_var.tag][b]):
                    del self.S[other_var.tag][b]
                    domain_index_to_pop.append(other_var.domain.index(b))

        domain_index_to_pop.sort()
        i = 0
        for index in domain_index_to_pop:
            considered_var.domain.pop(index - i)
            i += 1

        for i in range(len(considered_var.domain)):
            a = considered_var.domain[i]
            found = False
            for j in range(len(other_var.domain)):
                b = other_var.domain[j]
                if self.consistent(a, b):
                    found = True
                    break
            if not found:
                domain_index_to_pop.append(i)
                ret = False
        return ret


if __name__ == "__main__":
    """
    a = Variable(list(range(0, 10)))
    b = Variable(list(range(0, 10)))
    c = Variable(list(range(0, 10)))
    Cab = AC3Constraint(a, b, tableFromExp(a, b, "x + y > 12"))
    Cbc = AC3Constraint(b, c, tableFromExp(b, c, "x + y < 7"))
    P = Propagation(Cab, Cbc)
    P.enqueue(a,b,c)
    P.run()
    print(a.domain)
    print(b.domain)
    print(c.domain)
    """

    a = Variable(list(range(0, 4)))
    b = Variable(list(range(0, 4)))
    c = Variable(list(range(0, 4)))
    d = Variable(list(range(0, 4)))

    Vs = [a, b, c, d]
    Cs = []

    for i in range(len(Vs) - 1):
        for j in range(i + 1, len(Vs)):
            Cs.append(AC3Constraint(Vs[i], Vs[j], tableFromExp(Vs[i], Vs[j], "x != y")))
            Cs.append(AC3Constraint(Vs[i], Vs[j], tableFromExp(Vs[i], Vs[j], "x != y - " + str(j - i))))
            Cs.append(AC3Constraint(Vs[i], Vs[j], tableFromExp(Vs[i], Vs[j], "x != y + " + str(j - i))))

    P = Propagation(Cs)
    P.enqueue(Vs)
    P.run()
    print(a.domain)
    print(b.domain)
    print(c.domain)
    print(d.domain)