from django.core.management import BaseCommand
import random, json
from faker import Faker
from datetime import timedelta
from users.models import User, Parent, Teacher, Student, CustomPermission
from school.models import Term, School, Class, Lesson
from subscription.models import Benefit, Plan


class Command(BaseCommand):
    
    help = 'Generate fake data'
  
    def handle(self, *args, **kwargs):
        fake = Faker()
        with open('sample_data.json', 'r') as file:
            data = json.load(file)

            # create data for benefit 
            for benefit in data['benefit']:
                Benefit.objects.get_or_create(
                    name=benefit['name'],
                    description=benefit['description']
                )

            # create data for plan
            for plan in data['plan']:
                plan_instance, created = Plan.objects.get_or_create(
                    name=plan['name'],
                    price=plan['price']
                )
                benefit_ids = plan['benefits']
                plan_instance.benefits.set(benefit_ids)

            # create permission
            for permission in data['permission']:
                CustomPermission.objects.get_or_create(
                    code_name=permission['code_name'],
                    code_id=permission['code_id']
                )
            
        for i in range(10):

            # create user data
            email = fake.email()
            username = email
            _pass = email.split('@')[0]
            password = _pass
            role = (i % 7) + 1
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=fake.random_int(min=1, max=2),
                mobile_no=fake.phone_number(),
                address=fake.address(),
                zip_code=fake.zipcode()
                )
            user.set_password(password) 
            user.save()

            # create parent data
            if role == User.Parent:
                Parent.objects.create(
                    user=user,
                    occupation=fake.job(),
                    assigned_students=fake.random_int(min=1, max=5),   
                    nin=fake.uuid4(),
                    address=fake.street_address(),
                    city=fake.city(),
                    region=fake.state(),
                    country=fake.country(),
                )

            # create class data
            start_date = fake.date_between(start_date='-1y')
            Class.objects.get_or_create(
                name=fake.word() + ' Class',
                start_date=start_date,
                end_date=fake.date_between(start_date=start_date, end_date='+3m')
            )
    
            # create teacher data
            if role == User.Teacher:
                Teacher.objects.get_or_create(
                    user=user,
                    teacher_id=fake.unique.random_number(digits=5),
                    joining_date=fake.date_between(start_date='-5y', end_date='today'),   
                    year_of_experience=fake.random_int(min=1, max=20),
                    qualification=fake.job(),
                    main_class=fake.random.choice(Class.objects.all()),
                    address=fake.street_address(),
                    city=fake.city(),
                    region=fake.state(),
                    country=fake.country(),
                )

            # create student data
            if role == User.Student:
                Student.objects.get_or_create(
                    user=user,
                    parent=fake.random.choice(Parent.objects.all()),
                    id_no=fake.unique.random_number(digits=3),   
                    _class=fake.random.choice(Class.objects.all()),
                    address=fake.street_address(),
                    city=fake.city(),
                    region=fake.state(),
                    country=fake.country(),
                )
            
            # create term data
            term, created = Term.objects.get_or_create(
                term_start_date= fake.date_between(start_date='-1y', end_date='+1y'),
                mid_term_break=start_date + timedelta(weeks=6),
                term_end_date=start_date + timedelta(weeks=16),
                term_name=f"Term {i+1}",
                country=fake.country(),
                academic_term=random.choice(['Fall', 'Spring', 'Summer']),
                academic_year=fake.random_int(min=2000, max=2023),
                weeks=16,
                months=4,
            )

            # create school data
            if role == User.Admin or User.Head_of_curicullum :
                    School.objects.get_or_create(
                        name=fake.word() + ' School',
                        phone=fake.phone_number(),
                        email=fake.email(),
                        defaults={
                            "year_established": fake.date_between(start_date='-100y', end_date='-20y'),
                            "motto": fake.sentence(nb_words=6),
                            "term_system": random.choice(Term.objects.all()),
                            "total_students": fake.random_int(min=100, max=10000),
                            "principal_name": fake.name(),
                            "website_url": fake.url(),
                            "address": fake.address(),
                            "region": fake.state(),
                            "city": fake.city(),
                            "country": fake.country(),
                            "description": fake.paragraph(nb_sentences=3),
                        }
                    )
            
            # craete lesson data
            Lesson.objects.get_or_create(
                name=f"Lesson {i+1}",
                subject_id=fake.random_number(digits=8),
                _class=fake.random.choice(Class.objects.all()),
                learning_area=fake.job(),
                term=fake.random.choice(Term.objects.all()),
                week=fake.random_int(min=1, max=20),
                country=fake.country()
            )
           
        self.stdout.write(self.style.SUCCESS('Successfully generated fake data'))
