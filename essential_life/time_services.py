__author__ = "PedroCR"


class TimeServices:
    def __init__(self, age, first_age, last_age):
        self.age = age
        self.first_age = first_age
        self.last_age = last_age

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.age}, {self.first_age}, {self.last_age})"

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, x):
        self.__age = x
        try:
            self.__set_past_time_service()
            self.__set_future_time_service()
            self.__set_future()
            self.__set_total_periods()
        except AttributeError as ae:
            pass

    @property
    def first_age(self):
        return self.__first_age

    @first_age.setter
    def first_age(self, x):
        self.__first_age = x
        try:
            self.__set_past_time_service()
            self.__set_future_time_service()
            self.__set_total_time_service()
            self.__set_future()
            self.__set_total_periods()
        except AttributeError as ae:
            pass

    @property
    def last_age(self):
        return self.__last_age

    @last_age.setter
    def last_age(self, x):
        self.__last_age = x
        try:
            self.__set_past_time_service()
            self.__set_future_time_service()
            self.__set_total_time_service()
            self.__set_future()
            self.__set_total_periods()
        except AttributeError as ae:
            pass

    @property
    def past_time_service(self):
        return self.__past_time_service

    def __set_past_time_service(self):
        self.__past_time_service = max(0, min(self.last_age - self.first_age, self.age - self.first_age))

    @property
    def future_time_service(self):
        return self.__future_time_service

    def __set_future_time_service(self):
        self.__future_time_service = max(0, min(self.last_age - self.age, self.last_age - self.first_age))

    @property
    def total_time_service(self):
        return self.__total_time_service

    def __set_total_time_service(self):
        self.__total_time_service = self.last_age - self.first_age

    @property
    def future(self):
        return self.__future

    def __set_future(self):
        self.__future = self.last_age - self.age

    @property
    def total_periods(self):
        return self.__total_periods

    def __set_total_periods(self):
        self.__total_periods = self.total_time_service + 1
