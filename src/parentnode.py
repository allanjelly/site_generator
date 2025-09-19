from htmlnode import HTMLNode
from leafnode import LeafNode

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if not self.tag:
            raise ValueError ("Parent without value")
        if not self.children:
            raise ValueError ("Error - no children")

        outstring = f"<{self.tag}{self.props_to_html()}>"
        
        for child in self.children:
            outstring += child.to_html()

        outstring += f"</{self.tag}>"

        return outstring
        
        