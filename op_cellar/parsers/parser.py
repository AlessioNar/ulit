from abc import ABC, abstractmethod
import os
from lxml import etree
from typing import Union, Tuple
import logging


class Parser(ABC):
    @abstractmethod
    def parse(self, data):
        pass

class XMLParser(Parser):
    def parse(self, data):
        # Your XML parsing logic here
        pass


def validate_xml(xml_path: str, xsd_path: str) -> Tuple[bool, Union[str, None]]:
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
        return True, None
            
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