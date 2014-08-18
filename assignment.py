from pulp import *

def expr(s, vars):
	return fd.make_expression( vars, s % vars )

def var(p, t):
	v = "x_" + str(p) + "_" + str(t)
	if not v in var.vars:
		var.vars[v] = LpVariable(v, cat = "Binary")
		var.info[v] = (p, t)
	return var.vars[v]
var.vars = {}
var.info = {}

def assign(persons, tasks):
	prob = LpProblem()
	
	pids = range(len(persons))
	tids = range(len(tasks))
	obj = LpAffineExpression()
	
	for p in pids:
		constraint = 0
		for t in tids:
			# no => bind variable to zero
			if persons[p][1][t] == "n":
				prob += var(p,t) == 0
			# yes => add to constraint and objective
			if persons[p][1][t] == "y":
				constraint += var(p,t)
				obj += var(p,t)
			# maybe => add to constraint and objective (with lower priority)
			if persons[p][1][t] == "m":
				constraint += var(p,t)
				obj += 2*var(p,t)
		prob += constraint == 1
	
	for t in tids:
		constraint = 0
		for p in pids:
			if persons[p][1][t] in ["y","m"]:
				constraint += var(p,t)
		prob += constraint <= 1
	
	prob += obj
	status = prob.solve(GLPK(msg = False))
	enabled = []
	for v in var.vars:
		if value(var.vars[v]) == 1:
			(p,t) = var.info[v]
			enabled.append( (persons[p][0], tasks[t]) )
	return (status, enabled, lambda p,t: (p,t) in enabled)
