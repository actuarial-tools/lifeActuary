__author__ = "PedroCR"

from soa_tables import read_soa_table_xml as rst
from disability_tables import disability_tables as dt
from turnover_tables import turnover_tables as tt
import mortality_table as mt
from multidecrement_table import MultiDecrementTable as mdt
import age
from amortization_schemes.projected_unit_credit import puc
from matplotlib import pyplot as plt

soa_TV7377 = rst.SoaTable('../soa_tables/TV7377.xml')
soa_GRF95 = rst.SoaTable('../soa_tables/GRF95.xml')
ekv80 = dt.EVK_80
ekv80_70 = dt.EVK_80_ext_70
pcr1 = tt.pcr_turnover
pcr2 = tt.pcr_turnover_65

mt_GRF95 = mt.MortalityTable(mt=soa_GRF95.table_qx)
mt_TV7377 = mt.MortalityTable(mt=soa_TV7377.table_qx)
dt_ekv80 = mt.MortalityTable(mt=ekv80, last_q=0)
tt_pcr = mt.MortalityTable(mt=pcr1, last_q=0)

tables_unidecrement = {'mortality': mt_TV7377, 'disability': dt_ekv80, 'turnover': tt_pcr}

tables_multidecrement = mdt(dict_tables=tables_unidecrement)
tables_multidecrement.create_udd_multidecrement_table()

dict_dates = {'date_of_birth': '1977-03-12', 'date_of_entry': '1997-05-15'}
date_of_valuation = '2019-12-31'

dates_for_term_cost = age.Age(date1=dict_dates['date_of_birth'], date2=dict_dates['date_of_birth']).date_inc_years(55)
age_term_cost_years = dates_for_term_cost.age_act()
puc_d = puc.PUC(date_of_valuation=date_of_valuation, date_of_birth=dict_dates['date_of_birth'],
                date_of_entry=dict_dates['date_of_entry'], age_of_term_cost=age_term_cost_years,
                multi_table=tables_multidecrement, decrement='disability', i=2,
                age_first_instalment=None, age_last_instalment=None, age_first_payment=None)

puc_d.set_default_waiting_periods()

# compute pvfb
x = 45
print(f"PVBT({puc_d.y}, {puc_d.x}, {puc_d.age_of_term_cost}|{x})={puc_d.pvtc(x=x)}")
print(f"PVBT({puc_d.y}, {puc_d.x}, {puc_d.age_of_term_cost}|{puc_d.x})={puc_d.pvtc_x()}")

# test
test = puc_d.test()

pvfb_all_d = puc_d.vec_pvtc_y_first_payment()
al_all_d = puc_d.al_all_ages()
nc_all_d = puc_d.nc_all_ages()
fig, ax = fig, axs = plt.subplots()
plt.plot(pvfb_all_d[1][:], pvfb_all_d[2][:], 'o-', label='pvfb disability')
plt.plot(al_all_d[1][:], al_all_d[2][:], 'o-', mfc='none', label='al disability')
plt.plot(nc_all_d[1][:], nc_all_d[2][:], 'o--', mfc='none', label='nc disability')
plt.title('Disability')
plt.legend()

# print(pvfb_all_d)
# print(al_all_d)
# print(nc_all_d)


# projection
pvfb_all_d = puc_d.vec_pvtc_y_w_proj()
al_all_d = puc_d.al_proj_all_ages_proj()
nc_all_d = puc_d.nc_proj_all_ages_proj()
fig, ax = fig, axs = plt.subplots()
plt.plot(pvfb_all_d[1][:], pvfb_all_d[2][:], 'o-', label='pvfb disability projected')
plt.plot(al_all_d[1][:], al_all_d[2][:], 'o-', mfc='none', label='al disability projected')
plt.plot(nc_all_d[1][:], nc_all_d[2][:], 'o--', mfc='none', label='nc disability projected')
plt.title('Disability Projected')
plt.legend()

'''



Retirement
'''
print('\n')
print('Testing for Retirement at 65')
age_retirement_65 = age.Age(date1=dict_dates['date_of_birth'], date2=dict_dates['date_of_birth']).date_inc_years(65)
puc_retirement = puc.PUC(date_of_valuation=date_of_valuation, date_of_birth=dict_dates['date_of_birth'],
                         date_of_entry=dict_dates['date_of_entry'], age_of_term_cost=65,
                         multi_table=tables_multidecrement, decrement=None, i=2,
                         age_first_instalment=None, age_last_instalment=None, age_first_payment=None)

puc_retirement.set_default_waiting_periods()

# compute pvfb
x = 65
print(
    f"PVBT({puc_retirement.y}, {puc_retirement.x}, {puc_retirement.age_of_term_cost}|{x})={puc_retirement.pvtc(x=x)}")
print(
    f"PVBT({puc_retirement.y}, {puc_retirement.x}, {puc_retirement.age_of_term_cost}|{puc_retirement.x})={puc_retirement.pvtc_x()}")

# test
test = puc_retirement.test()

pvfb_all_retirement = puc_retirement.vec_pvtc_y_first_payment()
al_all_retirement = puc_retirement.al_all_ages()
nc_all_retirement = puc_retirement.nc_all_ages()
fig, ax = fig, axs = plt.subplots()
plt.plot(pvfb_all_retirement[1], pvfb_all_retirement[2], 'o-', label='pvfb retirement')
plt.plot(al_all_retirement[1], al_all_retirement[2], 'o-', mfc='none', label='al retirement')
plt.plot(nc_all_retirement[1], nc_all_retirement[2], 'o-', mfc='none', label='nc retirement')
plt.title('Retirement')
plt.legend()

# projection
pvfb_all_retirement = puc_retirement.vec_pvtc_y_w_proj()
al_all_retirement = puc_retirement.al_proj_all_ages_proj()
nc_all_retirement = puc_retirement.nc_proj_all_ages_proj()
fig, ax = fig, axs = plt.subplots()
plt.plot(pvfb_all_retirement[1][:], pvfb_all_retirement[2][:], 'o-', label='pvfb retirement projected')
plt.plot(al_all_retirement[1][:], al_all_retirement[2][:], 'o-', mfc='none', label='al retirement projected')
plt.plot(nc_all_retirement[1][:], nc_all_retirement[2][:], 'o--', mfc='none', label='nc retirement projected')
plt.title('Retirement Projected')
plt.legend()
plt.show()
