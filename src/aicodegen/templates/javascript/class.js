/**
 * {{ class_name || "GeneratedClass" }}
 * 
 * {{ description || "Auto-generated class using AICodeGen" }}
 */

class {{ class_name || "GeneratedClass" }} {
    /**
     * Initialize the {{ class_name || "GeneratedClass" }}
     * @param {Object} options - Configuration options
     */
    constructor(options = {}) {
        {% if attributes %}
        {% for attr in attributes %}
        this.{{ attr.name }} = options.{{ attr.name }} || {{ attr.default || "null" }};
        {% endfor %}
        {% else %}
        this.options = options;
        {% endif %}
    }
    
    {{ generated_code | indent(4) }}
    
    /**
     * String representation of the {{ class_name || "GeneratedClass" }}
     * @returns {string} String representation
     */
    toString() {
        return `{{ class_name || "GeneratedClass" }}()`;
    }
}

module.exports = {{ class_name || "GeneratedClass" }};