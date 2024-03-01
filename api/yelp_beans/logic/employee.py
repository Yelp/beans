from yelp_beans.models import Employee


def get_employee(work_email):
    return Employee.query.filter(Employee.work_email == work_email).first()
