import json

class TriangleTree:
  def __init__(self):
    self.children = [None, None, None]
    self.lit = [False, False]
    self.inner_trim = 0
    self.outer_trim = [0, 0]
  
  def __str__(self):
    return self.show('*', 0)
  
  def show(self, k, level):
    text = level*' ' + '{} [{}, {}, {}]'.format(k, self.lit, self.outer_trim, self.inner_trim)
    if hasattr(self, 'index') and self.index != None:
      text += ' #' + str(self.index)
    for k in range(3):
      if self.children[k] != None:
        text += '\n' + self.children[k].show(k, level+1)
    return text
  
  # store the given coloring data at the given address, creating any nodes on
  # the way to the address that don't exist already. to store data for both
  # sides at once, set `side` to None and pass length-2 tuples or lists for
  # `lit` and `outer_trim`
  def store(self, address, side, lit, outer_trim, inner_trim):
    if address == []:
      if side == None:
        for side in range(2):
          if lit[side] != None: self.lit[side] = lit[side]
          if outer_trim[side] != None: self.outer_trim[side] = outer_trim[side]
          if inner_trim != None: self.inner_trim = inner_trim
      else:
        if lit != None: self.lit[side] = lit
        if outer_trim != None: self.outer_trim[side] = outer_trim
        if inner_trim != None: self.inner_trim = inner_trim
    else:
      k = address[0]
      if self.children[k] == None: self.children[k] = TriangleTree()
      self.children[k].store(address[1:], side, lit, outer_trim, inner_trim)
  
  def drop(self, address):
    if address == []:
      # turn off the lights
      self.lit[:] = (False, False)
      self.outer_trim[:] = (0, 0)
      self.inner_trim = 0
      
      # tell the node above whether this node can be severed from the tree
      return all(child == None for child in self.children)
    else:
      k = address[0]
      if self.children[k] == None:
        # there's nothing stored at the address provided, so tell the nodes
        # above to do nothing
        return False
      elif self.children[k].drop(address[1:]):
        # child `k` can be severed from the tree
        self.children[k] = None
        if (
          self.children[(k+1)%3] == None
          and self.children[(k+2)%3] == None
          and not any(self.lit)
          and not any(self.outer_trim)
          and not self.inner_trim
        ):
          # this node can be severed too
          return True
  
  # list the tree's nodes, depth first, and give each node an `index` attribute
  # that hold its list index plus the given offset. if `nodes` is provided,
  # append the list of nodes to it. otherwise, return the list
  def flatten(self, offset=0, nodes=None):
    # start a node list, if none is provided
    init = nodes == None
    if init: nodes = []
    
    # list this node
    self.index = len(nodes) + offset
    nodes.append(self)
    
    for k in range(3):
      if self.children[k] != None:
        self.children[k].flatten(offset, nodes)
    
    # if the node list wasn't passed to us, return it
    if init: return nodes
  
  def dump(self, fp, **kwargs):
    json.dump(self, fp, default=lambda obj: obj.__dict__, **kwargs)
  
  def dumps(self, **kwargs):
    return json.dumps(self, default=lambda obj: obj.__dict__, **kwargs)
  
  # for JSON deserialization, build a TriangleTree recursively from nested dicts
  #
  #   StackOverflow user martineau
  #   https://stackoverflow.com/a/23597335/1644283
  #
  @staticmethod
  def from_dict(data, legacy=False):
    tree = TriangleTree()
    for k in range(3):
      if child := data['children'][k]:
        tree.children[k] = TriangleTree.from_dict(child, legacy)
    tree.lit = data['lit']
    tree.outer_trim = data['outer_trim']
    tree.inner_trim = data['inner_trim']
    return tree
  
  @staticmethod
  def load(fp, legacy=False, **kwargs):
    return TriangleTree.from_dict(json.load(fp, **kwargs), legacy)
  
  @staticmethod
  def loads(s, legacy=False, **kwargs):
    return TriangleTree.from_dict(json.loads(s, **kwargs), legacy)

def tree_test():
  tree = TriangleTree()
  tree.store([0, 0, 0], None, (True, True), (9000, 5555), 7)
  tree.store([0, 1], 0, True, 901, 7)
  tree.store([0, 1, 1], 1, True, 9011, None)
  tree.store([2, 0, 1], 0, False, 9201, None)
  tree.store([2], None, (False, False), (92, 55), None)
  
  nodes = tree.flatten()
  print(tree)
  print()
  for node in nodes:
    print('[{}, {}, {}]'.format(node.lit, node.outer_trim, node.inner_trim))
  print()
  
  for address in [[0, 1], [0, 0, 0], [0, 1, 1], [2, 0], [2, 0, 1]]:
    tree.drop(address)
    print('drop ' + ''.join(map(str, address)))
    print(tree)
    print()

def root_drop_test():
  tree = TriangleTree()
  tree.store([], 0, True, 99, None)
  print(tree)
  print()
  
  tree.drop([])
  print(tree)
  print()
