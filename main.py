from model import Model


class Student(Model):
    first_name: str = 'text not null CHECK(length("first_name") <= 20 AND length("first_name") > 2)'
    last_name: str = 'text not null CHECK(length("first_name") <= 20 AND length("first_name") > 2)'
    subject: str = 'text not null CHECK(length("first_name") <= 20 AND length("first_name") > 2)'
    qualification: float = 'real not null CHECK("qualification" >= 0 AND "qualification" <= 10)' # type: ignore

    class Meta(Model.Meta):
        VERBOSE = False

    def __str__(self):
        return f'{(self.pk)} {self.first_name} {self.last_name} - {self.subject} - {self.qualification}'


def safe_float(value: str):
    try:
        return float(value)
    except ValueError:
        return None


def main():
    Student.setup()
    # Create a menu to add, update, delete, list students
    while True:
        print('1. Add student')
        print('2. Update student')
        print('3. Delete student')
        print('4. List students')
        print('5. Exit')
        choice = input('Enter your choice: ')
        if choice == '1':
            first_name = input('Enter first name: ').strip()
            last_name = input('Enter last name: ').strip()
            subject = input('Enter subject: ').strip()
            qualification = safe_float(input('Enter qualification: ').strip())

            student = Student(first_name=first_name, last_name=last_name,
                              subject=subject, qualification=qualification)
            try:
                student.save()
                print('Student added')
            except Exception as e:
                print(f'Error: {e}')
        elif choice == '2':
            try:
                pk = int(input('Enter student id: '))
            except ValueError:
                print('Invalid id')
                continue
            student = Student.get(pk)
            if not student:
                print('Student not found')
                continue
            print(f'Current student: {student}')
            kwargs = {}
            first_name = input(
                f'Enter first name ({student.first_name}): ').strip()
            kwargs['first_name'] = input(
                f'Enter first name ({student.first_name}): ').strip()
            kwargs['last_name'] = input(
                f'Enter last name ({student.last_name}): ').strip()
            kwargs['subject'] = input(
                f'Enter subject ({student.subject}): ').strip()
            kwargs['qualification'] = safe_float(
                input(f'Enter qualification ({student.qualification}): ').strip())
            for key, value in kwargs.copy().items():
                if value is None or value == '':
                    kwargs.pop(key)
            try:
                student.update(**kwargs)
                print('Student updated')
            except Exception as e:
                print(f'Error: {e}')
        elif choice == '3':
            try:
                pk = int(input('Enter student id: '))
            except ValueError:
                print('Invalid id')
                continue
            if Student.delete(pk):
                print('Student deleted')
            else:
                print('Student not found')
        elif choice == '4':
            students = Student.list()
            if len(students) == 0:
                print('No students found')
                continue
            print('Students:', *students, sep='\n\t')
        elif choice == '5':
            break
        else:
            print('Invalid choice')
        print()


if __name__ == '__main__':
    main()
