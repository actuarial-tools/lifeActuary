__author__ = "PedroCR"

import numpy as np
import age


class PVTermCost:
    def __init__(self, date_of_valuation, date_of_birth, date_of_entry,
                 age_of_term_cost, age_first_payment=None,
                 multi_table=None, decrement=None,
                 i=None,
                 age_of_projection=None):
        '''
        Creates an instance of a Present Value of a Term Cost object. This object will allow us to get an hold
        in all the information necessary to compute everything we need to valuate actuarial liabilities.
        :param date_of_valuation: date of valuation
        :param date_of_birth: date of birth
        :param date_of_entry: date of entry
        :param age_of_term_cost: date of the first payment of the term cost
        :param age_first_payment: how many periods, after the age of the term cost, until the first payment
        of the term cost
        :param multi_table: the net table, that is, the multidecrement table used
        :param decrement: the decrement that originates the payment
        :param i: the technical rate of interest
        :param age_of_projection: The age for each we are projecting the present value of the term cost if x lives to
        age_of_projection
        '''

        self.date_of_valuation = date_of_valuation
        self.date_of_birth = date_of_birth
        self.date_of_entry = date_of_entry

        self.multi_table = multi_table

        self.age_date_of_entry = age.Age(date1=self.date_of_birth, date2=self.date_of_entry)
        self.age_date_of_valuation = age.Age(date1=self.date_of_birth, date2=self.date_of_valuation)

        self.x = self.age_date_of_valuation.age_act()
        self.y_ = self.age_date_of_entry.age_f()[3]
        self.y = int(np.ceil(self.y_))
        self.past_time_service_years = self.x - self.y
        self.future_time_service_years = self.age_of_term_cost - self.x
        self.total_time_service_years = self.age_of_term_cost - self.y

        # this needs to be recomputed whenever changed
        self.age_of_term_cost = age_of_term_cost

        self.dates_ages_w = None

    @property
    def date_of_valuation(self):
        return self.date_of_valuation

    @property
    def date_of_birth(self):
        return self.date_of_birth

    @property
    def date_of_entry(self):
        return self.date_of_entry

    @property
    def multi_table(self):
        return self.multi_table

    @property
    def age_date_of_entry(self):
        return self.age_date_of_entry

    @property
    def age_date_of_valuation(self):
        return self.age_date_of_valuation

    @property
    def y_(self):
        return self.y_

    @property
    def y(self):
        return self.y

    @property
    def y_(self):
        return self.y_

    @property
    def x(self):
        return self.x

    @property
    def age_of_term_cost(self):
        return self.__age_of_term_cost

    @age_of_term_cost.setter
    def age_of_term_cost(self, atc):
        self.__age_of_term_cost = atc
        self.__future_time_service_years = self.__age_of_term_cost - self.x
        self.__total_time_service_years = self.__age_of_term_cost - self.y
        self.__waiting = None
        self.__dates_ages_w = None

    @property
    def dates_ages_w(self):
        return self.__dates_ages_w

    @dates_ages_w.setter
    def dates_ages_w(self):
        '''
        Creates all dates and ages from y to the largest w, expectedly the mortality table's w.
        '''
        # careful when counting years because of the actuarial ages
        max_w = [t[1].w for t in self.multi_table.unidecrement_tables.items()]
        max_w = max(max_w)
        dates_ages_w = [(age.Age(date1=self.date_of_valuation,
                                 date2=self.date_of_valuation).date_inc_years(j).date2.year, self.x + j)
                        for j in range(-self.past_time_service_years, max_w - self.x + 1)]
        self.__dates_ages_w = dates_ages_w

    def set_waiting_period(self, w=0):
        self.age_first_payment = self.age_of_term_cost + w
        self.waiting = w
        if self.dates_ages_w is None:
            self.create_dates_ages_w()

    def prob_survival(self, x1, x2):
        '''
        We compute the probability of survival from today (x) until age x, used to project liabilities,
        considering that the decrement occurred, that is, considering that (x) will enter the state
        defined by the decrement.
        :param x1: initial age
        :param x2: final age
        :return: The probability of survival considering all the decrements
        '''
        if x2 <= x2: return 1
        if x2 < self.age_of_term_cost:
            tpx_T = self.multi_table.net_table.tpx(x1, t=x2 - x1, method='udd')
        else:
            bool_decrement = bool(self.decrement)
            tpx_T = self.multi_table.net_table.tpx(x1, t=self.age_of_term_cost - x1 - bool_decrement,
                                                   method='udd') * \
                    self.multi_table.unidecrement_tables['mortality'].tpx(self.age_of_term_cost,
                                                                          t=x2 - self.age_of_term_cost, method='udd')
        return tpx_T

    def pvftc(self, x):
        '''
        Computes the Present Value of a Future Term Cost, that will allow us to use for all amortization schemes
        :param x: the age fo life (x). We consider that (x) is alive and if the decrement happens, it will be moved to
        to the other state. Hence, if there is a wanting period between the decrement occurrence and the first payment
        (x) should already be placed in the state corresponding to the decrement.
        For instance, if the decrement is disability, immediately after the decrement, (x) is moved to the state of
        disable and there is where the waiting period happens, if any.
        There are states where the decrement happens just due to survival up to that age, for instance, retirement.
        :return: The Present Value of Future Benefits
        '''
        if x < self.y: return 0  # no liability before entry age
        if self.decrement:
            q_d_x = self.multi_table.multidecrement_tables[self.decrement].tqx(self.age_of_term_cost - 1, t=1,
                                                                               method='udd')
        else:
            q_d_x = 1
        if x >= self.age_first_payment: return q_d_x  # full amortization
        if self.y <= x < self.age_of_term_cost:
            if self.decrement:
                tpx_T = self.multi_table.net_table.tpx(x, t=self.age_of_term_cost - x - 1, method='udd')
            else:
                tpx_T = self.multi_table.net_table.tpx(x, t=self.age_of_term_cost - x, method='udd')
            pvft = tpx_T * q_d_x * np.power(self.v, self.age_of_term_cost - x)
            if self.waiting > 0:
                tpx = self.multi_table.unidecrement_tables['mortality'].tpx(x=self.age_of_term_cost, t=self.waiting,
                                                                            method='udd')
                deferment = tpx * np.power(self.v, self.waiting)
                pvft *= deferment
        else:  # no more instalments but still compounding until the first payment
            waiting = self.age_first_payment - x
            tpx = self.multi_table.unidecrement_tables['mortality'].tpx(x, t=waiting, method='udd')
            deferment = np.power(self.v, waiting)
            pvft = q_d_x * tpx * deferment
        return pvft

    def pvftc_proj(self, x, px):
        '''
        Computes the Present Value of a Future Term Cost, that will allow us to use for all amortization schemes
        :param x: the age for life x. We consider that x is alive and if the decrement happens, it will be moved to
        to the other state. Hence, if there is a waiting period between the decrement occurrence and the first payment
        x should already be placed in the state corresponding to the decrement.
        For instance, if the decrement is disability, immediately after the decrement, x is moved to the state of
        disable and do the waiting, if any, until the first payment.
        There are states where the decrement happens just due to survival up to that age, for instance, retirement.
        :param px: the age where we project
        :return: The Present Value of Future Benefits
        '''
        dif_ages = x - self.y
        pvftc = self.pvftc(x)
        p = self.prob_survival(x, px)

        d = {'entry_year': self.dates_ages_w[0][0], 'entry_age': self.y,
             'year': self.dates_ages_w[dif_ages][0], 'age': self.dates_ages_w[dif_ages][1],
             'year_p': self.dates_ages_w[dif_ages][0], 'age_p': self.dates_ages_w[dif_ages][1],
             'age_of_term_cost': self.age_of_term_cost, 'age_first_payment': self.age_first_payment,
             'past_time_service_years': self.past_time_service_years + x - self.x,
             'futute_time_service_years': self.future_time_service_years - (x - self.x),
             'pvftc': pvftc, 'prob_surv_px': p, 'pvftc_p': pvftc * p}
        return d

    def sum_pvftc_proj(self, x, px, age_of_term_cost_init, age_of_term_cost_final, waiting=0):
        lst_tc_pj = []
        ages_term_costs = list(range(age_of_term_cost_init, age_of_term_cost_final + 1))
        for atc in ages_term_costs:
            self.age_of_term_cost = atc
            self.set_waiting_period(w=waiting)
            lst_tc_pj.append(self.pvftc_proj(x, px))
        return lst_tc_pj
