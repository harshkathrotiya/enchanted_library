
from datetime import datetime, timedelta
from enum import Enum, auto

from models.book import BookCondition, BookStatus

class PreservationAction(Enum):

    INSPECTION = auto()
    CLEANING = auto()
    REPAIR = auto()
    REBINDING = auto()
    RESTORATION = auto()
    DIGITIZATION = auto()
    DEACIDIFICATION = auto()
    CLIMATE_CONTROL = auto()

class PreservationRecord:


    def __init__(self, book_id, action, performed_by, notes=None):

        self._record_id = f"{book_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._book_id = book_id
        self._action = action
        self._performed_by = performed_by
        self._timestamp = datetime.now()
        self._notes = notes or ""
        self._before_condition = None
        self._after_condition = None

    @property
    def record_id(self):
        return self._record_id

    @property
    def book_id(self):
        return self._book_id

    @property
    def action(self):
        return self._action

    @property
    def performed_by(self):
        return self._performed_by

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    @property
    def before_condition(self):
        return self._before_condition

    @before_condition.setter
    def before_condition(self, value):
        if not isinstance(value, BookCondition):
            raise ValueError("Condition must be a BookCondition enum value")
        self._before_condition = value

    @property
    def after_condition(self):
        return self._after_condition

    @after_condition.setter
    def after_condition(self, value):
        if not isinstance(value, BookCondition):
            raise ValueError("Condition must be a BookCondition enum value")
        self._after_condition = value

    def __str__(self):
        return (
            f"Preservation Record {self._record_id}: {self._action.name} on Book {self._book_id} "
            f"by {self._performed_by} at {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

class PreservationSchedule:


    def __init__(self, book_id, action, interval_days, last_performed=None):

        self._schedule_id = f"{book_id}_{action.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self._book_id = book_id
        self._action = action
        self._interval_days = interval_days
        self._last_performed = last_performed
        self._next_due = self._calculate_next_due()
        self._active = True

    def _calculate_next_due(self):

        if self._last_performed:
            return self._last_performed + timedelta(days=self._interval_days)
        else:
            return datetime.now() + timedelta(days=self._interval_days)

    @property
    def schedule_id(self):
        return self._schedule_id

    @property
    def book_id(self):
        return self._book_id

    @property
    def action(self):
        return self._action

    @property
    def interval_days(self):
        return self._interval_days

    @interval_days.setter
    def interval_days(self, value):
        self._interval_days = value
        self._next_due = self._calculate_next_due()

    @property
    def last_performed(self):
        return self._last_performed

    @last_performed.setter
    def last_performed(self, value):
        self._last_performed = value
        self._next_due = self._calculate_next_due()

    @property
    def next_due(self):
        return self._next_due

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = bool(value)

    def is_due(self):

        return self._active and datetime.now() >= self._next_due

    def days_until_due(self):

        if not self._active:
            return None

        delta = self._next_due - datetime.now()
        return max(0, delta.days)

    def days_overdue(self):

        if not self._active or self._next_due > datetime.now():
            return 0

        delta = datetime.now() - self._next_due
        return delta.days

    def next_due_date(self):

        return self._next_due

    def __str__(self):
        return (
            f"Preservation Schedule {self._schedule_id}: {self._action.name} for Book {self._book_id} "
            f"every {self._interval_days} days, next due on {self._next_due.strftime('%Y-%m-%d')}"
        )

class PreservationService:


    def __init__(self, catalog=None, event_manager=None):

        self._catalog = catalog
        self._event_manager = event_manager
        self._restoration_queue = []
        self._restoration_history = []
        self._preservation_records = []
        self._preservation_schedules = []

        self._condition_thresholds = {
            'general': BookCondition.POOR,
            'rare': BookCondition.FAIR,
            'ancient': BookCondition.GOOD
        }
        self._restoration_durations = {
            'general': 7,
            'rare': 14,
            'ancient': 30
        }

    def check_needs_restoration(self, book):

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'

        threshold = self._condition_thresholds.get(book_type, BookCondition.POOR)

        return book.condition.value >= threshold.value

    def add_to_restoration_queue(self, book, priority=0, notes=None):

        for item in self._restoration_queue:
            if item['book_id'] == book.book_id:
                return {
                    'success': False,
                    'message': 'Book is already in the restoration queue'
                }

        if book.status != BookStatus.AVAILABLE and book.status != BookStatus.RESTORATION:
            return {
                'success': False,
                'message': f'Book is not available for restoration (current status: {book.status.name})'
            }

        from models.book import GeneralBook, RareBook, AncientScript

        if isinstance(book, GeneralBook):
            book_type = 'general'
        elif isinstance(book, RareBook):
            book_type = 'rare'
        elif isinstance(book, AncientScript):
            book_type = 'ancient'
        else:
            book_type = 'general'

        duration_days = self._restoration_durations.get(book_type, 7)

        queue_item = {
            'book_id': book.book_id,
            'title': book.title,
            'book_type': book_type,
            'condition': book.condition,
            'priority': priority,
            'notes': notes,
            'added_date': datetime.now(),
            'estimated_duration': duration_days,
            'estimated_completion': datetime.now() + timedelta(days=duration_days)
        }

        self._restoration_queue.append(queue_item)

        book.status = BookStatus.RESTORATION

        return {
            'success': True,
            'message': 'Book added to restoration queue',
            'estimated_completion': queue_item['estimated_completion']
        }

    def remove_from_restoration_queue(self, book_id):

        for i, item in enumerate(self._restoration_queue):
            if item['book_id'] == book_id:
                removed_item = self._restoration_queue.pop(i)

                return {
                    'success': True,
                    'message': 'Book removed from restoration queue',
                    'item': removed_item
                }

        return {
            'success': False,
            'message': 'Book not found in restoration queue'
        }

    def get_restoration_queue(self, sort_by='priority'):

        if sort_by == 'priority':
            return sorted(self._restoration_queue, key=lambda x: (-x['priority'], x['added_date']))
        elif sort_by == 'added_date':
            return sorted(self._restoration_queue, key=lambda x: x['added_date'])
        elif sort_by == 'estimated_completion':
            return sorted(self._restoration_queue, key=lambda x: x['estimated_completion'])
        else:
            return self._restoration_queue

    def complete_restoration(self, book_id, new_condition=None, notes=None):

        queue_item = None
        for i, item in enumerate(self._restoration_queue):
            if item['book_id'] == book_id:
                queue_item = self._restoration_queue.pop(i)
                break

        if not queue_item:
            return {
                'success': False,
                'message': 'Book not found in restoration queue'
            }

        history_item = {
            'book_id': book_id,
            'title': queue_item['title'],
            'book_type': queue_item['book_type'],
            'original_condition': queue_item['condition'],
            'new_condition': new_condition or BookCondition.GOOD,
            'start_date': queue_item['added_date'],
            'completion_date': datetime.now(),
            'duration': (datetime.now() - queue_item['added_date']).days,
            'notes': notes or queue_item['notes']
        }

        self._restoration_history.append(history_item)

        return {
            'success': True,
            'message': 'Restoration completed successfully',
            'history_item': history_item
        }

    def get_restoration_history(self, book_id=None, start_date=None, end_date=None):

        history = self._restoration_history

        if book_id:
            history = [item for item in history if item['book_id'] == book_id]

        if start_date:
            history = [item for item in history if item['completion_date'] >= start_date]

        if end_date:
            history = [item for item in history if item['completion_date'] <= end_date]

        return sorted(history, key=lambda x: x['completion_date'], reverse=True)

    def get_books_needing_restoration(self, catalog):

        books_needing_restoration = []

        for book in catalog._books.values():
            if self.check_needs_restoration(book) and book.status != BookStatus.RESTORATION:
                books_needing_restoration.append(book)

        return books_needing_restoration

    def get_restoration_recommendations(self, catalog):

        recommendations = []

        for book in catalog._books.values():
            if book.status == BookStatus.RESTORATION:
                continue

            from models.book import GeneralBook, RareBook, AncientScript

            if isinstance(book, GeneralBook):
                book_type = 'general'
            elif isinstance(book, RareBook):
                book_type = 'rare'
            elif isinstance(book, AncientScript):
                book_type = 'ancient'
            else:
                book_type = 'general'

            priority = 0

            type_factor = {'general': 1, 'rare': 2, 'ancient': 3}

            condition_factor = {
                BookCondition.EXCELLENT: 0,
                BookCondition.GOOD: 1,
                BookCondition.FAIR: 2,
                BookCondition.POOR: 3,
                BookCondition.CRITICAL: 4
            }

            priority = min(10, type_factor.get(book_type, 1) * condition_factor.get(book.condition, 0))

            if priority > 0:
                recommendations.append({
                    'book': book,
                    'priority': priority,
                    'reason': f"{book_type.capitalize()} book in {book.condition.name} condition"
                })

        return sorted(recommendations, key=lambda x: x['priority'], reverse=True)

    def add_preservation_record(self, book_id, action, performed_by, notes=None):

        book = None
        if self._catalog:
            book = self._catalog.get_book(book_id)

        record = PreservationRecord(book_id, action, performed_by, notes)

        if book:
            record.before_condition = book.condition

        self._preservation_records.append(record)

        return record

    def complete_preservation_action(self, record_id, new_condition, notes=None):

        record = None
        for r in self._preservation_records:
            if r.record_id == record_id:
                record = r
                break

        if not record:
            return False

        book = None
        if self._catalog:
            book = self._catalog.get_book(record.book_id)

        if book:
            book.condition = new_condition

            record.after_condition = new_condition
            if notes:
                record.notes += f"\nCompletion notes: {notes}"

            self._catalog.update_book(book)

            for schedule in self._preservation_schedules:
                if schedule.book_id == record.book_id and schedule.action == record.action:
                    schedule.last_performed = datetime.now()

            if book.status == BookStatus.RESTORATION:
                book.status = BookStatus.AVAILABLE
                self._catalog.update_book(book)

                if self._event_manager:
                    self._event_manager.book_restored(book)

            return True
        else:
            record.after_condition = new_condition
            if notes:
                record.notes += f"\nCompletion notes: {notes}"
            return True

    def schedule_preservation(self, book_id, action, interval_days, start_after_days=0):

        if self._catalog:
            book = self._catalog.get_book(book_id)
            if not book:
                raise ValueError(f"Book with ID {book_id} not found")

        if start_after_days > 0:
            last_performed = datetime.now() - timedelta(days=interval_days - start_after_days)
        else:
            last_performed = None

        schedule = PreservationSchedule(book_id, action, interval_days, last_performed)

        self._preservation_schedules.append(schedule)

        return schedule

    def get_due_preservation_actions(self):

        return [schedule for schedule in self._preservation_schedules if schedule.is_due()]

    def get_book_preservation_history(self, book_id):

        return [record for record in self._preservation_records if record.book_id == book_id]

    def get_book_preservation_schedules(self, book_id):

        return [schedule for schedule in self._preservation_schedules if schedule.book_id == book_id]

    def assess_book_condition(self, book_id, assessor_id):

        book = None
        if self._catalog:
            book = self._catalog.get_book(book_id)
            if not book:
                return {
                    'success': False,
                    'message': f"Book with ID {book_id} not found"
                }
        else:
            return {
                'success': False,
                'message': "Catalog not available for assessment"
            }

        record = self.add_preservation_record(
            book_id,
            PreservationAction.INSPECTION,
            assessor_id,
            "Routine condition assessment"
        )

        needs_restoration = self.check_needs_restoration(book)

        if needs_restoration:
            book.status = BookStatus.RESTORATION
            self._catalog.update_book(book)

            if self._event_manager:
                self._event_manager.book_needs_restoration(book)

        return {
            'success': True,
            'book_id': book_id,
            'current_condition': book.condition,
            'needs_restoration': needs_restoration,
            'assessment_record': record
        }

    def recommend_preservation_actions(self, book_id):

        book = None
        if self._catalog:
            book = self._catalog.get_book(book_id)
            if not book:
                return []
        else:
            return []

        recommended_actions = []

        if book.condition == BookCondition.EXCELLENT:
            recommended_actions.append({
                'action': PreservationAction.INSPECTION,
                'interval': 180,
                'priority': 'Low',
                'reason': 'Regular maintenance for excellent condition book'
            })

        elif book.condition == BookCondition.GOOD:
            recommended_actions.append({
                'action': PreservationAction.INSPECTION,
                'interval': 90,
                'priority': 'Low',
                'reason': 'Regular maintenance for good condition book'
            })
            recommended_actions.append({
                'action': PreservationAction.CLEANING,
                'interval': 180,
                'priority': 'Low',
                'reason': 'Preventive cleaning to maintain condition'
            })

        elif book.condition == BookCondition.FAIR:
            recommended_actions.append({
                'action': PreservationAction.INSPECTION,
                'interval': 60,
                'priority': 'Medium',
                'reason': 'Regular monitoring of fair condition book'
            })
            recommended_actions.append({
                'action': PreservationAction.CLEANING,
                'interval': 90,
                'priority': 'Medium',
                'reason': 'Regular cleaning to prevent deterioration'
            })
            recommended_actions.append({
                'action': PreservationAction.REPAIR,
                'interval': 365,
                'priority': 'Medium',
                'reason': 'Minor repairs to prevent further deterioration'
            })

        elif book.condition == BookCondition.POOR:
            recommended_actions.append({
                'action': PreservationAction.INSPECTION,
                'interval': 30,
                'priority': 'High',
                'reason': 'Close monitoring of poor condition book'
            })
            recommended_actions.append({
                'action': PreservationAction.REPAIR,
                'interval': 90,
                'priority': 'High',
                'reason': 'Regular repairs needed for poor condition'
            })
            recommended_actions.append({
                'action': PreservationAction.REBINDING,
                'interval': 0,
                'priority': 'High',
                'reason': 'Rebinding needed to preserve book structure'
            })

        elif book.condition == BookCondition.CRITICAL:
            recommended_actions.append({
                'action': PreservationAction.RESTORATION,
                'interval': 0,
                'priority': 'Urgent',
                'reason': 'Full restoration needed for critically damaged book'
            })
            recommended_actions.append({
                'action': PreservationAction.DIGITIZATION,
                'interval': 0,
                'priority': 'Urgent',
                'reason': 'Digitize content before further deterioration'
            })

        from models.book import RareBook, AncientScript

        if isinstance(book, RareBook):
            recommended_actions.append({
                'action': PreservationAction.CLIMATE_CONTROL,
                'interval': 7,
                'priority': 'High',
                'reason': 'Maintain optimal climate conditions for rare book'
            })

            if hasattr(book, 'estimated_value') and book.estimated_value:
                if book.estimated_value > 10000:
                    for action in recommended_actions:
                        if action['priority'] != 'Urgent':
                            action['priority'] = 'High'

        elif isinstance(book, AncientScript):
            recommended_actions.append({
                'action': PreservationAction.DEACIDIFICATION,
                'interval': 365,
                'priority': 'High',
                'reason': 'Prevent acid deterioration of ancient paper'
            })
            recommended_actions.append({
                'action': PreservationAction.CLIMATE_CONTROL,
                'interval': 1,
                'priority': 'Urgent',
                'reason': 'Strict climate control required for ancient manuscript'
            })

            if not any(a['action'] == PreservationAction.DIGITIZATION for a in recommended_actions):
                recommended_actions.append({
                    'action': PreservationAction.DIGITIZATION,
                    'interval': 0,
                    'priority': 'High',
                    'reason': 'Create digital backup of irreplaceable ancient script'
                })

        return recommended_actions
