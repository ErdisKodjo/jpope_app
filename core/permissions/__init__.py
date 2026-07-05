"""
Shared DRF permission classes.

Re-exports from the canonical definitions in ``apps.accounts.api.permissions``
to avoid the previous duplication where identical ``IsStudent``,
``IsCounselor``, ``IsSchoolRep``, and ``IsAdminOrReadOnly`` classes existed
in both ``core/permissions`` and ``apps/accounts/api/permissions``.
"""
from apps.accounts.api.permissions import (  # noqa: F401
    IsStudent,
    IsCounselor,
    IsSchoolRep,
    IsAdminOrReadOnly,
)
