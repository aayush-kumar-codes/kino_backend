from .models import School, User

def get_school_obj(request):
    school = School.objects.get(users=request.user.id, users__role=User.School_Admin)
    return school
