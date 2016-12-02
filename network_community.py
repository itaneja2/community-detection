import csv 
import sys 
import math 


community = {} #maps community number to node id
community_node_obj = {} #maps community number to node object 
nodes_community = {} #maps node to commmunity number 


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0): #parameters are vertices 
        self.adjacent[neighbor] = weight

    def update_edge_weight(self,neighbor,weight):
        print(self.adjacent[neighbor])
        print("here")
        self.adjacent[neighbor] += weight 

    def get_connections(self):
        return self.adjacent.keys()  #returns vertex objects 

    def get_degree(self):
        return len(self.adjacent.keys())

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):

        return self.adjacent[neighbor]

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node)
        if (node in self.vert_dict) == False:
            self.vert_dict[node] = new_vertex
        return new_vertex




    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)




    def get_vertices(self):
        return self.vert_dict.keys() #returns id of vertices 

    def get_vertices_obj(self):
        vertices = [] 
        for key in self.vert_dict.keys(): 
            vertices.append(self.vert_dict[key])
        return vertices 




def load_graph(g,filename):

    f = open(filename, 'rt')
    reader = csv.reader(f,dialect = 'excel-tab')

    count = 0 

    for row in reader:
        if count <= 1000: 
            print(row)
            g.add_edge(row[0],row[1],row[2])
            count += 1

def initialize_community(g):

    vertices = g.get_vertices() #returns the id of the vertices 
    vertices_obj = g.get_vertices_obj() 

    count = 0 
    for i in range(0,len(vertices)):
        v = vertices[i]
        v_obj = vertices_obj[i]
        community[count] = [v]
        community_node_obj[count] = [v_obj]  
        
        nodes_community[v_obj] = count 
        count += 1  

    print(community)

def sum_weights_community(community_num):


    vertices_obj = community_node_obj[community_num] #get all vertex objects inside community 

    sum_weights = 0 
    for i in range(0,len(vertices_obj)):
        for j in range(i+1,len(vertices_obj)):
                #check if edge exists 

                if vertices_obj[j] in vertices_obj[i].get_connections():
                    sum_weights += float(vertices_obj[i].get_weight(vertices_obj[j]))

    return float(sum_weights)

def sum_node_community(node,community_num):

    vertices_obj_community = community_node_obj[community_num]

    sum_node_weights = 0 
    for v in vertices_obj_community:
        if v in node.get_connections():
            sum_node_weights += float(node.get_weight(v))

    return float(sum_node_weights)


def get_edge_weights(g):

    #do a bfs 

    root = g.get_vertices_obj()[0]

    visited = {} 

    q = Queue()
    q.enqueue(root)

    total_edge_weight = 0 

    while q.size() > 0:

        curr = q.dequeue() 
        visited[curr] = True 

        for node in curr.get_connections():
            if (node in visited) == False:
                total_edge_weight += float(curr.get_weight(node))
                q.enqueue(node)

    return float(total_edge_weight)


def calc_modularity(node,community_to,g):

    community_curr = nodes_community[node]

    sum_inside_community = sum_weights_community(community_curr)
    sum_inside_other_community = sum_weights_community(community_to)

    degree = node.get_degree() 
    sum_node_other_community = sum_node_community(node,community_to)
    sum_weights_all = get_edge_weights(g)


    return calc_modularity_formula(sum_inside_community,sum_inside_other_community,degree,sum_node_other_community,sum_weights_all)

def calc_modularity_formula(sum_inside_community,sum_inside_other_community,degree,sum_node_other_community,sum_weights_all):

    return ( ( (sum_inside_community+2*sum_node_other_community)/(2*sum_weights_all) - math.pow( (sum_inside_other_community+degree)/(2*sum_weights_all),2 )  ) 
        - ( (sum_inside_community/2*sum_weights_all) - math.pow( (sum_inside_other_community)/(2*sum_weights_all),2 ) - math.pow( (degree)/(2*sum_weights_all),2 ) ) 
        )



def place_in_community(g):

    num_modularity_changes = 1

    while num_modularity_changes > 0:
        num_modularity_changes = 0 
        #print("here")
        #print(g.get_vertices_obj())
        #print("wut")

        for node in (g.get_vertices_obj()): 
            community_curr_node = {} 
            for neighbor in node.get_connections():
                community_neighbor = nodes_community[neighbor]
                community_curr_node[community_neighbor] = True #keys are communities of all neighbors 
            max_modularity = -1
            max_community = -1 

            curr_modularity = calc_modularity(node,nodes_community[node],g) #modularity in current community for this node 
            curr_community = nodes_community[node]
            changed = False 

            #print(community_curr_node)
            for key in community_curr_node: #all communities current node is connected to 
                #print(key)
                modularity = calc_modularity(node,key,g)
                if modularity > curr_modularity:
                    curr_modularity = modularity
                    curr_community = key 
                    changed = True 
                    num_modularity_changes += 1 

            if changed:
                print"ch"
                old_community = nodes_community[node]
                community[old_community].remove(node.get_id())
                community_node_obj[old_community].remove(node)

                community[curr_community].append(node.get_id())
                community_node_obj[curr_community].append(node) #add node to this community
                nodes_community[node] = curr_community
            print(num_modularity_changes)

            
        print"huH"
        print(num_modularity_changes)

            #remove 

def convert_community_graph():

    updated_graph = Graph() 

    for key in community:
        updated_graph.add_vertex(key)
        vertices_obj = community_node_obj[key] #get all vertices inside community

        #print(key)
        #print("w")
        #print(vertices_obj)

        sum_weights = 0 
        for i in range(0,len(vertices_obj)):
            for j in range(0,len(vertices_obj)):
                if i != j:
                    #check if edge exists 
                    if vertices_obj[j] in (vertices_obj[i].get_connections()):
                        weight = vertices_obj[i].get_weight(vertices_obj[j])
                        sum_weights += weight  
        #print(sum_weights)
        if sum_weights > 0: 
            updated_graph.add_edge(sum_weights,key,key) #add self loop 

    vertices = updated_graph.get_vertices() #get vertice id which in this case is the community number 
    #print(vertices)
    vertices_obj = updated_graph.get_vertices_obj() 
    #print(vertices_obj)
    #print("here")
    #print(vertices_obj[0].get_connections())
    #sys.exit()

    #add edges between communities 

    for i in range(0,len(vertices)):
        for j in range(i+1,len(vertices)):
            nodes_i = community_node_obj[vertices[i]] #nodes in community i 
            nodes_j = community_node_obj[vertices[j]]
            ##print(nodes_i)
            #print(nodes_j)
            #print(vertices[i])
            #print(vertices[j])
            #print(community_node_obj)
            for k in range(0,len(nodes_i)):
                for l in range(0,len(nodes_j)):
                    if nodes_j[l] in nodes_i[k].get_connections():
                        weight = nodes_i[k].get_weight(nodes_j[l])
                        #print(weight)
                        #print("lo")
                        #print float(vertices_obj[i].get_weight(vertices_obj[j]))
                        #print("hi")
                        #print float(vertices_obj[i].get_weight(vertices_obj[i]))
                        #w = float(vertices_obj[i].get_weight(vertices_obj[i]))
                        #if edge exists between vertices[i] and vertices[j] then udpate weight
                        #print(vertices_obj[i].get_connections()) 
                        if vertices_obj[j] in vertices_obj[i].get_connections():
                            vertices_obj[i].update_edge_weight(vertices_obj[j],weight)
                            vertices_obj[j].update_edge_weight(vertices_obj[i],weight)
                        else:
                            updated_graph.add_edge(weight,vertices[i],vertices[j]) #takes id of vertices 


    return updated_graph 









def main():

    g = Graph() 
    load_graph(g,"1_ppi_anonym_v2.txt")
    initialize_community(g)

    while (len(g.get_vertices()) >= 40):
        print(len(g.get_vertices()))
        place_in_community(g)
        g = convert_community_graph()
        print("iter")
        print(len(g.get_vertices()))
        

main() 