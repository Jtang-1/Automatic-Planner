import json
import jsonpickle


class Test ():
    def __init__(self, student, grade):
        self.student = [student]
        self.grade = grade

    def add_student(self, student):
        self.student.append(student)

    def get_students(self):
        return self.student

    def to_json(self):
        return jsonpickle.encode(self)

class Test2():
    def __init__(self,teacher, subject):
        self.teacher = teacher
        self.subject = [subject]

    def add_subject(self,subject):
        self.subject.append(subject)

    def get_subjects(self):
        return self.subject