XML IO
======

Lookup factory and read existing XML model::

    >>> import os
    >>> from zope.component import getUtility
    >>> from node.ext.xml.interfaces import IXMLFactory
    >>> factory = getUtility(IXMLFactory)
    >>> path = os.path.sep.join([datadir, 'test.xml'])

The second argument given to the factory is the attribute name used to catalog
nodes by id. Its set to ``id`` by default::

    >>> xml = factory(path, 'xmi.id')

It's an XMI exported by poseidon::

    >>> xml
    <XMLNode object '...' at ...>

The name of the root element is the path to the xml file::

    >>> xml.__name__
    ''

    >>> xml.outpath
    '.../node.ext.xml/src/node/ext/xml/testing/data/test.xml'

Get the XMI element. The name given to the nodes ``__getitem__`` function is
always interpreted as the plain tag name. If more than one node is found by tag
name, return a list of them::

    >>> xmi = xml['XMI']
    >>> xmi
    <XMLNode object '...' at ...>

Path of the XMI node::

    >>> xmi.path
    ['', '...:XMI']

Read some more child nodes and check name and tag::

    >>> content = xmi['XMI.content']
    >>> content.__name__
    '...:XMI.content'

    >>> content.element.tag
    'XMI.content'

The ``__name__`` attribute of each node is combined out of the node uuid and
the tag name separated by ``:``::

    >>> model = content['Model']
    >>> model.__name__
    '...:{org.omg.xmi.namespace.UML}Model'

The ``tag`` attribute is formatted in clark name notation::

    >>> model.element.tag
    '{org.omg.xmi.namespace.UML}Model'

Read some more child nodes::

    >>> nsoe = model['Namespace.ownedElement']
    >>> nsoe.__name__
    '...:{org.omg.xmi.namespace.UML}Namespace.ownedElement'

    >>> nsoe.element.tag
    '{org.omg.xmi.namespace.UML}Namespace.ownedElement'

    >>> package = nsoe['Package']
    >>> package.__name__
    '...:{org.omg.xmi.namespace.UML}Package'

    >>> package.element.tag
    '{org.omg.xmi.namespace.UML}Package'

    >>> mestereotype = package['ModelElement.stereotype']
    >>> mestereotype.__name__
    '...:{org.omg.xmi.namespace.UML}ModelElement.stereotype'

    >>> mestereotype.element.tag
    '{org.omg.xmi.namespace.UML}ModelElement.stereotype'

    >>> stereotyperef = mestereotype['Stereotype']
    >>> stereotyperef.__name__
    '...:{org.omg.xmi.namespace.UML}Stereotype'

    >>> stereotyperef.element.tag
    '{org.omg.xmi.namespace.UML}Stereotype'

The attributes of a node are accessible through the node's ``attributes``
attribute::

    >>> stereotyperef.attributes
    {'xmi.idref': 'Im2b54d018m12023811d77mm7e67'}

    >>> stereotyperef.path
    ['',
    '...:XMI',
    '...:XMI.content',
    '...:{org.omg.xmi.namespace.UML}Model',
    '...:{org.omg.xmi.namespace.UML}Namespace.ownedElement',
    '...:{org.omg.xmi.namespace.UML}Package',
    '...:{org.omg.xmi.namespace.UML}ModelElement.stereotype',
    '...:{org.omg.xmi.namespace.UML}Stereotype']

Lets read a reference id from a node, under which the referenced node can be
looked up::

    >>> stereotyperef.attributes['xmi.idref']
    'Im2b54d018m12023811d77mm7e67'

As pointed above, if more nodes are contained by tag name, they are returned as
list from ``__getitem__`` and as well by ``get()``::

    >>> stereotypedef = nsoe['Stereotype']
    >>> stereotypedef
    [<XMLNode object '...' at ...>,
    <XMLNode object '...' at ...>,
    <XMLNode object '...' at ...>,
    <XMLNode object '...' at ...>,
    <XMLNode object '...' at ...>]

This is the node which is referenced by the ``stereotyperef`` above::

    >>> stereotypedef[0].attributes['xmi.id']
    'Im2b54d018m12023811d77mm7e67'

    >>> stereotypedef[0].path
    ['',
    '...:XMI',
    '...:XMI.content',
    '...:{org.omg.xmi.namespace.UML}Model',
    '...:{org.omg.xmi.namespace.UML}Namespace.ownedElement',
    '...:{org.omg.xmi.namespace.UML}Stereotype']

    >>> stereotypedef[0].attributes['name']
    'egg'

Now look up the referenced node by id. The ``reference`` function could be
called elsewhere in the tree::

    >>> refid = stereotyperef.attributes['xmi.idref']
    >>> fromrefstereotypedef = stereotyperef.reference(refid)

    >>> fromrefstereotypedef.path
    ['',
    '...:XMI',
    '...:XMI.content',
    '...:{org.omg.xmi.namespace.UML}Model',
    '...:{org.omg.xmi.namespace.UML}Namespace.ownedElement',
    '...:{org.omg.xmi.namespace.UML}Stereotype']

Must be the same node::

    >>> fromrefstereotypedef is stereotypedef[0]
    True

Also the elements must point to the same memory::

    >>> fromrefstereotypedef.element is stereotypedef[0].element
    True

    >>> fromrefstereotypedef.attributes['name']
    'egg'

    >>> stereotypedef[-1].path
    ['',
    '...:XMI',
    '...:XMI.content',
    '...:{org.omg.xmi.namespace.UML}Model',
    '...:{org.omg.xmi.namespace.UML}Namespace.ownedElement',
    '...:{org.omg.xmi.namespace.UML}Stereotype']

    >>> stereotypedef[-1].attributes['name']
    'view'

Overwrite ``_outpath`` which is on root the input path. Model just gets
overwritten on ``__call__`` by default::

    >>> xml.outpath = os.path.sep.join([datadir, 'testout.xml'])
    >>> xml()

Create XML tree from scratch::

    >>> from node.ext.xml import XMLNode
    >>> path = os.path.sep.join([datadir, 'new.xml'])
    >>> nsmap = {
    ...    None: 'http://fubar.com/ns1',
    ...    'ns2': 'http://fubar.com/ns2',
    ... }
    >>> xml = XMLNode('root', path=path, ns=nsmap[None], nsmap=nsmap)
    >>> child = XMLNode('child', nsmap=nsmap)
    >>> xml[child.uuid] = child
    >>> child = XMLNode('child', ns=nsmap['ns2'], nsmap=nsmap)
    >>> xml[child.uuid] = child
    >>> child.attributes['foo'] = 'bar'
    >>> child.attributes['{%s}baz' % nsmap['ns2']] = 'bar'
    >>> xml.format = 1
    >>> xml()

Values::

    >>> xml.values()
    [<XMLNode object '...:child' at ...>, 
    <XMLNode object '...:{http://fubar.com/ns2}child' at ...>]

Items::

    >>> xml.items()
    [('...:child', 
    <XMLNode object '...:child' at ...>), 
    ('...:{http://fubar.com/ns2}child', 
    <XMLNode object '...:{http://fubar.com/ns2}child' at ...>)]
