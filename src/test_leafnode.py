import unittest

from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        print ('a')
        node = LeafNode("p","Hello world!")
        self.assertEqual(node.to_html(), "<p>Hello world!</p>")


    def test_leaf_to_html_a(self):
        print ('p')
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

if __name__ == "__main__":
    unittest.main()