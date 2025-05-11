
from datetime import datetime, timedelta

from models.book import BookCondition

class FeeCalculator:

    def __init__(self):

        self._late_fee_rates = {
            'general': 0.25,
            'rare': 1.00,
            'ancient': 2.00
        }

        self._max_late_fees = {
            'general': 20.00,
            'rare': 50.00,
            'ancient': 100.00
        }

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

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'

        daily_rate = self._late_fee_rates.get(book_type, 0.25)
        max_fee = self._max_late_fees.get(book_type, 20.00)

        fee = days_overdue * daily_rate

        fee = min(fee, max_fee)

        return fee

    def calculate_damage_fee(self, original_condition, new_condition):

        if new_condition.value <= original_condition.value:
            return 0.0

        condition_fees = self._damage_fees.get(original_condition, {})
        fee = condition_fees.get(new_condition, 0.0)

        return fee

    def calculate_replacement_cost(self, book):

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'

        type_costs = self._replacement_costs.get(book_type, self._replacement_costs['general'])

        cost = type_costs.get(book.condition, type_costs[BookCondition.GOOD])

        if book_type == 'rare' and hasattr(book, 'estimated_value') and book.estimated_value:
            cost += book.estimated_value

        return cost

    def calculate_total_fees(self, lending_record, book, original_condition=None):

        fees = {
            'late_fee': 0.0,
            'damage_fee': 0.0,
            'replacement_cost': 0.0,
            'total': 0.0
        }

        if lending_record.is_overdue():
            days_overdue = lending_record.days_overdue()
            fees['late_fee'] = self.calculate_late_fee(book, days_overdue)

        if original_condition and original_condition != book.condition:
            fees['damage_fee'] = self.calculate_damage_fee(original_condition, book.condition)

        from models.lending import LendingStatus
        if lending_record.status == LendingStatus.LOST or book.condition == BookCondition.CRITICAL:
            fees['replacement_cost'] = self.calculate_replacement_cost(book)

        fees['total'] = fees['late_fee'] + fees['damage_fee'] + fees['replacement_cost']

        return fees

    def apply_discount(self, fee, discount_percentage):

        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")

        discount = fee * (discount_percentage / 100)
        return fee - discount

    def calculate_membership_fee(self, membership_type, duration_months):
        
        if membership_type == "Standard":
            monthly_fee = 5.00
        elif membership_type == "Premium":
            monthly_fee = 10.00
        else:
            raise ValueError("Invalid membership type")

        if duration_months >= 12:
            return monthly_fee * duration_months * 0.9
        elif duration_months >= 6:
            return monthly_fee * duration_months * 0.95
        else:
            return monthly_fee * duration_months

    def calculate_seasonal_discount(self, fee, season=None):
        
        if season is None:
            current_month = datetime.now().month
            if 3 <= current_month <= 5:
                season = "Spring"
            elif 6 <= current_month <= 8:
                season = "Summer"
            elif 9 <= current_month <= 11:
                season = "Fall"
            else:
                season = "Winter"

        if season == "Summer":
            return fee * 0.8
        elif season == "Winter":
            return fee * 0.85
        elif season == "Spring":
            return fee * 0.9
        elif season == "Fall":
            return fee * 0.9
        elif season == "Library Week":
            return fee * 0.75
        else:
            return fee

    def calculate_academic_discount(self, fee, user):
        
        from models.user import UserRole

        if user.get_role() == UserRole.SCHOLAR:
            if hasattr(user, 'academic_level'):
                if user.academic_level == "Distinguished":
                    return fee * 0.7
                elif user.academic_level == "Professor":
                    return fee * 0.8
                elif user.academic_level == "Graduate":
                    return fee * 0.9

        return fee
