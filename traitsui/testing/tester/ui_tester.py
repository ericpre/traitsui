#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
import contextlib

from traitsui.testing._gui import process_cascade_events
from traitsui.testing._exception_handling import reraise_exceptions
from traitsui.testing.tester._ui_tester_registry.default_registry import (
    get_default_registry
)
from traitsui.testing.tester.ui_wrapper import UIWrapper


class UITester:
    """ UITester assists testing of GUI applications developed using TraitsUI.

    See :ref:`testing-traitsui-applications` Section in the User Manual for
    further details.

    Parameters
    ----------
    registries : list of TargetRegistry, optional
        Registries of interaction for different targets, in the order
        of decreasing priority. If provided, a shallow copy will be made.
        Default registries are always appended to the list to provide
        builtin support for TraitsUI UI and editors.
    delay : int, optional
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired. Defaults to 0.

    Attributes
    ----------
    delay : int
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired.
    """

    def __init__(self, registries=None, delay=0):
        if registries is None:
            self._registries = []
        else:
            self._registries = registries.copy()

        # The find_by_name method in this class depends on this registry
        self._registries.append(get_default_registry())
        self.delay = delay

    @contextlib.contextmanager
    def create_ui(self, object, ui_kwargs=None):
        """ Context manager to create a UI and dispose it upon exit.

        Parameters
        ----------
        object : HasTraits
            An instance of HasTraits for which a GUI will be created.
        ui_kwargs : dict or None, optional
            Keyword arguments to be provided to ``HasTraits.edit_traits``.
            Default is to call ``edit_traits`` with no additional keyword
            arguments.

        Yields
        ------
        ui : traitsui.ui.UI
        """
        # Nothing here uses UITester, but it is an instance method to preserve
        # options to extend using instance states.

        ui_kwargs = {} if ui_kwargs is None else ui_kwargs
        ui = object.edit_traits(**ui_kwargs)
        try:
            yield ui
        finally:
            with reraise_exceptions():
                # At the end of a test, there may be events to be processed.
                # If dispose happens first, those events will be processed
                # after various editor states are removed, causing errors.
                process_cascade_events()
                try:
                    ui.dispose()
                finally:
                    # dispose is not atomic and may push more events to the
                    # event queue. Flush those too.
                    process_cascade_events()

    def find_by_name(self, ui, name):
        """ Find the TraitsUI editor with the given name and return a new
        ``UIWrapper`` object for further interactions with the editor.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single name for retrieving a target on a UI.

        Returns
        -------
        wrapper : UIWrapper
        """
        return UIWrapper(
            target=ui,
            registries=self._registries,
            delay=self.delay,
        ).find_by_name(name=name)

    def find_by_id(self, ui, id):
        """ Find the TraitsUI editor with the given identifier and return a new
        ``UIWrapper`` object for further interactions with the editor.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        id : str
            Id for finding an item in the UI.

        Returns
        -------
        wrapper : UIWrapper
        """
        return UIWrapper(
            target=ui,
            registries=self._registries,
            delay=self.delay,
        ).find_by_id(id=id)