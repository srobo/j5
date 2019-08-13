"""
Type stubs for pytest.

Note that stubs are only written for the parts that we use.
"""

from typing import ContextManager, Optional, Type


# This function actually has more arguments than are specified here, and the
# context manager actually yields a _pytest._code.ExceptionInfo instead of None.
# We don't use either of these features, so I don't think its worth including
# them in our type stub. We can always change it later.
def raises(exc_type: Type[Exception], match: Optional[str] = None) -> ContextManager[None]:
    ...
