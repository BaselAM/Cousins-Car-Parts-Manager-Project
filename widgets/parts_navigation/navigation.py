"""
Navigation state management for the parts selection process.
Keeps track of what's selected at each step.
"""
from logger import get_logger

logger = get_logger('navigation_state')

class NavigationState:
    """
    Manages the navigation state for the parts selection process.
    Keeps track of selections at each step of the hierarchy.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all navigation state"""
        # Primary selection state
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
        """Get the selected brand"""
        return self._brand

    @brand.setter
    def brand(self, value):
        """Set the selected brand and reset dependent values"""
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
        """Get the selected model"""
        return self._model

    @model.setter
    def model(self, value):
        """Set the selected model and reset dependent values"""
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
        """Get the selected year"""
        return self._year

    @year.setter
    def year(self, value):
        """Set the selected year and reset dependent values"""
        if value != self._year:
            logger.debug(f"Year changed to: {value}")
            self._year = value

            # Reset dependent values
            self._category = None
            self._product = None
            self._details = None

    @property
    def car(self):
        """Get the complete car info"""
        return self._car

    @car.setter
    def car(self, value):
        """Set the complete car info and reset dependent values"""
        if value != self._car:
            logger.debug(f"Car changed to: {value}")
            self._car = value

            # Reset dependent values
            self._category = None
            self._product = None
            self._details = None

    @property
    def category(self):
        """Get the selected category"""
        return self._category

    @category.setter
    def category(self, value):
        """Set the selected category and reset dependent values"""
        if value != self._category:
            logger.debug(f"Category changed to: {value}")
            self._category = value

            # Reset dependent values
            self._product = None
            self._details = None

    @property
    def product(self):
        """Get the selected product"""
        return self._product

    @product.setter
    def product(self, value):
        """Set the selected product and reset dependent values"""
        if value != self._product:
            logger.debug(f"Product changed to: {value}")
            self._product = value

            # Reset dependent values
            self._details = None

    @property
    def details(self):
        """Get the product details"""
        return self._details

    @details.setter
    def details(self, value):
        """Set the product details"""
        if value != self._details:
            logger.debug(f"Details changed to: {value}")
            self._details = value

    def set_car(self, brand, model, year):
        """Set complete car information"""
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
        """Check if a brand has been selected"""
        return self._brand is not None

    def has_model(self):
        """Check if a model has been selected"""
        return self._model is not None

    def has_year(self):
        """Check if a year has been selected"""
        return self._year is not None

    def has_car(self):
        """Check if a complete car has been selected"""
        return self._car is not None

    def has_category(self):
        """Check if a category has been selected"""
        return self._category is not None

    def has_product(self):
        """Check if a product has been selected"""
        return self._product is not None

    def has_details(self):
        """Check if details have been selected"""
        return self._details is not None

    def is_complete(self):
        """Check if all required steps are complete"""
        return (self.has_car() and
                self.has_category() and
                self.has_product() and
                self.has_details())

    def get_step_data(self, step_index):
        """Get the data for a specific step"""
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