"""
Montu Manager Shared UI Widgets

Collection of reusable UI widgets used across Montu Manager applications.
Consolidated from individual widget files for better organization.
"""

# Import all widgets from their original locations
from ..pagination_widget import PaginationWidget
from ..advanced_search_widget import AdvancedSearchWidget

# Re-export for convenience
__all__ = [
    'PaginationWidget',
    'AdvancedSearchWidget'
]
