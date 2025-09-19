import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        print("simple equal")
        
        node = HTMLNode("tag","value",None,None)
        node2 = HTMLNode ("tag","value",None,None)
        self.assertEqual(node, node2)

    def test_prop1(self):
        print ("href")
        node = HTMLNode("Tag","value",None,{"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(),' href="https://www.google.com" target="_blank"')

    def test_prop2(self):
        print ("img")
        node = HTMLNode(None,None,None,{"src":"url/of/image.jpg", "alt": "Description of image"})
        self.assertEqual(node.props_to_html(), ' src="url/of/image.jpg" alt="Description of image"')

    def test_prop3(self):
        print ("props ne")
        node = HTMLNode("Tag","value",None,{"href": "https://www.google.com", "target": "_blank"})
        self.assertNotEqual(node.props_to_html(),' href="https://www.google.com"')

if __name__ == "__main__":
    unittest.main()
