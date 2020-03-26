__author__ = "PedroCR"

import age


class PUC:
    def __init__(self, date_of_valuation, date_of_birth,
                 date_of_entry, date_of_term_cost, net_table=None, decrement=1,
                 waiting_first_instalment=0, waiting_last_instalment=0, waiting_first_payment=0):
        '''
        Creates an instance of a Projected Unit Credit amortization scheme
        :param date_of_valuation: date of valuation
        :param date_of_birth: date of birth
        :param date_of_entry: date of entry
        :param date_of_term_cost: date of the first payment of the term cost
        :param net_table: the net table, that is, the multidecrement table used
        :param decrement: the decrement that originates the payment
        :param waiting_first_instalment: how many periods we wait until we the first instalment to start amortizing the
        term cost
        :param waiting_last_instalment: how many periods we wait until we the last instalment to finish amortizing the
        term cost
        :param waiting_first_payment: how many periods, after the last instalment, until the first payment
        of the term cost
        '''
        self.date_of_valuation = date_of_valuation
        self.date_of_birth = date_of_birth
        self.date_of_entry = date_of_entry
        self.date_of_term_cost = date_of_term_cost
        self.net_table = net_table
        self.decrement = decrement
        self.waiting_first_instalment = waiting_first_instalment
        self.waiting_last_instalment = waiting_last_instalment
        self.waiting_first_payment = waiting_first_payment

        self.past_time_service = age.Age(date1=date_of_entry, date2=date_of_valuation)
        self.future_time_service = age.Age(date1=date_of_valuation, date2=date_of_term_cost)
        self.total_time_service = age.Age(date1=date_of_entry, date2=date_of_term_cost)

        dates_to_consider = list(range(self.past_time_service.date2.year, self.future_time_service.date2.year + 1))
        print(dates_to_consider)
