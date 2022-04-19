## Changelog Module edit_days

All the changes this project will be documented in this file

Note: 
This file contains changes to the form hr_payroll.view_hr_payslip_form of the pay_roll model

## Create Module Version 14 || 17-09-2021
https://www.ganemo.co/web#id=2449&action=510&model=project.task&view_type=form&cids=1&menu_id=360

### Views

### base_view

#### Changed
- inherit: hr_payroll.view_hr_payslip_form
    - In field worked_days_line_ids [replace], the "Readonly" attribute was modified to:
	    - work_entry_type_id
	    - name
	    - number_of_days
	    - number_of_hours
	    - amount
	    - is_paid
	    - sequence


