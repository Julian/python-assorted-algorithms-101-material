from collections import deque
from operator import itemgetter

class InvalidTree(Exception):
    pass

class BinaryTree(object):
    def __init__(self, root=None, left=None, right=None, leaf=False, **kwargs):
        """
        Basic binary tree (with insertion, no deletion).
        """
        self.root = root
        self.parent = None
        self._left = None
        self._right = None

        if not leaf:
            self.left = left
            self.right = right
        else:
            if left or right:
                raise InvalidTree("Leaves have no children!")

        # use kwargs to store additional data on the root node
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __iter__(self):
        """
        Does *in-order* iteration.
        """
        if self.left:
            for node in self.left:
                yield node
        yield self
        if self.right:
            for node in self.right:
                yield node

    def __eq__(self, other):
        return self.root == other

    def __nonzero__(self):
        return self.root is not None

    def __repr__(self):
        return "<Binary Tree: Node - {0}>".format(self)

    def __str__(self):
        return str(self.root or "Empty")

    def __int__(self):
        return int(self.root)

    def _insert(self, side, value):
        """
        This is just a convenient way to not have to write both an insert_left
        and insert_right function that do the same thing.
        """
        b_tree_value = BinaryTree(value, leaf=True)
        return self._attach(side, b_tree_value)

    def _attach(self, side, tree):
        current_value = getattr(self, side)

        if not current_value:
            setattr(self, side, tree)
        else:
            setattr(tree, side, current_value)
            setattr(self, side, tree)
            current_value.parent = tree
        tree.parent = self

    @property
    def height(self):
        if not self:
            return 0
        elif not self.left and not self.right:
            return 1
        else:
            return 1 + max(getattr(self.left, "height", 0),
                           getattr(self.right, "height", 0))

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        return self._insert("_left", value)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        return self._insert("_right", value)

    @property
    def leaves(self):
        return [node for node in self if not node.left and not node.right]

    def iter_in_order(self):
        """
        Does *in-order* iteration.
        """
        return iter(self)

    def iter_pre_order(self):
        yield self
        if self.left:
            for node in self.left.iter_pre_order():
                yield node
        if self.right:
            for node in self.right.iter_pre_order():
                yield node

    def iter_post_order(self):
        if self.left:
            for node in self.left.iter_post_order():
                yield node
        if self.right:
            for node in self.right.iter_post_order():
                yield node
        yield self

    def attach_left(self, tree):
        """
        Attach an existing tree to a node.
        """
        return self._attach("_left", tree)

    def attach_right(self, tree):
        return self._attach("_right", tree)

def count(text, sort=False, reverse=False):
    counted = ((letter, text.count(letter)) for letter in set(text))
    if sort:
        counted = sorted(counted, key=itemgetter(1), reverse=reverse)
    return counted

def get_huffman_tree(text, do_count=False):
    """
    O(n) Huffman coding implementation using two (de)queues.

    (Direct translation from algorithm to Python code.)
    """
    if do_count:
        text = count(text, sort=True)
    # construct a deque containing leaves out of the frequencies returned by
    # count. store the letter in an attr of each node
    initial_weights = deque([BinaryTree(l[1], leaf=True, letter=l[0])
                                        for l in text])
    combined_weights = deque()

    while len(initial_weights) + len(combined_weights) > 1:
        least_two_nodes = []
        # (for loop over range(2) = do this twice)
        for _ in range(2):
            if not initial_weights or not combined_weights:
                least_two_nodes.append(
                    (initial_weights or combined_weights).popleft())
            elif initial_weights[0].root <= combined_weights[0].root:
                least_two_nodes.append(initial_weights.popleft())
            else:
                least_two_nodes.append(combined_weights.popleft())
        left, right = least_two_nodes
        node = BinaryTree(left.root + right.root)
        node.attach_left(left)
        node.attach_right(right)
        combined_weights.append(node)
    root = (initial_weights or combined_weights).popleft()
    return root

def get_huffman_code(node):
    if not node.parent:
        return ""
    else:
        if node is node.parent.left:
            return get_huffman_code(node.parent) + "0"
        else:
            return get_huffman_code(node.parent) + "1"

if __name__ == "__main__":
    sample_data = "a" * 24 + "b" * 12 + "c" * 10 + "d" * 8 + "e" * 8
    print "Sample Huffman tree for: {0}".format(sorted(count(sample_data)))
    t = get_huffman_tree(sample_data)
    print [(x.letter, get_huffman_code(x)) for x in t.leaves]
