import unittest

from textnode import TextNode, TextType
from main import *

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        print("simple equal")
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode ("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ne(self):
        print ("simple ne")
        node = TextNode ("This", TextType.TEXT)
        node2 = TextNode ("this", TextType.TEXT)
        self.assertNotEqual(node, node2)

    def test_ulr(self):
        print("url")
        node = TextNode("This", TextType.LINK, 'url')
        node2 = TextNode("This", TextType.LINK)
        self.assertNotEqual(node,node2)
    
    def test_text(self):
        print ("text to html")
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_img(self):
        print ("img to html")
        node = TextNode("blabla",TextType.IMAGE,"whatever.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value,None)
        self.assertEqual(html_node.props, {"src":"whatever.jpg","alt":"blabla"})

    def test_link(self):
        print ("img to html")
        node = TextNode (text='blah', text_type=TextType.LINK,url="www.google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag,"a")
        self.assertEqual(html_node.value, "blah")
        self.assertEqual(html_node.props, {"href":"www.google.com"})

    def test_split(self):
        print ("split test1")
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes,[TextNode("This is text with a ", TextType.TEXT),
                                    TextNode("code block", TextType.CODE),
                                    TextNode(" word", TextType.TEXT),])

    def test_split2(self):
        print ("split test2")
        node = TextNode("This is text with a `code block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes,[TextNode("This is text with a ", TextType.TEXT),
                                    TextNode("code block", TextType.CODE)])

    def test_split3(self):
        print ("split test3")
        node = TextNode("`code block`at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes,[TextNode("code block", TextType.CODE),
                                    TextNode("at start",TextType.TEXT)])
        
    def test_split4(self):
        print ("split test4")
        node = TextNode("`some code` text `code block` finish", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes,[TextNode("some code", TextType.CODE),
                                    TextNode(" text ",TextType.TEXT),
                                    TextNode("code block",TextType.CODE),
                                    TextNode(" finish",TextType.TEXT)])
        

    def test_extract_markdown_images(self):
        matches = extract_markdown_images("This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"    )
        print(matches)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)    

    def test_split_images(self):
        node = TextNode("This is text with an ![alt_text](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [TextNode("This is text with an ", TextType.TEXT),
            TextNode("alt_text", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png")],
        new_nodes)    

    def test_split_links(self):
        node = TextNode("This is a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [TextNode("This is a link ", TextType.TEXT),
             TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
             TextNode(" and ", TextType.TEXT),
             TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev")
            ],
            new_nodes)

    def test_split_main(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes= text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_block_to_blocktype(self):
        self.assertTrue(block_to_block_type('```fdsfsa````')==BlockType.CODE)

    def test_block_to_blocktype2(self):
        self.assertTrue(block_to_block_type('``fdsfsa````')==BlockType.PARAGRAPH)
    
    def test_block_to_blocktype3(self):
        self.assertTrue(block_to_block_type('## ```fdsfsa````')==BlockType.HEADING)
    
    def test_block_to_blocktype4(self):
        self.assertTrue(block_to_block_type('1.fdsa\n2.dsfsa')==BlockType.ORDERED_LIST)
    
    def test_block_to_blocktype5(self):
        self.assertTrue(block_to_block_type('>fdsfsa\n>aaa')==BlockType.QUOTE)

    def test_block_to_blocktype(self):
        self.assertTrue(block_to_block_type('- fsa\n- b')==BlockType.UNORDERED_LIST)        

    def test_block_to_blocktype(self):
        self.assertTrue(block_to_block_type('- fdsfsa\nfdsa')==BlockType.PARAGRAPH)        

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph text in a p tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    )

    def test_codeblock(self):
        md = """
```This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
        "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
    )        

if __name__ == "__main__":
    unittest.main()
