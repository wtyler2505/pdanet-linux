"""
Tests for connection state transition validation
Issue #56: Ensure state machine prevents illegal transitions
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from connection_manager import ConnectionState, VALID_TRANSITIONS, ConnectionManager


class TestStateTransitions:
    """Test state transition validation"""
    
    def test_valid_transitions_defined(self):
        """All states should have defined valid transitions"""
        for state in ConnectionState:
            assert state in VALID_TRANSITIONS, f"Missing transitions for {state.value}"
    
    def test_disconnected_to_connecting(self):
        """DISCONNECTED -> CONNECTING should be valid"""
        cm = ConnectionManager()
        assert cm.state == ConnectionState.DISCONNECTED
        result = cm._set_state(ConnectionState.CONNECTING)
        assert result is True
        assert cm.state == ConnectionState.CONNECTING
    
    def test_disconnected_to_connected_invalid(self):
        """DISCONNECTED -> CONNECTED should be invalid (must go through CONNECTING)"""
        cm = ConnectionManager()
        assert cm.state == ConnectionState.DISCONNECTED
        result = cm._set_state(ConnectionState.CONNECTED)
        assert result is False
        assert cm.state == ConnectionState.DISCONNECTED  # Should not change
    
    def test_connecting_to_connected(self):
        """CONNECTING -> CONNECTED should be valid"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        result = cm._set_state(ConnectionState.CONNECTED)
        assert result is True
        assert cm.state == ConnectionState.CONNECTED
    
    def test_connecting_to_error(self):
        """CONNECTING -> ERROR should be valid (connection failed)"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        result = cm._set_state(ConnectionState.ERROR)
        assert result is True
        assert cm.state == ConnectionState.ERROR
    
    def test_connected_to_disconnecting(self):
        """CONNECTED -> DISCONNECTING should be valid"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        result = cm._set_state(ConnectionState.DISCONNECTING)
        assert result is True
        assert cm.state == ConnectionState.DISCONNECTING
    
    def test_connected_to_disconnected_valid(self):
        """CONNECTED -> DISCONNECTED should be valid (network loss)"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        result = cm._set_state(ConnectionState.DISCONNECTED)
        assert result is True
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_disconnecting_to_disconnected(self):
        """DISCONNECTING -> DISCONNECTED should be valid"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        cm._set_state(ConnectionState.DISCONNECTING)
        result = cm._set_state(ConnectionState.DISCONNECTED)
        assert result is True
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_error_to_disconnected(self):
        """ERROR -> DISCONNECTED should be valid (recovery)"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.ERROR)
        result = cm._set_state(ConnectionState.DISCONNECTED)
        assert result is True
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_error_to_connecting(self):
        """ERROR -> CONNECTING should be valid (retry)"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.ERROR)
        result = cm._set_state(ConnectionState.CONNECTING)
        assert result is True
        assert cm.state == ConnectionState.CONNECTING
    
    def test_error_from_any_state(self):
        """ERROR should be reachable from any state (safety)"""
        for initial_state in ConnectionState:
            cm = ConnectionManager()
            # Force state to initial_state
            cm.state = initial_state
            # Try to transition to ERROR
            result = cm._set_state(ConnectionState.ERROR)
            # Should succeed from any state
            assert result is True, f"Failed to transition from {initial_state.value} to ERROR"
            assert cm.state == ConnectionState.ERROR
    
    def test_same_state_transition(self):
        """Transitioning to same state should be no-op"""
        cm = ConnectionManager()
        result = cm._set_state(ConnectionState.DISCONNECTED)
        assert result is True
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_connected_to_connecting_invalid(self):
        """CONNECTED -> CONNECTING should be invalid"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        result = cm._set_state(ConnectionState.CONNECTING)
        assert result is False
        assert cm.state == ConnectionState.CONNECTED  # Should not change
    
    def test_disconnecting_to_connecting_invalid(self):
        """DISCONNECTING -> CONNECTING should be invalid"""
        cm = ConnectionManager()
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        cm._set_state(ConnectionState.DISCONNECTING)
        result = cm._set_state(ConnectionState.CONNECTING)
        assert result is False
        assert cm.state == ConnectionState.DISCONNECTING  # Should not change
    
    def test_typical_connection_flow(self):
        """Test typical connect -> disconnect flow"""
        cm = ConnectionManager()
        
        # Start disconnected
        assert cm.state == ConnectionState.DISCONNECTED
        
        # Initiate connection
        assert cm._set_state(ConnectionState.CONNECTING)
        assert cm.state == ConnectionState.CONNECTING
        
        # Connection succeeds
        assert cm._set_state(ConnectionState.CONNECTED)
        assert cm.state == ConnectionState.CONNECTED
        
        # User disconnects
        assert cm._set_state(ConnectionState.DISCONNECTING)
        assert cm.state == ConnectionState.DISCONNECTING
        
        # Disconnection completes
        assert cm._set_state(ConnectionState.DISCONNECTED)
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_connection_failure_flow(self):
        """Test connection attempt that fails"""
        cm = ConnectionManager()
        
        # Start disconnected
        assert cm.state == ConnectionState.DISCONNECTED
        
        # Initiate connection
        assert cm._set_state(ConnectionState.CONNECTING)
        assert cm.state == ConnectionState.CONNECTING
        
        # Connection fails
        assert cm._set_state(ConnectionState.ERROR)
        assert cm.state == ConnectionState.ERROR
        
        # Recover to disconnected
        assert cm._set_state(ConnectionState.DISCONNECTED)
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_connection_cancellation_flow(self):
        """Test cancelling connection during CONNECTING"""
        cm = ConnectionManager()
        
        # Start connection
        cm._set_state(ConnectionState.CONNECTING)
        assert cm.state == ConnectionState.CONNECTING
        
        # User cancels
        assert cm._set_state(ConnectionState.DISCONNECTING)
        assert cm.state == ConnectionState.DISCONNECTING
        
        # Cancellation completes
        assert cm._set_state(ConnectionState.DISCONNECTED)
        assert cm.state == ConnectionState.DISCONNECTED
    
    def test_network_loss_flow(self):
        """Test sudden network loss (CONNECTED -> DISCONNECTED)"""
        cm = ConnectionManager()
        
        # Establish connection
        cm._set_state(ConnectionState.CONNECTING)
        cm._set_state(ConnectionState.CONNECTED)
        assert cm.state == ConnectionState.CONNECTED
        
        # Network loss detected
        assert cm._set_state(ConnectionState.DISCONNECTED)
        assert cm.state == ConnectionState.DISCONNECTED


class TestTransitionMatrix:
    """Test comprehensive transition matrix"""
    
    def test_all_invalid_transitions(self):
        """Test all combinations of invalid transitions"""
        invalid_pairs = []
        
        for from_state in ConnectionState:
            valid_to_states = VALID_TRANSITIONS.get(from_state, set())
            
            for to_state in ConnectionState:
                if to_state == from_state:
                    continue  # Same state is always ok (no-op)
                
                if to_state not in valid_to_states and to_state != ConnectionState.ERROR:
                    invalid_pairs.append((from_state, to_state))
        
        # Test each invalid transition
        for from_state, to_state in invalid_pairs:
            cm = ConnectionManager()
            cm.state = from_state  # Force state
            result = cm._set_state(to_state)
            assert result is False, f"Expected invalid: {from_state.value} -> {to_state.value}"
            assert cm.state == from_state, f"State should not change on invalid transition"
