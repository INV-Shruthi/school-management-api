from rest_framework import serializers
from .models import CustomUser, Teacher, Student , Exam, Question, StudentExam, StudentAnswer
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user_id': self.user.id,
            'username': self.user.username,
            'role': self.user.role,
        })
        return data



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }



class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            'id',
            'employee_id',
            'subject_specialization',
            'date_of_joining',
            'status',
            'full_name',
        ]

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"



class StudentSerializer(serializers.ModelSerializer):
    assigned_teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), write_only=True
    )
    assigned_teacher_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'roll_number',
            'student_name',
            'phone_number',
            'student_class',
            'date_of_birth',
            'admission_date',
            'status',
            'user',
            'assigned_teacher',        
            'assigned_teacher_name'    
        ]

    def get_assigned_teacher_name(self, obj):
        if obj.assigned_teacher:
            return f"{obj.assigned_teacher.user.first_name} {obj.assigned_teacher.user.last_name}"
        return None

    def get_student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"



    def get_assigned_teacher(self, obj):
        if obj.assigned_teacher:
            return f"{obj.assigned_teacher.user.first_name} {obj.assigned_teacher.user.last_name}"
        return None

    def get_student_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class StudentNameSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name')

    class Meta:
        model = Student
        fields = ['id', 'name']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text']

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, write_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'title', 'teacher', 'created_at', 'questions']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        exam = Exam.objects.create(**validated_data)
        for question in questions_data:
            Question.objects.create(exam=exam, **question)
        return exam

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['question', 'answer_text']

class StudentExamSerializer(serializers.ModelSerializer):
    answers = StudentAnswerSerializer(many=True)
    score = serializers.IntegerField(required=False)
    remarks = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = StudentExam
        fields = ['exam', 'student', 'answers', 'score', 'remarks']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        student_exam = StudentExam.objects.create(**validated_data)
        for ans in answers_data:
            StudentAnswer.objects.create(student_exam=student_exam, **ans)
        return student_exam

    def update(self, instance, validated_data):
        instance.score = validated_data.get('score', instance.score)
        instance.remarks = validated_data.get('remarks', instance.remarks)
        instance.save()
        return instance
