from textnode import TextNode
from textnode import TextType
from leafnode import LeafNode
from textnode import BlockType
from htmlnode import HTMLNode
from parentnode import ParentNode
import re
import shutil
import os
import sys

def main():

    basepath ='/'
    if len(sys.argv) >1:
        basepath = sys.argv[1]
    
    print (basepath)
    copy_static_to_public()
    generate_pages_recursive('content', 'template.html', 'docs',basepath)

def text_node_to_html_node(text_node:TextNode)->LeafNode:

    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None,value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b",value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i",value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code",value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a",value=text_node.text,props={"href":text_node.url})
        case TextType.IMAGE:
            return LeafNode(tag="img",value=' ',props={"src":text_node.url,"alt":text_node.text})
        case _:
            raise Exception ("Unknown text type")

def split_nodes_delimiter(old_nodes:list[TextNode], delimiter:str, text_type:TextType) -> list[TextNode]:

    ret_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            ret_nodes.append(node)
            continue

        text = node.text
        while len(text) > 0:
            pos1 = text.find(delimiter)
# delimiter not found            
            if pos1 == -1:
                ret_nodes.append(TextNode(text,TextType.TEXT))
                break
            pos2 = text.find(delimiter,pos1+len(delimiter))
# closing delimiter not found
            if pos2 == -1:
                raise Exception ("closing delimiter not found")          
# good cases
            if pos1 > 0:
                ret_nodes.append(TextNode(text[0:pos1], TextType.TEXT))
            ret_nodes.append(TextNode(text[pos1+len(delimiter):pos2],text_type))
            text = text[pos2+len(delimiter):]

    return ret_nodes
        
def extract_markdown_images(text:str):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def extract_markdown_links(text:str):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def split_nodes_image(old_nodes:list[TextNode])-> list[TextNode]:
    
    ret_nodes = []
    for node in old_nodes:

        images_found = extract_markdown_images(node.text)
        if len(images_found) == 0:
            ret_nodes.append(node)
            continue
        text = node.text
        for image in images_found:
            pos1 = text.find(f"![{image[0]}]")
            pos2 = text.find(f"({image[1]})")+len(image[1])+2
        
            if pos1 > 0:
                ret_nodes.append(TextNode(text[0:pos1],TextType.TEXT))
            ret_nodes.append(TextNode(image[0],TextType.IMAGE,image[1]))
            text = text[pos2:]
        if  len(text) > 0:
            ret_nodes.append(TextNode(text,TextType.TEXT))

    return ret_nodes

def split_nodes_link(old_nodes:list[TextNode])-> list[TextNode]:
    
    ret_nodes = []
    for node in old_nodes:

        links_found = extract_markdown_links(node.text)

        if len(links_found) == 0:
            ret_nodes.append(node)
            continue
        text = node.text
        for link in links_found:
            pos1 = text.find(f"[{link[0]}]")
            pos2 = text.find(f"({link[1]})")+len(link[1])+2
        
            if pos1 > 0:
                ret_nodes.append(TextNode(text[0:pos1],TextType.TEXT))
            ret_nodes.append(TextNode(link[0],TextType.LINK,link[1]))
            text = text[pos2:]
        if  len(text) > 0:
            ret_nodes.append(TextNode(text,TextType.TEXT))

    return ret_nodes

def text_to_textnodes(text:str)-> list[TextNode]:

    nodes = []
    nodes.append(TextNode(text, TextType.TEXT))
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes,'`',TextType.CODE)
    nodes = split_nodes_delimiter(nodes, '_',TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes,'**',TextType.BOLD)

    return nodes

def markdown_to_blocks(markdown:str) -> list[str]:
    blocks = markdown.split('\n\n')

    if len(blocks) == 0:
        return []
    ret_blocks = []
    for block in blocks:
        block=block.strip()
        if block == '':
            continue
        ret_blocks.append(block)
    return ret_blocks

def block_to_block_type(block:str) -> BlockType:
    lines = block.splitlines()
    if lines[0].startswith('```') and lines[-1].endswith('```'):
        return BlockType.CODE
    
    if lines[0].startswith(('# ','## ','### ','#### ','##### ','###### ')):
        return BlockType.HEADING
    
    is_quote = False
    is_unordered = False
    is_ordered = False
    i = 1

    for line in lines:
        if line.startswith('>'):
            is_quote = True
        else:
            is_quote = False
        if line.startswith('- '):
            is_unordered = True
        else:
            is_unordered = False
        if line.startswith(f"{i}."):
            is_ordered = True
        else:
            ordered = False

    if is_quote == True:
        return BlockType.QUOTE
    if is_unordered == True:
        return BlockType.UNORDERED_LIST
    if is_ordered == True:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown:str) -> HTMLNode:

    blocks = markdown_to_blocks(markdown)
    html_blocks = []

    for block in blocks:

        type = block_to_block_type(block)
        match type:
            case BlockType.PARAGRAPH:
                html_blocks.append (ParentNode(tag="p",children = text_to_children(block)))
            case BlockType.UNORDERED_LIST:
                list_items = block.splitlines()
                children = []
                for item in list_items:
                    children.append(ParentNode(tag="li",children = text_to_children(item[2:])))
                html_blocks.append (ParentNode(tag="ul",children=children))
            case BlockType.ORDERED_LIST:
                list_items = block.splitlines()
                children = []
                for item in list_items:
                    i = len(f"{i}. ")
                    text = str(item)[i:]
                    children.append(ParentNode(tag="li",children = text_to_children(text)))
                html_blocks.append (ParentNode(tag="ol",children = children))
            case BlockType.CODE:
                html_blocks.append(ParentNode(tag="pre",children = [text_node_to_html_node(TextNode(block[3:-3],TextType.CODE))]))
            case BlockType.QUOTE:
                quote_lines = block.splitlines()
                new_lines = []
                for line in quote_lines:
                    new_lines.append(line[2:])
                block = ''.join(new_lines)
                html_blocks.append (ParentNode(tag="blockquote",children = text_to_children(block)))
            case BlockType.HEADING:
                i = len(block)-len(block.lstrip('#'))+1
                html_blocks.append (ParentNode(tag=f"h{1}",children = text_to_children(block[i:])))

    return ParentNode(tag="div",children=html_blocks)

def text_to_children(text:str) -> list[HTMLNode]:

    text_nodes = text_to_textnodes(text)
    leaf_nodes = []
    for node in text_nodes:
        leaf_nodes.append(text_node_to_html_node(node))
    return leaf_nodes

def copy_static_to_public():
    if os.getcwd().endswith('src'):
        src_dir = '../static'
        dst_dir = '../docs'
    else:
        src_dir = 'static'
        dst_dir = 'docs'
    if not os.path.exists('static'):
        raise Exception ("wrong path")
    
    shutil.rmtree(dst_dir)

    copy_dir_content(src_dir,dst_dir)

def copy_dir_content(src_dir,dst_dir):
    print (f"creating dir...{dst_dir}")
    os.mkdir(dst_dir)
    to_copy =  os.listdir(src_dir)
    for file in to_copy:
        src_path = os.path.join(src_dir,file)
        dst_path = os.path.join(dst_dir,file)        
        if os.path.isfile(src_path):
            print(f"copyting file..{src_path} to {dst_path}")
            shutil.copy(src_path,dst_path)
        else:
            copy_dir_content(src_dir+'/'+file, dst_dir+'/'+file)

def extract_title(markdown:str)-> str:
    lines = markdown.splitlines()
    for line in lines:
        if line.startswith('# '):
            return line.lstrip('# ')
    raise Exception ("No title (h1) in markdown")    

def generate_page(from_path, template_path, dest_path, basepath):
    print (f"Generating page from {from_path} to {dest_path} using {template_path}")
    if os.getcwd().endswith('src'):
        os.chdir('..')

    f = open(from_path)
    markdown = f.read()

    f = open(template_path)
    template = f.read()

    title = extract_title(markdown)
    html = markdown_to_html_node(markdown).to_html()

    out_html = template.replace('{{ Title }}', title)
    out_html = out_html.replace('{{ Content }}', html)
    out_html = out_html.replace('href="/', f'href="{basepath}')
    out_html = out_html.replace('src="/', f'src="{basepath}')
    
    directory = os.path.dirname(dest_path)
    if not os.path.exists(directory):
        os.mkdir (directory)

    with open(dest_path, "w") as f:
        f.write(out_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):

    if os.getcwd().endswith('src'):
        os.chdir('..')

    dir_content = os.listdir(dir_path_content)

    for dir_entry in dir_content:
        src_path = os.path.join(dir_path_content, dir_entry)
        dst_path = os.path.join(dest_dir_path, dir_entry)
  
        if os.path.isfile(src_path):
            if src_path.endswith('.md'):
                dst_path = dst_path[:-3]
                dst_path += '.html'
            generate_page(src_path, template_path, dst_path, basepath)            
        else:
            if not os.path.exists(dst_path):
                os.mkdir(dst_path)
            generate_pages_recursive (src_path, template_path, dst_path, basepath)


main()
