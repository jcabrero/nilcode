"""
Test code templates for different languages and frameworks.
"""

from langchain_core.tools import tool


# Python test templates
PYTEST_TEMPLATE = '''"""
Tests for {module_name}
"""

import pytest
from {module_path} import {functions}


class Test{ClassName}:
    """Test suite for {class_name}"""

    def test_{function_name}_success(self):
        """Test {function_name} with valid input"""
        # Arrange
        {arrange_code}

        # Act
        result = {function_name}({test_args})

        # Assert
        assert result is not None
        {assertions}

    def test_{function_name}_edge_cases(self):
        """Test {function_name} with edge cases"""
        # Test with None
        result = {function_name}(None)
        assert result is not None  # Adjust based on expected behavior

        # Test with empty input
        result = {function_name}({empty_args})
        assert result is not None  # Adjust based on expected behavior

    def test_{function_name}_error_handling(self):
        """Test {function_name} error handling"""
        with pytest.raises(Exception):
            {function_name}({invalid_args})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

UNITTEST_TEMPLATE = '''"""
Tests for {module_name}
"""

import unittest
from {module_path} import {functions}


class Test{ClassName}(unittest.TestCase):
    """Test suite for {class_name}"""

    def setUp(self):
        """Set up test fixtures"""
        {setup_code}

    def test_{function_name}_success(self):
        """Test {function_name} with valid input"""
        # Arrange
        {arrange_code}

        # Act
        result = {function_name}({test_args})

        # Assert
        self.assertIsNotNone(result)
        {assertions}

    def test_{function_name}_edge_cases(self):
        """Test {function_name} with edge cases"""
        result = {function_name}({empty_args})
        self.assertIsNotNone(result)

    def tearDown(self):
        """Clean up after tests"""
        pass


if __name__ == "__main__":
    unittest.main()
'''

# FastAPI test template
FASTAPI_TEST_TEMPLATE = '''"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from {main_module} import app

client = TestClient(app)


def test_{endpoint_name}_get():
    """Test GET {endpoint_path}"""
    response = client.get("{endpoint_path}")
    assert response.status_code == 200
    assert response.json() is not None


def test_{endpoint_name}_post():
    """Test POST {endpoint_path}"""
    test_data = {test_payload}
    response = client.post("{endpoint_path}", json=test_data)
    assert response.status_code in [200, 201]
    assert response.json() is not None


def test_{endpoint_name}_validation():
    """Test {endpoint_path} input validation"""
    invalid_data = {{}}
    response = client.post("{endpoint_path}", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_{endpoint_name}_not_found():
    """Test {endpoint_path} with non-existent resource"""
    response = client.get("{endpoint_path}/99999")
    assert response.status_code == 404
'''

# JavaScript/Jest test templates
JEST_TEMPLATE = '''/**
 * Tests for {module_name}
 */

import {{ {functions} }} from './{module_file}';

describe('{module_name}', () => {{
  describe('{function_name}', () => {{
    test('should work with valid input', () => {{
      // Arrange
      {arrange_code}

      // Act
      const result = {function_name}({test_args});

      // Assert
      expect(result).toBeDefined();
      {assertions}
    }});

    test('should handle edge cases', () => {{
      // Test with null
      const resultNull = {function_name}(null);
      expect(resultNull).toBeDefined();

      // Test with empty input
      const resultEmpty = {function_name}({empty_args});
      expect(resultEmpty).toBeDefined();
    }});

    test('should handle errors gracefully', () => {{
      expect(() => {{
        {function_name}({invalid_args});
      }}).toThrow();
    }});
  }});
}});
'''

# React component test template
REACT_TEST_TEMPLATE = '''/**
 * Tests for {component_name} component
 */

import {{ render, screen, fireEvent, waitFor }} from '@testing-library/react';
import {{ {component_name} }} from './{component_file}';

describe('{component_name}', () => {{
  test('renders without crashing', () => {{
    render(<{component_name} />);
    expect(screen.getByTestId('{test_id}')).toBeInTheDocument();
  }});

  test('displays correct content', () => {{
    render(<{component_name} {props} />);
    expect(screen.getByText(/{expected_text}/i)).toBeInTheDocument();
  }});

  test('handles user interaction', async () => {{
    render(<{component_name} />);

    // Simulate user action
    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Assert state change
    await waitFor(() => {{
      expect(screen.getByText(/{updated_text}/i)).toBeInTheDocument();
    }});
  }});

  test('handles props correctly', () => {{
    const testProps = {test_props};
    render(<{component_name} {{...testProps}} />);

    expect(screen.getByTestId('{test_id}')).toHaveAttribute('data-value', testProps.value);
  }});
}});
'''

# Vitest template
VITEST_TEMPLATE = '''/**
 * Tests for {module_name}
 */

import {{ describe, test, expect, beforeEach }} from 'vitest';
import {{ {functions} }} from './{module_file}';

describe('{module_name}', () => {{
  beforeEach(() => {{
    // Setup before each test
    {setup_code}
  }});

  describe('{function_name}', () => {{
    test('should work with valid input', () => {{
      const result = {function_name}({test_args});
      expect(result).toBeDefined();
      {assertions}
    }});

    test('should handle edge cases', () => {{
      expect({function_name}(null)).toBeDefined();
      expect({function_name}({empty_args})).toBeDefined();
    }});

    test('should throw on invalid input', () => {{
      expect(() => {function_name}({invalid_args})).toThrow();
    }});
  }});
}});
'''


@tool
def generate_python_test(
    module_name: str,
    module_path: str,
    function_name: str,
    framework: str = "pytest"
) -> str:
    """
    Generate Python test code for a module.

    Args:
        module_name: Name of the module being tested
        module_path: Import path for the module (e.g., 'app.utils')
        function_name: Name of the function to test
        framework: Testing framework ('pytest' or 'unittest')

    Returns:
        Generated test code
    """
    if framework == "pytest":
        template = PYTEST_TEMPLATE
    else:
        template = UNITTEST_TEMPLATE

    # Generate class name from function name
    class_name = ''.join(word.capitalize() for word in function_name.split('_'))

    return template.format(
        module_name=module_name,
        module_path=module_path,
        functions=function_name,
        ClassName=class_name,
        class_name=function_name,
        function_name=function_name,
        arrange_code='test_input = "test"',
        test_args='test_input',
        empty_args='""',
        invalid_args='None',
        assertions='# Add specific assertions here',
        setup_code='pass'
    )


@tool
def generate_fastapi_test(
    main_module: str,
    endpoint_path: str,
    endpoint_name: str
) -> str:
    """
    Generate FastAPI test code for an endpoint.

    Args:
        main_module: Import path for the main FastAPI app (e.g., 'app.main')
        endpoint_path: API endpoint path (e.g., '/api/users')
        endpoint_name: Name for the test function (e.g., 'users')

    Returns:
        Generated test code
    """
    return FASTAPI_TEST_TEMPLATE.format(
        main_module=main_module,
        endpoint_path=endpoint_path,
        endpoint_name=endpoint_name,
        test_payload='{"name": "Test User", "email": "test@example.com"}'
    )


@tool
def generate_javascript_test(
    module_name: str,
    module_file: str,
    function_name: str,
    framework: str = "jest"
) -> str:
    """
    Generate JavaScript test code.

    Args:
        module_name: Name of the module being tested
        module_file: File name without extension (e.g., 'utils')
        function_name: Name of the function to test
        framework: Testing framework ('jest' or 'vitest')

    Returns:
        Generated test code
    """
    if framework == "vitest":
        template = VITEST_TEMPLATE
    else:
        template = JEST_TEMPLATE

    return template.format(
        module_name=module_name,
        module_file=module_file,
        functions=function_name,
        function_name=function_name,
        arrange_code='const testInput = "test";',
        test_args='testInput',
        empty_args='""',
        invalid_args='null',
        assertions='// Add specific assertions here',
        setup_code='// Setup code here'
    )


@tool
def generate_react_test(
    component_name: str,
    component_file: str,
    test_id: str = "component-root"
) -> str:
    """
    Generate React component test code.

    Args:
        component_name: Name of the React component
        component_file: File name without extension (e.g., 'Button')
        test_id: Test ID for the component

    Returns:
        Generated test code
    """
    return REACT_TEST_TEMPLATE.format(
        component_name=component_name,
        component_file=component_file,
        test_id=test_id,
        props='title="Test"',
        expected_text='Test',
        updated_text='Clicked',
        test_props='{ value: "test", onClick: jest.fn() }'
    )


@tool
def get_test_framework_for_language(language: str) -> str:
    """
    Get recommended testing framework for a language.

    Args:
        language: Programming language (python, javascript, typescript)

    Returns:
        Recommended testing framework
    """
    frameworks = {
        "python": "pytest",
        "javascript": "jest",
        "typescript": "jest",
        "react": "react-testing-library",
        "vue": "vitest",
        "fastapi": "pytest + TestClient",
        "flask": "pytest + Flask test client",
        "django": "pytest-django"
    }

    return frameworks.get(language.lower(), "Unknown - please specify framework")


# Export all tools
test_template_tools = [
    generate_python_test,
    generate_fastapi_test,
    generate_javascript_test,
    generate_react_test,
    get_test_framework_for_language
]
