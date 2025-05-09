import networkx as nx
import pymetis

class preMETIS:
    def __init__(self, graph: nx.Graph, degree_threshold=-1):
        
        self.original_graph = graph.copy()
        self.graph = graph

        self.degree_threshold = degree_threshold
        
        self.reductions = {
            'simplical_reduction' : 0,
            'indistinguishable_reduction' : 0,
            'twin_reduction' : 0
        }

        self.ordering = []

        self.operations = {
            'simplical_reduction' : 0,
            'indistinguishable_reduction' : 0,
            'twin_reduction' : 0
        }


    def eliminate_node(self, node, func):
        '''
        This removes a node from the graph and adds it to the ordering
        O(deg(v)) cost
        '''
        self.operations[func] += self.graph.degree(node) # cost of popping a node
        self.reductions[func] += 1

        self.graph.remove_node(node)
        self.ordering.append(node)


    def reduce_nodes(self, nodes, func, save_operations=False):
        new_node = "reduced"
        union = set()
        for node in nodes:
            new_node += f"_{node}"
            union |= set(self.graph.neighbors(node))

        if operations: # if not indistinguishible or twin reduction
            self.operations += 
        
        self.graph.add_node(new_node)

        union = set()
        

        neighbor_union = set(self.graph.neighbors(u)) | set(self.graph.neighbors(v)) | set(self.graph.neighbors(node))
        neighbor_union -= {u, v, node}
        for n in neighbor_union:
            self.graph.add_edge(new_node, n)
        return self.remove_node([u, v, node], depth + 1, 'triangle_contraction')

    def simplical_reduction(self, degree_threshold=-1):
        '''
        Removes nodes with a clique neigborhood
        Iterates through all nodes once, so avoids potentially created cliques
        O(n * d^2), where d is the degree threshold
        '''
        removed = set()
        for node in list(self.graph.nodes()):

            if degree_threshold != -1 and self.graph.degree(node) > degree_threshold:
                continue

            neighbors = list(self.graph.neighbors(node))
            is_clique = True

            for i, u in enumerate(neighbors):
                if u in removed:
                    continue
                for v in neighbors[i+1:]:
                    self.operations['simplical_reduction'] += 1
                    if v not in removed and not self.graph.has_edge(u, v):
                        is_clique = False
                        break

                if not is_clique:
                    break
                            
            if is_clique:
                removed.add(node)
                self.eliminate_node(node, 'simplical_reduction')

    def indistinguishable_reduction(self, depth=0):
        hashes = { 
            node : sum((int) neighbor for neighbor in self.graph.neighbors(node))
            for node in self.graph.nodes()
                  
            }

                
        self.operations += len(self.graph.edges) # cost of creating hashes

        for u, v in self.graph.edges:
            if self.graph.neighbors(u) | {u} == self.graph.neighbors(v) | {v}:
                self.remove_node([node], depth + 1, 'indistinguishable_reduction')
        if neighbors in twins:
            return self.remove_node([node], depth + 1, 'indistinguishable_reduction')
        twins[node] = node

    def twin_reduction(self, depth=0):
        twins = {}
        for node in list(self.graph.nodes()):
            neighbors = frozenset(self.graph.neighbors(node))
            if neighbors in twins:
                return self.remove_node([node], depth + 1, 'twin_reduction')
            twins[neighbors] = node

    def path_compression(self, depth=0):
        for node in list(self.graph.nodes()):
            if self.graph.degree(node) != 2:
                continue
            neighbors = list(self.graph.neighbors(node))
            if self.graph.has_edge(neighbors[0], neighbors[1]):
                continue
            self.graph.add_edge(neighbors[0], neighbors[1])
            return self.remove_node([node], depth + 1, 'path_compression')

    def degree_2_elimination(self, depth=0):
        for node in list(self.graph.nodes()):
            if self.graph.degree(node) == 2:
                neighbors = list(self.graph.neighbors(node))
                if not self.graph.has_edge(neighbors[0], neighbors[1]):
                    self.graph.add_edge(neighbors[0], neighbors[1])
                return self.remove_node([node], depth + 1, 'degree_2_elimination')

    def triangle_contraction(self, depth=0):
        
        for node in list(self.graph.nodes()):
            neighbors = list(self.graph.neighbors(node))
            if len(neighbors) < 2:
                continue
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u, v = neighbors[i], neighbors[j]
                    if self.graph.has_edge(u, v):
                        # Contract triangle into a new node
                        new_node = f"tri_{u}_{v}_{node}"
                        self.graph.add_node(new_node)
                        neighbor_union = set(self.graph.neighbors(u)) | set(self.graph.neighbors(v)) | set(self.graph.neighbors(node))
                        neighbor_union -= {u, v, node}
                        for n in neighbor_union:
                            self.graph.add_edge(new_node, n)
                        return self.remove_node([u, v, node], depth + 1, 'triangle_contraction')

    def summary(self):
        return {
            'original_nodes': self.original_graph.number_of_nodes(),
            'reduced_nodes': self.graph.number_of_nodes(),
            'reduction_steps': self.reductions
        }
