"""Base class for a Widget"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2013  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import uuid

from IPython.config import LoggingConfigurable
from IPython.utils.traitlets import Instance, Unicode, Bytes, Bool, Dict, Any

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------

class Widget(LoggingConfigurable):
    
    shell = Instance('IPython.core.interactiveshell.InteractiveShellABC')
    def _shell_default(self):
        return get_ipython()
    iopub_socket = Any()
    def _iopub_socket_default(self):
        return self.shell.parent.iopub_socket
    session = Instance('IPython.kernel.zmq.session.Session')
    def _session_default(self):
        if self.shell is None:
            return
        return self.shell.parent.session
    
    topic = Bytes()
    def _topic_default(self):
        return ('widget-%s' % self.widget_id).encode('ascii')
    
    _destroy_data = Dict(help="data dict, if any, to be included in widget_destroy")
    _create_data = Dict(help="data dict, if any, to be included in widget_create")
    
    _destroyed = Bool(False)
    widget_type = Unicode('widget')
    widget_id = Unicode()
    def _widget_id_default(self):
        return uuid.uuid4().hex
    
    def _publish_msg(self, msg_type, data=None, **keys):
        """Helper for sending a widget message on IOPub"""
        data = {} if data is None else data
        self.session.send(self.iopub_socket, msg_type,
            dict(data=data, widget_id=self.widget_id, **keys),
            ident=self.topic,
        )
    
    def __del__(self):
        """trigger destroy on gc"""
        self.destroy()
    
    # publishing messages
    
    def create(self):
        """Create the frontend-side version of this widget"""
        self._publish_msg('widget_create', self._create_data, widget_type = self.widget_type)
    
    def destroy(self):
        """Destroy the frontend-side version of this widget"""
        if self._destroyed:
            # only destroy once
            return
        self._publish_msg('widget_destroy', self._destroy_data)
        self._destroyed = True
    
    def update(self, data=None):
        """Update the frontend-side version of this widget"""
        self._publish_msg('widget_update', data)
    
    # handling of incoming messages
    
    def handle_destroy(self, data):
        """Handle a widget_destroy message"""
        self.log.debug("handle_destroy %s", data)
    
    def handle_update(self, data):
        """Handle a widget_update message"""
        self.log.debug("handle_update %s", data)
        self.update_data = data


__all__ = ['Widget']
