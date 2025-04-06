"""
Navigation state management for the parts selection process.

This module provides state tracking for the parts navigation flow,
ensuring proper dependencies between steps and maintaining selection history.
"""
from logger import get_logger

logger = get_logger('parts_navigation.state')


class NavigationState:
    """
    Manages the navigation state for the parts selection process.

    Tracks the state of each step in the navigation flow and ensures
    that steps are properly connected with the right dependencies.
    """

    def __init__(self):
        """Initialize with empty state."""
        self.reset()

    def reset(self):
        """Reset all navigation state to starting values."""
        # Step selection data
        self._brand = None
        self._model = None
        self._year = None
        self._car = None  # Combined brand, model, year
        self._category = None
        self._product = None
        self._details = None

        # Search state
        self.search_results = None
        self.direct_selection = False  # Flag for direct selection from search

        logger.debug("Navigation state reset")

    @property
    def brand(self):
        """Get the selected brand."""
        return self._brand

    @brand.setter
    def brand(self, value):
        """
        Set the selected brand and reset dependent values.

        Args:
            value: Brand data dictionary
        """
        if value != self._brand:
            logger.debug(f"Brand changed to: {value}")
            self._brand = value

            # Reset dependent values
            self._model = None
            self._year = None
            self._car = None
            self._category = None
            self._product = None
            self._details = None

    @property
    def model(self):
        """Get the selected model."""
        return self._model

    @model.setter
    def model(self, value):
        """
        Set the selected model and reset dependent values.

        Args:
            value: Model data dictionary
        """
        if value != self._model:
            logger.debug(f"Model changed to: {value}")
            self._model = value

            # Reset dependent values
            self._year = None
            self._car = None
            self._category = None
            self._product = None
            self._details = None

    @property
    def year(self):
        """Get the selected year."""
        return self._year

    @year.setter
    def year(self, value):
        """
        Set the selected year and reset dependent values.

        Args:
            value: Year data dictionary
        """
        if value != self._year:
            logger.debug(f"Year changed to: {value}")
            self._year = value

            # Reset dependent values
            self._category = None
            self._product = None
            self._details = None

    @property
    def car(self):
        """Get the complete car info (brand, model, year)."""
        return self._car

    @car.setter
    def car(self, value):
        """
        Set the complete car info and reset dependent values.

        Args:
            value: Car data dictionary with brand, model, year
        """
        if value != self._car:
            logger.debug(f"Car changed to: {value}")
            self._car = value

            # Reset dependent values
            self._category = None
            self._product = None
            self._details = None

    @property
    def category(self):
        """Get the selected category."""
        return self._category

    @category.setter
    def category(self, value):
        """
        Set the selected category and reset dependent values.

        Args:
            value: Category data dictionary
        """
        if value != self._category:
            logger.debug(f"Category changed to: {value}")
            self._category = value

            # Reset dependent values
            self._product = None
            self._details = None

    @property
    def product(self):
        """Get the selected product."""
        return self._product

    @product.setter
    def product(self, value):
        """
        Set the selected product and reset dependent values.

        Args:
            value: Product data dictionary
        """
        if value != self._product:
            logger.debug(f"Product changed to: {value}")
            self._product = value

            # Reset dependent values
            self._details = None

    @property
    def details(self):
        """Get the product details configuration."""
        return self._details

    @details.setter
    def details(self, value):
        """
        Set the product details.

        Args:
            value: Details data dictionary
        """
        if value != self._details:
            logger.debug(f"Details changed to: {value}")
            self._details = value

    def set_car(self, brand, model, year):
        """
        Set complete car information.

        Args:
            brand: Brand data dictionary
            model: Model data dictionary
            year: Year data dictionary
        """
        self._brand = brand
        self._model = model
        self._year = year
        self._car = {
            'brand': brand['brand'],
            'model': model['model'],
            'year': year['year']
        }
        logger.debug(f"Complete car set: {self._car}")

    def has_brand(self):
        """Check if a brand has been selected."""
        return self._brand is not None

    def has_model(self):
        """Check if a model has been selected."""
        return self._model is not None

    def has_year(self):
        """Check if a year has been selected."""
        return self._year is not None

    def has_car(self):
        """Check if a complete car has been selected."""
        return self._car is not None

    def has_category(self):
        """Check if a category has been selected."""
        return self._category is not None

    def has_product(self):
        """Check if a product has been selected."""
        return self._product is not None

    def has_details(self):
        """Check if details have been selected."""
        return self._details is not None

    def is_complete(self):
        """Check if all required steps are complete."""
        return (self.has_car() and
                self.has_category() and
                self.has_product() and
                self.has_details())

    def get_step_data(self, step_index):
        """
        Get the data for a specific step.

        Args:
            step_index: Index of the step (0-6)

        Returns:
            dict: Step data or None if not set
        """
        if step_index == 0:
            return self._brand
        elif step_index == 1:
            return self._model
        elif step_index == 2:
            return self._year
        elif step_index == 3:
            return self._category
        elif step_index == 4:
            return self._product
        elif step_index == 5:
            return self._details
        return None

    def get_dependency_chain(self, step_index):
        """
        Get the chain of dependencies required for a step.

        Args:
            step_index: Index of the step

        Returns:
            list: Indices of steps this step depends on
        """
        if step_index == 0:  # Brand step has no dependencies
            return []
        elif step_index == 1:  # Model depends on brand
            return [0]
        elif step_index == 2:  # Year depends on model and brand
            return [0, 1]
        elif step_index == 3:  # Category depends on complete car
            return [0, 1, 2]
        elif step_index == 4:  # Product depends on category and car
            return [0, 1, 2, 3]
        elif step_index == 5:  # Details depends on product
            return [0, 1, 2, 3, 4]
        elif step_index == 6:  # Summary depends on details
            return [0, 1, 2, 3, 4, 5]
        return []

    def can_navigate_to_step(self, step_index):
        """
        Check if navigation to a step is possible.

        Args:
            step_index: Target step index

        Returns:
            bool: True if navigation is possible
        """
        # Can always navigate to step 0
        if step_index == 0:
            return True

        # For other steps, check that all prerequisites are met
        dependencies = self.get_dependency_chain(step_index)

        # For each dependency, check if data exists
        for dep_step in dependencies:
            if not self.get_step_data(dep_step):
                return False

        return True