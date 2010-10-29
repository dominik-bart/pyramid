import venusian

from zope.interface import implements

from pyramid.interfaces import IContextFound
from pyramid.interfaces import INewRequest
from pyramid.interfaces import INewResponse
from pyramid.interfaces import IApplicationCreated

class subscriber(object):
    """ Decorator activated via a :term:`scan` which treats the
    function being decorated as an event subscriber for the set of
    interfaces passed as ``*ifaces`` to the decorator constructor.

    For example:

    .. code-block:: python
    
       from pyramid.interfaces import INewRequest
       from pyramid.events import subscriber

       @subscriber(INewRequest)
       def mysubscriber(event):
           event.request.foo = 1

    More than one event type can be passed as a construtor argument:
        
    .. code-block:: python
    
       from pyramid.interfaces import INewRequest
       from pyramid.events import subscriber

       @subscriber(INewRequest, INewResponse)
       def mysubscriber(event):
           print event

    When the ``subscriber`` decorator is used without passing an arguments,
    the function it decorates is called for every event sent:

    .. code-block:: python
    
       from pyramid.interfaces import INewRequest
       from pyramid.events import subscriber

       @subscriber()
       def mysubscriber(event):
           print event

    This method will have no effect until a :term:`scan` is performed
    against the package or module which contains it, ala:

    .. code-block:: python
    
       from pyramid.configuration import Configurator
       config = Configurator()
       config.scan('somepackage_containing_subscribers')

    """
    venusian = venusian # for unit testing

    def __init__(self, *ifaces):
        self.ifaces = ifaces

    def register(self, scanner, name, wrapped):
        config = scanner.config
        config.add_subscriber(wrapped, self.ifaces)

    def __call__(self, wrapped):
        self.venusian.attach(wrapped, self.register, category='pyramid')
        return wrapped

class NewRequest(object):
    """ An instance of this class is emitted as an :term:`event`
    whenever :mod:`pyramid` begins to process a new request.  The
    even instance has an attribute, ``request``, which is a
    :term:`request` object.  This event class implements the
    :class:`pyramid.interfaces.INewRequest` interface."""
    implements(INewRequest)
    def __init__(self, request):
        self.request = request

class NewResponse(object):
    """ An instance of this class is emitted as an :term:`event`
    whenever any :mod:`pyramid` :term:`view` or :term:`exception
    view` returns a :term:`response`.

    The instance has two attributes:``request``, which is the request
    which caused the response, and ``response``, which is the response
    object returned by a view or renderer.

    If the ``response`` was generated by an :term:`exception view`,
    the request will have an attribute named ``exception``, which is
    the exception object which caused the exception view to be
    executed.  If the response was generated by a 'normal' view, the
    request will not have this attribute.

    This event will not be generated if a response cannot be created
    due to an exception that is not caught by an exception view (no
    response is created under this circumstace).

    This class implements the
    :class:`pyramid.interfaces.INewResponse` interface.

    .. note::

       Postprocessing a response is usually better handled in a WSGI
       :term:`middleware` component than in subscriber code that is
       called by a :class:`pyramid.interfaces.INewResponse` event.
       The :class:`pyramid.interfaces.INewResponse` event exists
       almost purely for symmetry with the
       :class:`pyramid.interfaces.INewRequest` event.
    """
    implements(INewResponse)
    def __init__(self, request, response):
        self.request = request
        self.response = response

class ContextFound(object):
    """ An instance of this class is emitted as an :term:`event` after
    the :mod:`pyramid` :term:`router` finds a :term:`context`
    object (after it performs traversal) but before any view code is
    executed.  The instance has an attribute, ``request``, which is
    the request object generated by :mod:`pyramid`.

    Notably, the request object will have an attribute named
    ``context``, which is the context that will be provided to the
    view which will eventually be called, as well as other attributes
    attached by context-finding code.

    This class implements the
    :class:`pyramid.interfaces.IContextFound` interface.

    .. note:: As of :mod:`pyramid` 1.0, for backwards compatibility
       purposes, this event may also be imported as
       :class:`pyramid.events.AfterTraversal`.
    """
    implements(IContextFound)
    def __init__(self, request):
        self.request = request

AfterTraversal = ContextFound # b/c as of 1.0
    
class ApplicationCreated(object):    
    """ An instance of this class is emitted as an :term:`event` when
    the :meth:`pyramid.configuration.Configurator.make_wsgi_app` is
    called.  The instance has an attribute, ``app``, which is an
    instance of the :term:`router` that will handle WSGI requests.
    This class implements the
    :class:`pyramid.interfaces.IApplicationCreated` interface.

    .. note:: For backwards compatibility purposes, this class can
       also be imported as
       :class:`pyramid.events.WSGIApplicationCreatedEvent`.  This
       was the name of the event class before :mod:`pyramid` 1.0.

    """
    implements(IApplicationCreated)
    def __init__(self, app):
        self.app = app
        self.object = app

WSGIApplicationCreatedEvent = ApplicationCreated # b/c (as of 1.0)

