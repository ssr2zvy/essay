"""
Example Rename Logic Implementation

This module demonstrates a complete rename logic implementation
with validation, error handling, and reference updates.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
import json


class RenameError(Exception):
    """Custom exception for rename operations"""
    pass


class RenameHistory:
    """Tracks rename history for audit purposes"""
    
    def __init__(self):
        self.history: List[Dict] = []
    
    def record(self, old_name: str, new_name: str, entity_type: str, timestamp: datetime):
        """Record a rename operation"""
        self.history.append({
            'old_name': old_name,
            'new_name': new_name,
            'entity_type': entity_type,
            'timestamp': timestamp.isoformat()
        })
    
    def get_history(self, entity_name: str) -> List[Dict]:
        """Get rename history for an entity"""
        return [
            record for record in self.history 
            if record['old_name'] == entity_name or record['new_name'] == entity_name
        ]


class Entity:
    """Base entity class with rename support"""
    
    def __init__(self, name: str, entity_type: str = 'generic'):
        self.name = name
        self.entity_type = entity_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.references: List[str] = []
    
    def add_reference(self, ref_name: str):
        """Add a reference to another entity"""
        if ref_name not in self.references:
            self.references.append(ref_name)
    
    def remove_reference(self, ref_name: str):
        """Remove a reference"""
        if ref_name in self.references:
            self.references.remove(ref_name)
    
    def update_reference(self, old_name: str, new_name: str):
        """Update a reference when another entity is renamed"""
        if old_name in self.references:
            idx = self.references.index(old_name)
            self.references[idx] = new_name


class RenameManager:
    """
    Manages rename operations with validation, rollback, and reference updates.
    
    This class demonstrates a complete rename logic implementation including:
    - Pre-rename validation
    - Reference tracking and updates
    - Rollback capability
    - History tracking
    - Event notifications
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.history = RenameHistory()
        self.rename_validators: List[Callable] = []
        self.rename_listeners: List[Callable] = []
    
    def register_entity(self, entity: Entity):
        """Register an entity for management"""
        if entity.name in self.entities:
            raise RenameError(f"Entity '{entity.name}' already exists")
        self.entities[entity.name] = entity
    
    def add_validator(self, validator: Callable):
        """Add a custom validator for rename operations"""
        self.rename_validators.append(validator)
    
    def add_listener(self, listener: Callable):
        """Add a listener to be notified of rename events"""
        self.rename_listeners.append(listener)
    
    def validate_rename(self, old_name: str, new_name: str) -> None:
        """
        Validate a rename operation
        
        Args:
            old_name: Current name of the entity
            new_name: Proposed new name
            
        Raises:
            RenameError: If validation fails
        """
        # Check if source exists
        if old_name not in self.entities:
            raise RenameError(f"Entity '{old_name}' does not exist")
        
        # Check if new name is already taken
        if new_name in self.entities:
            raise RenameError(f"Entity '{new_name}' already exists")
        
        # Check for empty name
        if not new_name or not new_name.strip():
            raise RenameError("New name cannot be empty")
        
        # Run custom validators
        for validator in self.rename_validators:
            validator(old_name, new_name)
    
    def update_references(self, old_name: str, new_name: str):
        """
        Update all references to the renamed entity
        
        Args:
            old_name: Old entity name
            new_name: New entity name
        """
        for entity in self.entities.values():
            entity.update_reference(old_name, new_name)
    
    def notify_listeners(self, old_name: str, new_name: str, entity: Entity):
        """Notify all registered listeners of the rename"""
        for listener in self.rename_listeners:
            listener(old_name, new_name, entity)
    
    def rename(self, old_name: str, new_name: str, dry_run: bool = False) -> bool:
        """
        Rename an entity with full validation and reference updates
        
        Args:
            old_name: Current name of the entity
            new_name: New name for the entity
            dry_run: If True, only validate without performing rename
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            RenameError: If validation fails or operation cannot be completed
        """
        # Validate the rename operation
        self.validate_rename(old_name, new_name)
        
        if dry_run:
            return True
        
        # Get the entity
        entity = self.entities[old_name]
        
        # Create backup for rollback
        backup_state = {
            'entity': entity,
            'references': {
                name: list(e.references) 
                for name, e in self.entities.items()
            }
        }
        
        try:
            # Perform the rename
            del self.entities[old_name]
            entity.name = new_name
            entity.updated_at = datetime.now()
            self.entities[new_name] = entity
            
            # Update all references
            self.update_references(old_name, new_name)
            
            # Record in history
            self.history.record(old_name, new_name, entity.entity_type, datetime.now())
            
            # Notify listeners
            self.notify_listeners(old_name, new_name, entity)
            
            return True
            
        except Exception as e:
            # Rollback on error
            self.entities[old_name] = backup_state['entity']
            if new_name in self.entities:
                del self.entities[new_name]
            
            # Restore references
            for name, refs in backup_state['references'].items():
                if name in self.entities:
                    self.entities[name].references = refs
            
            raise RenameError(f"Rename failed: {str(e)}")
    
    def get_entity(self, name: str) -> Optional[Entity]:
        """Get an entity by name"""
        return self.entities.get(name)
    
    def get_rename_history(self, entity_name: str) -> List[Dict]:
        """Get the rename history for an entity"""
        return self.history.get_history(entity_name)
    
    def list_entities(self) -> List[str]:
        """List all entity names"""
        return list(self.entities.keys())


# Example usage and demonstration
if __name__ == "__main__":
    print("=== Rename Logic Example ===\n")
    
    # Create a rename manager
    manager = RenameManager()
    
    # Add a custom validator
    def no_special_chars_validator(old_name: str, new_name: str):
        """Validator that disallows special characters"""
        if not new_name.replace('_', '').replace('-', '').isalnum():
            raise RenameError("Name can only contain alphanumeric characters, hyphens, and underscores")
    
    manager.add_validator(no_special_chars_validator)
    
    # Add a listener to log renames
    def log_rename(old_name: str, new_name: str, entity: Entity):
        """Listener that logs rename operations"""
        print(f"[LOG] Entity renamed: '{old_name}' -> '{new_name}' (type: {entity.entity_type})")
    
    manager.add_listener(log_rename)
    
    # Create some entities
    print("1. Creating entities...")
    doc1 = Entity("document1", "document")
    doc2 = Entity("document2", "document")
    project = Entity("my_project", "project")
    
    # Add references
    doc1.add_reference("my_project")
    doc2.add_reference("my_project")
    
    # Register entities
    manager.register_entity(doc1)
    manager.register_entity(doc2)
    manager.register_entity(project)
    
    print(f"   Created entities: {manager.list_entities()}")
    print(f"   document1 references: {doc1.references}\n")
    
    # Example 1: Successful rename
    print("2. Renaming 'my_project' to 'awesome_project'...")
    try:
        manager.rename("my_project", "awesome_project")
        print(f"   Success! Entities: {manager.list_entities()}")
        print(f"   document1 references updated: {doc1.references}\n")
    except RenameError as e:
        print(f"   Error: {e}\n")
    
    # Example 2: Failed rename (name already exists)
    print("3. Attempting to rename 'document1' to 'document2' (should fail)...")
    try:
        manager.rename("document1", "document2")
        print("   Success!")
    except RenameError as e:
        print(f"   Error (expected): {e}\n")
    
    # Example 3: Failed rename (invalid characters)
    print("4. Attempting to rename 'document1' to 'doc@#$' (should fail)...")
    try:
        manager.rename("document1", "doc@#$")
        print("   Success!")
    except RenameError as e:
        print(f"   Error (expected): {e}\n")
    
    # Example 4: Dry run
    print("5. Dry run: Check if 'document1' can be renamed to 'main_document'...")
    try:
        result = manager.rename("document1", "main_document", dry_run=True)
        print(f"   Dry run successful: {result}")
        print(f"   Entities (unchanged): {manager.list_entities()}\n")
    except RenameError as e:
        print(f"   Error: {e}\n")
    
    # Example 5: Actual rename after dry run
    print("6. Actually renaming 'document1' to 'main_document'...")
    try:
        manager.rename("document1", "main_document")
        print(f"   Success! Entities: {manager.list_entities()}\n")
    except RenameError as e:
        print(f"   Error: {e}\n")
    
    # Show rename history
    print("7. Rename history:")
    for entity_name in ["my_project", "awesome_project", "main_document"]:
        history = manager.get_rename_history(entity_name)
        if history:
            print(f"   {entity_name}:")
            for record in history:
                print(f"      {record['old_name']} -> {record['new_name']} at {record['timestamp']}")
