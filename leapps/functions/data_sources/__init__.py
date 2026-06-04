"""Data source package"""

from .json_files import get_json_file_content, convert_json_file_to_namedtuple

__all__ = ["get_json_file_content", "convert_json_file_to_namedtuple"]
