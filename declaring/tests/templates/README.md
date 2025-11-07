# Test Templates

This directory contains ready-to-use test templates for creating tests for new domains.

## Quick Start

When adding tests for a new domain:

1. **Copy the appropriate template** to the correct location
2. **Replace placeholders** with your domain-specific names
3. **Customize tests** to match your domain's functionality

## Template Files

| Template | Copy To | Purpose |
|----------|---------|---------|
| `test_models.py.template` | `tests/unit/{domain}/test_models.py` | Domain model tests |
| `test_schemas.py.template` | `tests/unit/{domain}/test_schemas.py` | Schema validation tests |
| `test_service.py.template` | `tests/unit/{domain}/test_service.py` | Service layer unit tests |
| `test_repository.py.template` | `tests/unit/{domain}/test_repository.py` | Repository unit tests |
| `test_service_integration.py.template` | `tests/integration/{domain}/test_service_integration.py` | Integration tests |
| `test_api.py.template` | `tests/api/test_{domain}_api.py` | API endpoint tests |
| `fixtures.py.template` | `tests/fixtures/{domain}s.py` | Test data fixtures |

## Placeholders

Replace these placeholders in all templates:

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Domain}` | Capitalized domain name | `Item` |
| `{domain}` | Lowercase domain name | `item` |
| `{domain}s` | Plural lowercase | `items` |
| `{entity}` | Entity variable name | `item` |
| `{DOMAIN}` | Uppercase domain | `ITEM` |

## Example: Adding Tests for "Products" Domain

### 1. Create Directory Structure

```bash
mkdir -p tests/unit/products
mkdir -p tests/integration/products
touch tests/unit/products/__init__.py
touch tests/integration/products/__init__.py
```

### 2. Copy and Customize Templates

```bash
# Unit tests
cp tests/templates/test_models.py.template tests/unit/products/test_models.py
cp tests/templates/test_schemas.py.template tests/unit/products/test_schemas.py
cp tests/templates/test_service.py.template tests/unit/products/test_service.py
cp tests/templates/test_repository.py.template tests/unit/products/test_repository.py

# Integration tests
cp tests/templates/test_service_integration.py.template tests/integration/products/test_service_integration.py

# API tests
cp tests/templates/test_api.py.template tests/api/test_products_api.py

# Fixtures
cp tests/templates/fixtures.py.template tests/fixtures/products.py
```

### 3. Replace Placeholders

In each file, replace:
- `{Domain}` → `Product`
- `{domain}` → `product`
- `{domain}s` → `products`
- `{entity}` → `product`

**Example using sed (Unix/Linux/Mac):**

```bash
# For all files in tests/unit/products/
for file in tests/unit/products/*.py; do
    sed -i '' 's/{Domain}/Product/g' "$file"
    sed -i '' 's/{domain}/product/g' "$file"
    sed -i '' 's/{entity}/product/g' "$file"
done
```

**Example using find & replace in editor:**
- VS Code: `Cmd/Ctrl + Shift + F` (find in files)
- Search for `{Domain}`, replace with `Product`
- Repeat for other placeholders

### 4. Customize for Your Domain

After replacing placeholders, customize:

1. **Add/remove fields** specific to your domain
2. **Add domain-specific tests** (e.g., business logic)
3. **Update validation rules** to match your schemas
4. **Add search/filter tests** if applicable

## Complete Example Workflow

```bash
# 1. Create directories
mkdir -p tests/unit/orders tests/integration/orders
touch tests/unit/orders/__init__.py
touch tests/integration/orders/__init__.py

# 2. Copy templates
cp tests/templates/test_models.py.template tests/unit/orders/test_models.py
cp tests/templates/test_service.py.template tests/unit/orders/test_service.py
cp tests/templates/fixtures.py.template tests/fixtures/orders.py

# 3. Replace placeholders (manual or automated)
# In your editor: Find/Replace {Domain} → Order, {domain} → order, etc.

# 4. Add domain-specific fields
# Edit tests/unit/orders/test_models.py:
#   - Add order_date field
#   - Add total_amount field
#   - Add customer_id field

# 5. Run tests
pytest tests/unit/orders -v

# 6. Check coverage
pytest tests/unit/orders --cov=app.orders --cov-report=term
```

## Tips for Agents

### Automated Placeholder Replacement

```python
import os
import re

def replace_placeholders(file_path, replacements):
    """Replace placeholders in a file."""
    with open(file_path, 'r') as f:
        content = f.read()

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    with open(file_path, 'w') as f:
        f.write(content)

# Usage
replacements = {
    '{Domain}': 'Product',
    '{domain}': 'product',
    '{domain}s': 'products',
    '{entity}': 'product',
    '{DOMAIN}': 'PRODUCT'
}

replace_placeholders('tests/unit/products/test_models.py', replacements)
```

### Checklist After Using Templates

- [ ] All placeholders replaced
- [ ] Domain-specific fields added
- [ ] Tests run successfully (`pytest tests/unit/{domain} -v`)
- [ ] Coverage meets minimum (80%+)
- [ ] Event tests included (for service layer)
- [ ] Edge cases tested
- [ ] Error cases tested

## Common Customizations

### Adding Custom Fields

```python
# In fixtures.py
def create_test_product(
    id: int = 1,
    name: str = "Test Product",
    category: str = "Electronics",  # ← Add custom field
    sku: str = "PROD-001",           # ← Add custom field
    # ... rest of fields
) -> Product:
    return Product(
        id=id,
        name=name,
        category=category,  # ← Include in constructor
        sku=sku,
        # ...
    )
```

### Adding Business Logic Tests

```python
# In test_models.py
@pytest.mark.unit
class TestProductBusinessLogic:
    """Test Product business logic methods."""

    def test_calculate_discount_applies_percentage(self):
        """Test discount calculation."""
        product = create_test_product(price=100.0)

        discounted_price = product.calculate_discount(10)  # 10%

        assert discounted_price == 90.0
```

### Adding Search Tests

```python
# In test_repository.py
@pytest.mark.unit
class TestProductRepositorySearch:
    """Test ProductRepository.search method."""

    @pytest.mark.asyncio
    async def test_search_by_category_returns_matches(self, test_db_session):
        """Test searching products by category."""
        repo = ProductRepository(test_db_session)
        await repo.create(create_test_product(name="Laptop", category="Electronics"))
        await repo.create(create_test_product(name="Desk", category="Furniture"))
        await test_db_session.commit()

        result = await repo.search(category="Electronics")

        assert len(result) == 1
        assert result[0].name == "Laptop"
```

## Further Reading

- [TESTING_GUIDE.md](../../TESTING_GUIDE.md) - Detailed testing patterns and examples
- [TESTING_STANDARDS.md](../../TESTING_STANDARDS.md) - Mandatory testing requirements
- [DEVELOPMENT_STANDARDS.md](../../DEVELOPMENT_STANDARDS.md) - TDD workflow

## Questions?

If you encounter issues with templates:

1. Check placeholder replacement is complete
2. Ensure imports match your domain structure
3. Verify fixtures are imported correctly
4. Run tests to see specific errors
5. Consult TESTING_GUIDE.md for patterns
