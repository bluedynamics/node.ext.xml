import os
import tempfile
import shutil
from lxml import etree
from plumber import plumber
from node.interfaces import (
    ICallable,
    IRoot,
)
from node.base import OrderedNode
from node.behaviors import (
    Order,
    Reference,
)
from zope.interface import (
    implementer,
    alsoProvides,
)
from node.utils import LocationIterator
from node.ext.xml.interfaces import (
    IXMLFactory,
    IXMLNode,
)


_marker = object()


@implementer(IXMLFactory)
class XMLFactory(object):

    def __call__(self, path, idattribute='id', buffer=None, nsprefix=None):
        file = open(path)
        model = etree.parse(file)
        file.close()
        nsmap=model.getroot().nsmap
        if nsprefix:
            #if an ns prefix is given, get the namespace by name and prefix
            #the id attribute with the namespace
            idattribute='{%s}%s' % (nsmap[nsprefix],idattribute)
        root = XMLNode(element=model,
                       path=path,
                       nsmap=nsmap,
                       idattribute=idattribute)
        alsoProvides(root, IRoot)
        return root


@implementer(IXMLNode, ICallable)
class XMLNode(OrderedNode):
    __metaclass__ = plumber
    __plumbing__ = Reference, Order
    refindex = dict() # XXX: don't provide global. otherwise multiple
                      #      instanciated xml trees share the same reference
                      #      index !!!!!!!!!!!!!!!!!

    def __init__(self,
                 name=None,
                 element=None,
                 ns=None,
                 nsmap=dict(),
                 idattribute='id',
                 path=None):
        self.format = 0
        self.outpath = path
        self.element = element
        if self.element is None and path is not None:
            self.element = etree.Element(name, nsmap=nsmap)
            alsoProvides(self, IRoot)
        self.namespaces = nsmap
        self.idattribute = idattribute
        _ns, _name = self._extractname(self.element)
        if not name: name = _name
        if not ns: ns = _ns
        if ns: self.prefix = '{%s}' % ns
        else: self.prefix = ''
        self.ns = ns
        OrderedNode.__init__(self, name=name)
        if element is None:
            return
        if etree.iselement(element):
            fq = '%s%s' % (self.prefix, name)
            if element.tag != fq:
                raise ValueError, \
                      'Fq of given element does not match (%s != %s)' \
                      % (element.tag, fq)
            children = self.element.getchildren()
        else:
            children = [element.getroot()]
        self._buildchildren(children)

    def __call__(self):
        if not IRoot.providedBy(self):
            raise RuntimeError(u"Called on nonroot")
        with open(self.outpath, "wb") as file:
            file.write("<?xml version=\"1.0\" encoding=\"%s\"?>\n" % 'UTF-8')
            file.write(etree.tostring(self.element, pretty_print=True))

    @property
    def attributes(self):
        if hasattr(self.element, 'attrib'):
            return self.element.attrib
        return dict()

    @property
    def text(self):
        if hasattr(self.element, 'text'):
            return self.element.text
        return ''

    def reference(self, id):
        return self.refindex.get(id, None)

    @property
    def ns_name(self):
        for key, value in self.namespaces.items():
            if value == self.ns:
                return key

    @property
    def namedpath(self):
        path = list()
        for parent in LocationIterator(self):
            if parent.attributes.has_key('name'):
                path.append(parent.attributes['name'])
        # remove model name, as model is the actual root, and put "" instead
        path.pop()
        path.append("")
        path.reverse()
        return path

    #def __delitem__(self, key):
    #    todelete = self[key]
    #    self.element.remove(todelete.element)
    #    Node.__delitem__(self, key)

    def __setitem__(self, key, val):
        name = '%s%s' % (val.prefix, val.__name__)
        if val.element is None:
            val.element = etree.SubElement(self.element, name)
        name = '%s:%s' % (val.uuid, name)
        id = val.attributes.get(val.idattribute, None)
        if id:
            self.refindex[id] = val
        OrderedNode.__setitem__(self, name, val)

    def __getitem__(self, name):
        # XXX: use UUID here for tree representation and provide ``children``
        #      function for filtering by tag name and similar.
        keys = self._parsekeys(name)
        if not keys:
            raise KeyError(u"Node not found")
        if len(keys) == 1:
            return OrderedNode.__getitem__(self, keys[0])
        return [OrderedNode.__getitem__(self, key) for key in keys]

    def get(self, name, default=_marker):
        # XXX: see __getitem__
        try:
            return self[name]
        except ValueError, e:
            return default

    def values(self):
        # XXX: see __getitem__
        return [OrderedNode.__getitem__(self, key) for key in self.keys()]

    def items(self):
        # XXX: see __getitem__
        return [(key, OrderedNode.__getitem__(self, key)) for key in self.keys()]

    def _parsekeys(self, name):
        ret = list()
        for key in self.keys():
            ns, tagname = self._parsename(key[key.find(':') + 1:])
            if tagname.lower() == name.lower():
                ret.append(key)
        return ret

    def _buildchildren(self, children):
        for elem in children:
            try:
                ns, name = self._extractname(elem)
            except:
                # XXX: elem is comment -> what to do?
                continue
            node = XMLNode(name=name, element=elem,
                           ns=ns, nsmap=self.namespaces,
                           idattribute=self.idattribute)
            self[name] = node

    def _extractname(self, element):
        if etree.iselement(element):
            return self._parsename(element.tag)
        return '', ''

    def _parsename(self, name):
        ns = ''
        if name.find('{') != -1:
            start = name.find('{') + 1
            end = name.find('}')
            ns = name[start:end]
            name = name[end + 1:]
        return ns, name

    def printtree(self):
        print self.__name__
        self._printtree(0)

    def _printtree(self, indent):
        for node in self.values():
            print indent * ' ' + node.element.tag
            node._printtree(indent + 2)
