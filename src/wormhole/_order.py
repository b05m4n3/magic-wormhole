from __future__ import print_function, absolute_import, unicode_literals
from zope.interface import implementer
from attr import attrs, attrib
from attr.validators import provides, instance_of
from automat import MethodicalMachine
from . import _interfaces

@attrs
@implementer(_interfaces.IOrder)
class Order(object):
    _side = attrib(validator=instance_of(type(u"")))
    _timing = attrib(validator=provides(_interfaces.ITiming))
    m = MethodicalMachine()

    def __attrs_post_init__(self):
        self._key = None
        self._queue = []
    def wire(self, key, receive):
        self._K = _interfaces.IKey(key)
        self._R = _interfaces.IReceive(receive)

    @m.state(initial=True)
    def S0_no_pake(self): pass
    @m.state(terminal=True)
    def S1_yes_pake(self): pass

    def got_message(self, phase, body):
        assert isinstance(phase, type("")), type(phase)
        assert isinstance(body, type(b"")), type(body)
        if phase == "pake":
            self.got_pake(phase, body)
        else:
            self.got_non_pake(phase, body)

    @m.input()
    def got_pake(self, phase, body): pass
    @m.input()
    def got_non_pake(self, phase, body): pass

    @m.output()
    def queue(self, phase, body):
        assert isinstance(phase, type("")), type(phase)
        assert isinstance(body, type(b"")), type(body)
        self._queue.append((phase, body))
    @m.output()
    def notify_key(self, phase, body):
        self._K.got_pake(body)
    @m.output()
    def drain(self, phase, body):
        del phase
        del body
        for (phase, body) in self._queue:
            self._deliver(phase, body)
        self._queue[:] = []
    @m.output()
    def deliver(self, phase, body):
        self._deliver(phase, body)

    def _deliver(self, phase, body):
        self._R.got_message(phase, body)

    S0_no_pake.upon(got_non_pake, enter=S0_no_pake, outputs=[queue])
    S0_no_pake.upon(got_pake, enter=S1_yes_pake, outputs=[notify_key, drain])
    S1_yes_pake.upon(got_non_pake, enter=S1_yes_pake, outputs=[deliver])
