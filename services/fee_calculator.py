"""
Fee Calculator implementation for the Enchanted Library system.
This module provides services for calculating late fees and other charges.
"""
from datetime import datetime, timedelta

from models.book import BookCondition


class FeeCalculator:
    """Service for calculating various fees in the library system."""
    
    def __init__(self):
        """Initialize the fee calculator with default rates."""
        # Base late fee rates per day for different book types
        self._late_fee_rates = {
            'general': 0.25,  # $0.25 per day for general books
            'rare': 1.00,     # $1.00 per day for rare books
            'ancient': 2.00   # $2.00 per day for ancient scripts (though they shouldn't be borrowed)
        }
        
        # Maximum late fees for different book types
        self._max_late_fees = {
            'general': 20.00,  # Maximum $20 late fee for general books
            'rare': 50.00,     # Maximum $50 late fee for rare books
            'ancient': 100.00  # Maximum $100 late fee for ancient scripts
        }
        
        # Damage fees based on condition change
        self._damage_fees = {
            BookCondition.EXCELLENT: {
                BookCondition.GOOD: 5.00,
                BookCondition.FAIR: 15.00,
                BookCondition.POOR: 30.00,
                BookCondition.CRITICAL: 50.00
            },
            BookCondition.GOOD: {
                BookCondition.FAIR: 10.00,
                BookCondition.POOR: 25.00,
                BookCondition.CRITICAL: 45.00
            },
            BookCondition.FAIR: {
                BookCondition.POOR: 15.00,
                BookCondition.CRITICAL: 35.00
            },
            BookCondition.POOR: {
                BookCondition.CRITICAL: 20.00
            }
        }
        
        # Replacement costs based on book type and condition
        self._replacement_costs = {
            'general': {
                BookCondition.EXCELLENT: 30.00,
                BookCondition.GOOD: 25.00,
                BookCondition.FAIR: 20.00,
                BookCondition.POOR: 15.00,
                BookCondition.CRITICAL: 10.00
            },
            'rare': {
                BookCondition.EXCELLENT: 100.00,
                BookCondition.GOOD: 80.00,
                BookCondition.FAIR: 60.00,
                BookCondition.POOR: 40.00,
                BookCondition.CRITICAL: 30.00
            },
            'ancient': {
                BookCondition.EXCELLENT: 500.00,
                BookCondition.GOOD: 400.00,
                BookCondition.FAIR: 300.00,
                BookCondition.POOR: 200.00,
                BookCondition.CRITICAL: 150.00
            }
        }
    
    def calculate_late_fee(self, book, days_overdue):
        """
        Calculate the late fee for an overdue book.
        
        Args:
            book: The overdue book
            days_overdue (int): Number of days the book is overdue
            
        Returns:
            float: The calculated late fee
        """
        # Determine the book type
        from models.book import GeneralBook, RareBook, AncientScript
        
        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'  # Default
        
        # Calculate the late fee
        daily_rate = self._late_fee_rates.get(book_type, 0.25)
        max_fee = self._max_late_fees.get(book_type, 20.00)
        
        fee = days_overdue * daily_rate
        
        # Apply maximum fee
        fee = min(fee, max_fee)
        
        return fee
    
    def calculate_damage_fee(self, original_condition, new_condition):
        """
        Calculate the fee for damaging a book.
        
        Args:
            original_condition (BookCondition): Original condition of the book
            new_condition (BookCondition): New condition of the book
            
        Returns:
            float: The calculated damage fee
        """
        # If the condition improved or stayed the same, no fee
        if new_condition.value <= original_condition.value:
            return 0.0
        
        # Look up the damage fee
        condition_fees = self._damage_fees.get(original_condition, {})
        fee = condition_fees.get(new_condition, 0.0)
        
        return fee
    
    def calculate_replacement_cost(self, book):
        """
        Calculate the replacement cost for a lost or severely damaged book.
        
        Args:
            book: The book to replace
            
        Returns:
            float: The calculated replacement cost
        """
        # Determine the book type
        from models.book import GeneralBook, RareBook, AncientScript
        
        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'  # Default
        
        # Get the replacement costs for this book type
        type_costs = self._replacement_costs.get(book_type, self._replacement_costs['general'])
        
        # Get the cost based on the book's condition
        cost = type_costs.get(book.condition, type_costs[BookCondition.GOOD])
        
        # For rare books, add the estimated value if available
        if book_type == 'rare' and hasattr(book, 'estimated_value') and book.estimated_value:
            cost += book.estimated_value
        
        return cost
    
    def calculate_total_fees(self, lending_record, book, original_condition=None):
        """
        Calculate the total fees for a lending record.
        
        Args:
            lending_record: The lending record
            book: The book that was borrowed
            original_condition (BookCondition, optional): Original condition of the book
            
        Returns:
            dict: Breakdown of the calculated fees
        """
        fees = {
            'late_fee': 0.0,
            'damage_fee': 0.0,
            'replacement_cost': 0.0,
            'total': 0.0
        }
        
        # Calculate late fee if the book is overdue
        if lending_record.is_overdue():
            days_overdue = lending_record.days_overdue()
            fees['late_fee'] = self.calculate_late_fee(book, days_overdue)
        
        # Calculate damage fee if the condition changed
        if original_condition and original_condition != book.condition:
            fees['damage_fee'] = self.calculate_damage_fee(original_condition, book.condition)
        
        # Calculate replacement cost if the book is lost or critically damaged
        from models.lending import LendingStatus
        if lending_record.status == LendingStatus.LOST or book.condition == BookCondition.CRITICAL:
            fees['replacement_cost'] = self.calculate_replacement_cost(book)
        
        # Calculate the total
        fees['total'] = fees['late_fee'] + fees['damage_fee'] + fees['replacement_cost']
        
        return fees
    
    def apply_discount(self, fee, discount_percentage):
        """
        Apply a discount to a fee.
        
        Args:
            fee (float): The original fee
            discount_percentage (float): Discount percentage (0-100)
            
        Returns:
            float: The discounted fee
        """
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        
        discount = fee * (discount_percentage / 100)
        return fee - discount
    
    def calculate_membership_fee(self, membership_type, duration_months):
        """
        Calculate the fee for a library membership.
        
        Args:
            membership_type (str): Type of membership (Standard or Premium)
            duration_months (int): Duration of the membership in months
            
        Returns:
            float: The calculated membership fee
        """
        if membership_type == "Standard":
            monthly_fee = 5.00
        elif membership_type == "Premium":
            monthly_fee = 10.00
        else:
            raise ValueError("Invalid membership type")
        
        return monthly_fee * duration_months
