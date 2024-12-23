from abc import ABC, abstractmethod
import os
from lxml import etree
from typing import Union, Tuple
import logging


class Parser(ABC):
    @abstractmethod
    def parse(self, data):
        pass
    
    def get_root(self, file: str):
        """
        Parses an XML file and returns its root element.

        Parameters
        ----------
        file : str
            Path to the XML file.

        Returns
        -------
        lxml.etree._Element
            Root element of the parsed XML document.
        """
        with open(file, 'r', encoding='utf-8') as f:
            tree = etree.parse(f)
            self.root = tree.getroot()
            return self.root
        
    def remove_node(self, tree, node):
        """
            Removes specified nodes from the XML tree while preserving their tail text.

            Parameters
            ----------
            tree : lxml.etree._Element
                The XML tree or subtree to process.
            node : str
                XPath expression identifying the nodes to remove.

            Returns
            -------
            lxml.etree._Element
                The modified XML tree with specified nodes removed.
        """
        if tree.findall(node, namespaces=self.namespaces) is not None:
            for item in tree.findall(node, namespaces=self.namespaces):
                text = ' '.join(item.itertext()).strip()
                
                # Find the parent and remove the <node> element
                parent = item.getparent()
                tail_text = item.tail
                if parent is not None:
                    parent.remove(item)

                # Preserve tail text if present
                if tail_text:
                    if parent.getchildren():
                        # If there's a previous sibling, add the tail to the last child
                        previous_sibling = parent.getchildren()[-1]
                        previous_sibling.tail = (previous_sibling.tail or '') + tail_text
                    else:
                        # If no siblings, add the tail text to the parent's text
                        parent.text = (parent.text or '') + tail_text
        
        return tree
    
def validate_xml(xml_path: str, xsd_path: str): 
    """
    Validate an XML file against an XSD schema.
    
    Args:
        xml_path (str): Path to the XML file to validate
        xsd_path (str): Path to the XSD schema file
        
    Returns:
        Tuple[bool, Union[str, None]]: A tuple containing:
            - bool: True if validation successful, False otherwise
            - Union[str, None]: Error message if validation failed, None if successful
    """
    try:
         # Create XML parser with schema location resolution
        parser = etree.XMLParser(remove_blank_text=True)
        
        # Create a custom resolver to handle relative paths
        class LocalResolver(etree.Resolver):
            def resolve(self, url, id, context):
                # Get the directory of the main XSD file
                schema_dir = os.path.dirname(os.path.abspath(xsd_path))
                # Construct full path to the imported schema
                schema_path = os.path.join(schema_dir, os.path.basename(url))
                
                if os.path.exists(schema_path):
                    return self.resolve_filename(schema_path, context)
                return None
        
        # Add the resolver to the parser
        parser.resolvers.add(LocalResolver())
        
        # Parse and validate
        xmlschema_doc = etree.parse(xsd_path, parser)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        xml_doc = etree.parse(xml_path, parser)
        
        xmlschema.assertValid(xml_doc)
        return True
            
    except etree.XMLSyntaxError as e:
        error_msg = f"XML Syntax Error: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
        
    except etree.DocumentInvalid as e:
        error_msg = f"Schema Validation Error: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected Error: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
    
 