"""{{ class_name or "GeneratedClass" }}

{{ description or "Auto-generated class using AICodeGen" }}
"""

from typing import Any, Optional


class {{ class_name or "GeneratedClass" }}:
    """{{ class_description or "Auto-generated class." }}"""
    
    def __init__(self{% if init_params %}, {{ init_params }}{% endif %}):
        """Initialize the {{ class_name or "GeneratedClass" }}."""
        {% if attributes %}
        {% for attr in attributes %}
        self.{{ attr.name }} = {{ attr.default or "None" }}
        {% endfor %}
        {% else %}
        pass
        {% endif %}
    
    {{ generated_code | indent(4) }}
    
    def __str__(self) -> str:
        """String representation of the {{ class_name or "GeneratedClass" }}."""
        return f"{{ class_name or "GeneratedClass" }}()"
    
    def __repr__(self) -> str:
        """Detailed representation of the {{ class_name or "GeneratedClass" }}."""
        return self.__str__()