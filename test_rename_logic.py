"""
Unit tests for rename logic implementation

This demonstrates how to properly test rename logic with comprehensive
test cases covering various scenarios.
"""

import unittest
from datetime import datetime
from rename_logic_example import RenameManager, Entity, RenameError


class TestRenameLogic(unittest.TestCase):
    """Test suite for rename logic functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.manager = RenameManager()
        self.entity1 = Entity("test_entity_1", "test_type")
        self.entity2 = Entity("test_entity_2", "test_type")
        self.manager.register_entity(self.entity1)
        self.manager.register_entity(self.entity2)
    
    def test_successful_rename(self):
        """Test that a valid rename operation succeeds"""
        result = self.manager.rename("test_entity_1", "renamed_entity")
        self.assertTrue(result)
        self.assertIn("renamed_entity", self.manager.list_entities())
        self.assertNotIn("test_entity_1", self.manager.list_entities())
    
    def test_rename_nonexistent_entity(self):
        """Test that renaming a non-existent entity raises an error"""
        with self.assertRaises(RenameError) as context:
            self.manager.rename("nonexistent", "new_name")
        self.assertIn("does not exist", str(context.exception))
    
    def test_rename_to_existing_name(self):
        """Test that renaming to an existing name raises an error"""
        with self.assertRaises(RenameError) as context:
            self.manager.rename("test_entity_1", "test_entity_2")
        self.assertIn("already exists", str(context.exception))
    
    def test_rename_to_empty_name(self):
        """Test that renaming to an empty name raises an error"""
        with self.assertRaises(RenameError) as context:
            self.manager.rename("test_entity_1", "")
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_rename_updates_references(self):
        """Test that rename updates references in other entities"""
        # Add a reference from entity1 to entity2
        self.entity1.add_reference("test_entity_2")
        
        # Rename entity2
        self.manager.rename("test_entity_2", "new_entity_2")
        
        # Check that entity1's reference was updated
        self.assertIn("new_entity_2", self.entity1.references)
        self.assertNotIn("test_entity_2", self.entity1.references)
    
    def test_rename_history_tracking(self):
        """Test that rename operations are tracked in history"""
        self.manager.rename("test_entity_1", "renamed_entity")
        history = self.manager.get_rename_history("renamed_entity")
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['old_name'], "test_entity_1")
        self.assertEqual(history[0]['new_name'], "renamed_entity")
    
    def test_dry_run_does_not_modify(self):
        """Test that dry run validates without modifying state"""
        result = self.manager.rename("test_entity_1", "new_name", dry_run=True)
        
        self.assertTrue(result)
        self.assertIn("test_entity_1", self.manager.list_entities())
        self.assertNotIn("new_name", self.manager.list_entities())
    
    def test_custom_validator(self):
        """Test that custom validators are executed"""
        def custom_validator(old_name, new_name):
            if "invalid" in new_name:
                raise RenameError("Name contains 'invalid'")
        
        self.manager.add_validator(custom_validator)
        
        with self.assertRaises(RenameError) as context:
            self.manager.rename("test_entity_1", "invalid_name")
        self.assertIn("contains 'invalid'", str(context.exception))
    
    def test_rename_listener_called(self):
        """Test that rename listeners are notified"""
        listener_called = []
        
        def test_listener(old_name, new_name, entity):
            listener_called.append((old_name, new_name, entity.name))
        
        self.manager.add_listener(test_listener)
        self.manager.rename("test_entity_1", "renamed_entity")
        
        self.assertEqual(len(listener_called), 1)
        self.assertEqual(listener_called[0][0], "test_entity_1")
        self.assertEqual(listener_called[0][1], "renamed_entity")
        self.assertEqual(listener_called[0][2], "renamed_entity")
    
    def test_entity_timestamp_updated(self):
        """Test that entity's updated_at timestamp is modified"""
        original_time = self.entity1.updated_at
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        self.manager.rename("test_entity_1", "renamed_entity")
        entity = self.manager.get_entity("renamed_entity")
        
        self.assertGreater(entity.updated_at, original_time)
    
    def test_multiple_renames_chain(self):
        """Test that an entity can be renamed multiple times"""
        self.manager.rename("test_entity_1", "first_rename")
        self.manager.rename("first_rename", "second_rename")
        self.manager.rename("second_rename", "third_rename")
        
        # Each rename creates a separate history entry
        # We should have 3 total entries in the complete history
        all_history = self.manager.history.history
        self.assertEqual(len(all_history), 3)
        
        # The entity should exist under its final name
        self.assertIn("third_rename", self.manager.list_entities())
    
    def test_reference_chain_updates(self):
        """Test that reference chains are properly updated"""
        entity3 = Entity("test_entity_3", "test_type")
        self.manager.register_entity(entity3)
        
        # Create reference chain: entity1 -> entity2 -> entity3
        self.entity1.add_reference("test_entity_2")
        self.entity2.add_reference("test_entity_3")
        
        # Rename entity3
        self.manager.rename("test_entity_3", "renamed_entity_3")
        
        # Check that entity2's reference was updated
        self.assertIn("renamed_entity_3", self.entity2.references)
    
    def test_get_entity_returns_correct_entity(self):
        """Test that get_entity returns the correct entity after rename"""
        self.manager.rename("test_entity_1", "renamed_entity")
        entity = self.manager.get_entity("renamed_entity")
        
        self.assertIsNotNone(entity)
        self.assertEqual(entity.name, "renamed_entity")
        self.assertIsNone(self.manager.get_entity("test_entity_1"))


class TestEntity(unittest.TestCase):
    """Test suite for Entity class"""
    
    def test_entity_creation(self):
        """Test that entity is created with correct attributes"""
        entity = Entity("test_name", "test_type")
        self.assertEqual(entity.name, "test_name")
        self.assertEqual(entity.entity_type, "test_type")
        self.assertIsInstance(entity.created_at, datetime)
        self.assertIsInstance(entity.updated_at, datetime)
    
    def test_add_reference(self):
        """Test adding references to an entity"""
        entity = Entity("test", "type")
        entity.add_reference("ref1")
        entity.add_reference("ref2")
        
        self.assertEqual(len(entity.references), 2)
        self.assertIn("ref1", entity.references)
        self.assertIn("ref2", entity.references)
    
    def test_add_duplicate_reference(self):
        """Test that duplicate references are not added"""
        entity = Entity("test", "type")
        entity.add_reference("ref1")
        entity.add_reference("ref1")
        
        self.assertEqual(len(entity.references), 1)
    
    def test_remove_reference(self):
        """Test removing references from an entity"""
        entity = Entity("test", "type")
        entity.add_reference("ref1")
        entity.remove_reference("ref1")
        
        self.assertEqual(len(entity.references), 0)
    
    def test_update_reference(self):
        """Test updating a reference"""
        entity = Entity("test", "type")
        entity.add_reference("old_ref")
        entity.update_reference("old_ref", "new_ref")
        
        self.assertIn("new_ref", entity.references)
        self.assertNotIn("old_ref", entity.references)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
