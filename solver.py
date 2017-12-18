from inc.variable import *
from inc.propagation import *
from inc.backtracking import *


class Solver:

    def __init__(self, algo):
        self.algo = algo
        self.variables = {}
        self.constraints = {}
        self.propagation = Propagation()

    @staticmethod
    def table_from_exp(X, Y, exp):
        """
        Creates a table for two variables evaluating a boolean expression
        :param X: first variable of the constraint
        :param Y: second variable of the constraint
        :param exp: must be a STRING formatted as valid Python 3 boolean expression.
        Nota Bene:
        - address each variable with its name, so if the name of the first variable is "x"
            then use "x" inside the expression
        - all constants are allowed
        - all comparison operator are allowed (>, <, >=, <=, =, !=)
        - all aritmetic operators are allowed (+, -, *, /, %)
        - all python aritmetic function are allowed (e.g. "math.pow()", "math.floor()", etc...)
        - etc...
        :return: boolean matrix table
        """
        table = []
        if X.name in exp:
            exp = exp.replace(X.name, "x")
        if Y.name in exp:
            exp = exp.replace(Y.name, "y")
        for i in range(len(X.domain)):
            x = X.domain[i]
            table.append([])
            for j in range(len(Y.domain)):
                y = Y.domain[j]
                table[i].append(eval(exp))
        return table

    @staticmethod
    def table_from_set(X, Y, allowedValueSet):
        """
        Creates a table for two variables starting from pairs of allowed value
        :param X: first variable
        :param Y: second variable
        :param allowedValueSet: list of pairs of values (values must be in domains of variables)
        :return: boolean matrix table
        """
        table = []
        for i in range(len(X.domain)):
            x = X.domain[i]
            table.append([])
            for j in range(len(Y.domain)):
                y = Y.domain[j]
                table[i].append((x, y) in allowedValueSet)
        return table

    def add_variable(self, domain, name=""):
        v = Variable(domain, self.propagation, name)
        self.variables[v.name] = v
        return v.name

    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        return None

    def add_constraint(self, x_name, y_name, exp, name=""):
        x = self.variables[x_name]
        y = self.variables[y_name]
        c = self.algo(x, y, self.table_from_exp(x, y, exp), name)
        self.constraints[c.name] = c
        return c.name

    def add_custom_constraint(self, x_name, y_name, allowedValueSet, name=""):
        x = self.variables[x_name]
        y = self.variables[y_name]
        c = self.algo(x, y, self.table_from_set(x, y, allowedValueSet), name)
        self.constraints[c.name] = c
        return c.name

    def filter_domains(self):
        self.propagation.build_graph(list(self.constraints.values()))
        self.propagation.run()

    def solve(self):
        if not self.propagation.run():
            return []

        self.sort_variables()

        return self.backtracking([v.domain for v in self.variables])

    def sort_variables(self):
        var_domain_size = [len(x.domain) for x in self.variables]
        self.variables = [x for _, x in sorted(zip(var_domain_size, self.variables))]

    def backtracking(self, domains):
        for i in range(len(self.variables)):
            self.variables[i].domain = domains[i]

        """
        if all len(domains) == 1:
            # then is a full assignment A = (x1, x2, ..., xN) for the problem
            if accepted(A):
                return [A]
            else:
                # assignement is not valid
                return []
        else:
            # restrict one variable domain
            x <- first variable of which len(x.domain) > 1
            return 
        """

        if len(self.backtracking([v.domain for v in self.variables])) == 0:
            return []
        else:
            pass
