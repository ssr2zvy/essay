# Rename Logic Flow Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RenameManager                            │
│                                                              │
│  ┌───────────────────┐  ┌──────────────────┐               │
│  │   Validators      │  │    Listeners     │               │
│  │  - Existence      │  │  - Logger        │               │
│  │  - Conflicts      │  │  - Notifier      │               │
│  │  - Custom Rules   │  │  - Custom        │               │
│  └───────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Entities Collection                        │ │
│  │  {                                                      │ │
│  │    "doc1": Entity(name="doc1", refs=["project1"]),     │ │
│  │    "project1": Entity(name="project1", refs=[])        │ │
│  │  }                                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              RenameHistory                              │ │
│  │  [                                                      │ │
│  │    {old: "doc1", new: "document1", time: "..."},       │ │
│  │    {old: "project1", new: "main_project", time: "..."} │ │
│  │  ]                                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Rename Operation Flow

```
User calls: rename("old_name", "new_name")
│
├──> 1. VALIDATION PHASE
│    ├── Check if "old_name" exists ✓
│    ├── Check if "new_name" is available ✓
│    ├── Check if "new_name" is not empty ✓
│    └── Run custom validators ✓
│
├──> 2. DRY RUN CHECK
│    └── If dry_run=True, return success (no changes)
│
├──> 3. BACKUP PHASE
│    ├── Save entity state
│    └── Save all entity references
│
├──> 4. EXECUTION PHASE
│    ├── Remove old_name from entities dict
│    ├── Update entity.name = new_name
│    ├── Update entity.updated_at timestamp
│    └── Add new_name to entities dict
│
├──> 5. PROPAGATION PHASE
│    └── For each entity in system:
│         └── Update references from old_name to new_name
│
├──> 6. RECORDING PHASE
│    └── Add rename to history with timestamp
│
├──> 7. NOTIFICATION PHASE
│    └── Call all registered listeners
│
└──> 8. RETURN SUCCESS
     (or rollback to backup if any step fails)
```

## Error Handling with Rollback

```
Try:
    Execute rename operation
    ├── Validate
    ├── Backup
    ├── Execute
    ├── Propagate
    ├── Record
    └── Notify

Catch Exception:
    Rollback operation
    ├── Restore entity to old name
    ├── Remove new name if added
    ├── Restore all references
    └── Raise RenameError
```

## Reference Update Example

**Before Rename:**
```
Entities:
  - document1 (refs: ["my_project"])
  - document2 (refs: ["my_project"])
  - my_project (refs: [])

Call: rename("my_project", "awesome_project")
```

**After Rename:**
```
Entities:
  - document1 (refs: ["awesome_project"])  ← Updated!
  - document2 (refs: ["awesome_project"])  ← Updated!
  - awesome_project (refs: [])             ← Renamed!
```

## Component Interaction

```
┌──────────┐
│   User   │
└────┬─────┘
     │ rename("old", "new")
     ▼
┌────────────────┐
│ RenameManager  │
└────┬───────────┘
     │
     ├──> Validators
     │    └──> Custom Validation Logic
     │
     ├──> Entities
     │    ├──> Update Entity Name
     │    └──> Update All References
     │
     ├──> History
     │    └──> Record Operation
     │
     └──> Listeners
          └──> Notify External Systems
```

## Key Design Principles

1. **Validation First**: Check all constraints before making changes
2. **Atomic Operations**: Either complete fully or rollback completely
3. **Reference Integrity**: Automatically update all references
4. **Audit Trail**: Keep complete history of all operations
5. **Extensibility**: Support custom validators and listeners
6. **Safety**: Dry-run capability and rollback support

## Usage Patterns

### Pattern 1: Simple Rename
```python
manager.rename("old_name", "new_name")
```

### Pattern 2: Validated Rename
```python
# First check if rename is valid
if manager.rename("old", "new", dry_run=True):
    # Then perform actual rename
    manager.rename("old", "new")
```

### Pattern 3: Rename with Custom Validation
```python
manager.add_validator(lambda old, new: 
    validate_naming_convention(new))
manager.rename("old_name", "new_name")
```

### Pattern 4: Rename with Notifications
```python
manager.add_listener(lambda old, new, entity:
    notify_dependent_systems(old, new))
manager.rename("old_name", "new_name")
```

## Benefits of This Implementation

✅ **Safe**: Validates before executing  
✅ **Consistent**: Updates all references automatically  
✅ **Auditable**: Maintains complete history  
✅ **Extensible**: Custom validators and listeners  
✅ **Reliable**: Rollback on failure  
✅ **Testable**: Comprehensive test coverage  
