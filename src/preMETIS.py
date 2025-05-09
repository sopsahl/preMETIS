import networkx as nx

class preMETIS:

    def transform(self):
        raise NotImplementedError

    def __init__(self, graph: nx.Graph):
        
        self.total_nodes = graph.number_of_nodes()
        self.total_edges = graph.number_of_edges()

        self.graph = graph.copy()
        
        self.reductions = {
            'simplicial_reduction' : 0,
            'indistinguishable_reduction' : 0,
            'twin_reduction' : 0,
            'path_compression' : 0,
            'degree_2_elimination' : 0,
            'triangle_contraction' : 0
        }

        self.operations = {
            'simplicial_reduction' : 0,
            'indistinguishable_reduction' : 0,
            'twin_reduction' : 0,
            'path_compression' : 0,
            'degree_2_elimination' : 0,
            'triangle_contraction' : 0
        }


        self.reduction_mapping = {}
        self.path_compression_nodes = {}

        self.ordering = []

        # Run the reductions specified in self.transform()
        self.transform()


    def eliminate_node(self, node, func):
        '''
        This removes a node from the graph and adds it to the ordering
        O(deg(v)) cost
        '''
        self.operations[func] += self.graph.degree(node) # cost of popping a node
        self.reductions[func] += 1

        self.graph.remove_node(node)
        self.ordering.append(node)


    def contract_nodes(self, nodes, func):
        '''
        This reduces a set of nodes into 1
        O(k * deg(v)) where k is number of nodes
        '''

        self.reductions[func] += len(nodes) - 1 # number of reductions

        new_node = ""
        neighbors = set()
        for node in nodes:
            new_node += f"_{node}"
            neighbors |= set(self.graph.neighbors(node))

            self.operations[func] += self.graph.degree(node) # cost of checking neighbors and popping edge
            self.graph.remove_node(node)

        neighbors -= set(nodes)
        self.graph.add_node(new_node)
        for n in neighbors:
            self.graph.add_edge(new_node, n)
        self.operations[func] += self.graph.degree(new_node) # cost of adding new_node


        self.reduction_mapping[new_node] = nodes
        return new_node
        

    def simplicial_reduction(self, degree_threshold=-1):
        '''
        Removes nodes with a clique neigborhood
        Iterates through all nodes once, so misses potentially created cliques
        O(n * d^2), where d is the degree threshold
        '''
        removed = set()
        for node in list(self.graph.nodes()):

            if degree_threshold != -1 and self.graph.degree(node) > degree_threshold:
                continue

            neighbors = self.graph.neighbors(node)
            deg = len(neighbors)

            self.operations['simplicial_reduction'] += deg * (deg - 1) // 2
                            
            if self.graph.subgraph(neighbors).number_of_edges() == deg * (deg - 1) // 2:
                removed.add(node)
                self.eliminate_node(node, 'simplicial_reduction')

    def indistinguishable_reduction(self):
        '''
        Reduces node pairs with an identical closed neighborhood
        O(m + m*deg(v))
        '''
        hashes = { 
            node : sum(hash(n) for n in self.graph.neighbors(node) | {node})
            for node in self.graph.nodes()
            }
        
        self.operations['indistinguishable_reduction'] += 2*len(self.graph.edges) # cost of creating hashes
        
        edges = list(self.graph.edges())
        reduced = {}

        for (u, v) in edges:
           
            if hashes[u] == hashes[v]: # worth comparing now
                u = self._find_lowest_reduction(reduced, u)
                v = self._find_lowest_reduction(reduced, v)
                
                self.operations['indistinguishable_reduction'] += max(self.graph.degree(u), self.graph.degree(v)) # cost of comparing neighbors
                
                if set(self.graph.neighbors(u)) | {u} == set(self.graph.neighbors(v)) | {v}:
                    new_node = self.contract_nodes([u, v], "indistinguishable_reduction")
                    reduced[u] = new_node
                    reduced[v] = new_node
                
            else: self.operations['indistinguishable_reduction'] += 1 # cost of iterating


    def twin_reduction(self):
        '''
        Reduces node pairs with an identical open neighborhood
        O(m + m*deg(v))
        '''
        hashes = { 
            node : sum(hash(n) for n in self.graph.neighbors(node))
            for node in self.graph.nodes()
            }
        
        self.operations['twin_reduction'] += 2*len(self.graph.edges) # cost of creating hashes
        
        edges = list(self.graph.edges())
        reduced = {}

        for (u, v) in edges:
           
            if hashes[u] == hashes[v]: # worth comparing now
                u = self._find_lowest_reduction(reduced, u)
                v = self._find_lowest_reduction(reduced, v)
                
                self.operations['twin_reduction'] += max(self.graph.degree(u), self.graph.degree(v)) # cost of comparing neighbors
                
                if set(self.graph.neighbors(u)) == set(self.graph.neighbors(v)):
                    new_node = self.contract_nodes([u, v], "twin_reduction")
                    reduced[u] = new_node
                    reduced[v] = new_node
                
            else: self.operations['twin_reduction'] += 1 # cost of iterating

    def path_compression(self):
        '''
        Reduces all paths of degree-2 nodes to one node
        O(n*deg(v))
        '''

        self.operations['path_compression'] += self.graph.number_of_nodes() # cost of iterating through nodes
        
        reduced = set()
        for node in list(self.graph.nodes()):
            if node in reduced: # already compressed
                continue
            
            if self.graph.degree(node) != 2:
                continue

            to_reduce = [node]

            neighbors = list(self.graph.neighbors(node))
            u, v = neighbors[0], neighbors[1]

            while True: # looks for all elements of degree-2 in the path
                if u in to_reduce:
                    u = None # for cycles
                    break
                if self.graph.degree(u) != 2:
                    break

                to_reduce.append(u)
                neighbors = list(self.graph.neighbors(u))
                u = neighbors[0] if neighbors[1] in to_reduce else neighbors[1]
                
            to_reduce = to_reduce[::-1] # reverse to compute the other side now
            while True:
                if v in to_reduce:
                    v = None # for cycles
                    break
                if self.graph.degree(v) != 2:
                    break

                to_reduce.append(v)
                neighbors = list(self.graph.neighbors(v))
                v = neighbors[0] if neighbors[1] in to_reduce else neighbors[1]

            if len(to_reduce) == 1:
                continue

            reduced.update(set(to_reduce)) 
            new_node = self.contract_nodes(to_reduce, 'path_compression')
            self.path_compression_nodes[new_node] = (u, v) # for ordering

    def degree_2_elimination(self):
        '''
        Eliminates all degree-2 nodes from the graph 
        This is an approximate reduction
        O(n) for iterating through the nodes
        '''

        self.operations['degree_2_elimination'] += self.graph.number_of_nodes() # cost of iterating through nodes

        for node in list(self.graph.nodes()):
            if self.graph.degree(node) == 2:
                neighbors = list(self.graph.neighbors(node))
                if not self.graph.has_edge(neighbors[0], neighbors[1]):
                    self.graph.add_edge(neighbors[0], neighbors[1])
                self.eliminate_node(node, 'degree_2_elimination')

    def triangle_contraction(self):
        '''
        Reduces all degree-3 neighbors
        This is an approximate reduction
        O(m) for iterating through all the edges
        '''


        visited = {}
        
        for node in list(self.graph.nodes()):

            if node in visited or self.graph.degree(node) != 3: continue


            to_reduce = []
            stack = [node]

            while stack:
                x = stack.pop()
                if x in visited or self.graph.degree(x) != 3:
                    continue

                visited.add(x)
                to_reduce.append(x)
                neighbors = set(self.graph.neighbors(x))

                self.operations['triangle_contraction'] += 3 

                for y in neighbors:
                    if y in visited or self.graph.degree(y) != 3:
                        continue
                    common_neighbors = neighbors & set(self.graph.neighbors(y))
                    if len(common_neighbors) >= 1:
                        visited.add(y)
                        to_reduce.append(y)
                        for a in common_neighbors:
                            for z in self.graph.neighbors(y):
                                self.operations['triangle_contraction'] += 1
                                if z in visited or z in to_reduce:
                                    continue
                                if self.graph.degree(z) == 3 and a in self.graph.neighbors(z):
                                    stack.append(z) # recurse on z
                                

            if len(to_reduce) == 1:
                continue

            self.contract_nodes(to_reduce, 'triangle_contraction')

    def get_ordering(self, metis_ordering, idx_mapping):
        '''
        Returns the final elimination ordering for the graph
        '''
        final_ordering = self.ordering.copy()
        
        for node_idx in metis_ordering:
            final_ordering += self._get_node_reduction(idx_mapping[node_idx], final_ordering)

        return final_ordering
    
    def _get_node_reduction(self, node, final_ordering):

        if node in self.reduction_mapping: # it was reduced
            ordering = []
            
            for child in self._node_reduction_order(node, final_ordering):
                ordering += self._get_node_reduction(child)
            return ordering
        
        return [node]
    
    def _node_reduction_order(self, node, final_ordering):
        nodes = self.reduction_mapping[node]
        if node in self.path_compression_nodes:
            return nodes if self.path_compression_nodes[node][1] is None \
                or self._get_node_reduction(self.path_compression_nodes[node][1])[0] in final_ordering \
                else nodes[::-1]
        return nodes

    def __repr__(self):
        return self.__class__.__name__
    
    def total_reductions(self):
        return sum(self.reductions.values())

    def total_operations(self):
        return sum(self.operations.values())

    def _find_lowest_reduction(self, reduced_set, node):
        while True:
            if node in reduced_set: 
                node = reduced_set[node]
                continue
            return node