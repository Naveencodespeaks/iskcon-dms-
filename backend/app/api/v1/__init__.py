"""Version 1 API routers."""

from .users import router as users_router  # noqa: F401
from .tenants import router as tenants_router  # noqa: F401
from .jobs import router as jobs_router  # noqa: F401
from .documents import router as documents_router  # noqa: F401
from .messages import router as messages_router  # noqa: F401
from .search import router as search_router  # noqa: F401