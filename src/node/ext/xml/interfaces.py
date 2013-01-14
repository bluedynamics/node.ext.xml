from zope.interface import (
    Interface,
    Attribute,
)
from node.interfaces import INode


class IXMLFactory(Interface):

    def __call__(path, idattribute):
        """Read XML file from path and instanciate model consisting of
        IXMLNode implementations.

        @param path: path to input xml file
        @param idattribute: attribute used to catalog referencable objects.
                            this might get a list in future.
        """


class IXMLNode(INode):
    """An XML Node.
    """
    idattribute = Attribute(u"Attribute indicating the xml element id")
    attributes = Attribute(u"The node attributes if there are one")
    text = Attribute(u"The Text content of the node.")
    namespaces = Attribute(u"Namespaces dictionary")

    def reference(id):
        """Get Node referenced by id or none if inexistent.
        """
