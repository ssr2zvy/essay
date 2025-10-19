# Quick Start Guide

## Answer to Your Question

**"Do you see any rename logic in the code? Where if an object is renamed it has some logic, or no?"**

**Answer: No**, the original codebase did not contain any rename logic. However, this repository now includes a complete implementation with examples.

## 5-Minute Quick Start

### 1. Try the Interactive Example

```bash
python3 rename_logic_example.py
```

This will demonstrate:
- Creating entities
- Successful renames with reference updates
- Error handling (name conflicts, invalid names)
- Dry-run validation
- History tracking

### 2. Run the Tests

```bash
python3 test_rename_logic.py
```

All 18 tests should pass, demonstrating the implementation's reliability.

### 3. Use in Your Code

```python
from rename_logic_example import RenameManager, Entity

# Create manager
manager = RenameManager()

# Create entities
doc = Entity("my_document", "document")
manager.register_entity(doc)

# Rename safely
try:
    manager.rename("my_document", "important_document")
    print("Success!")
except RenameError as e:
    print(f"Failed: {e}")
```

## Key Features Demonstrated

### ✅ Validation
```python
# Won't rename to existing name
manager.rename("doc1", "doc2")  # Raises error if doc2 exists
```

### ✅ Reference Updates
```python
# References automatically update
doc1.add_reference("project1")
manager.rename("project1", "main_project")
# doc1.references now contains "main_project"
```

### ✅ History Tracking
```python
# View rename history
history = manager.get_rename_history("main_project")
# Shows: project1 -> main_project at timestamp
```

### ✅ Dry Run
```python
# Check if rename would work without doing it
can_rename = manager.rename("doc", "new_doc", dry_run=True)
```

### ✅ Custom Validation
```python
# Add custom rules
manager.add_validator(
    lambda old, new: check_naming_convention(new)
)
```

### ✅ Event Listeners
```python
# Get notified of renames
manager.add_listener(
    lambda old, new, entity: log_change(old, new)
)
```

## Documentation Structure

📄 **README.md** - Overview and getting started  
📄 **QUICK_START.md** - This file (5-minute guide)  
📄 **ARCHITECTURE.md** - System design with diagrams  
📄 **RENAME_LOGIC_ANALYSIS.md** - Detailed analysis and patterns  
📄 **SUMMARY.md** - Complete summary of deliverables  

💻 **rename_logic_example.py** - Working implementation  
🧪 **test_rename_logic.py** - Comprehensive tests  

## Common Use Cases

### Use Case 1: File System
```python
file = Entity("document.txt", "file")
manager.rename("document.txt", "report.txt")
```

### Use Case 2: Database Entities
```python
user = Entity("user_123", "user")
manager.rename("user_123", "john_doe")
```

### Use Case 3: Project Objects
```python
project = Entity("project-alpha", "project")
manager.rename("project-alpha", "project-production")
```

## Error Handling

The system handles these errors:
- Non-existent source entity
- Duplicate target name
- Empty or whitespace-only names
- Custom validation failures

All errors raise `RenameError` with descriptive messages.

## What Makes This Implementation Special?

1. **Complete**: Handles all aspects of rename operations
2. **Safe**: Validates before changing anything
3. **Consistent**: Auto-updates all references
4. **Auditable**: Keeps full history
5. **Flexible**: Extensible with validators and listeners
6. **Reliable**: Rollback on any failure
7. **Tested**: 18 comprehensive tests

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Read [RENAME_LOGIC_ANALYSIS.md](RENAME_LOGIC_ANALYSIS.md) for patterns
3. Explore the code in `rename_logic_example.py`
4. Run and modify the tests in `test_rename_logic.py`

## Questions?

See the detailed documentation files for more information:
- System architecture: ARCHITECTURE.md
- Analysis and patterns: RENAME_LOGIC_ANALYSIS.md
- Complete summary: SUMMARY.md
