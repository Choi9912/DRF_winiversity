from rest_framework import viewsets, permissions
from .models import Mission, MissionSubmission
from .serializers import MissionSerializer, MissionSubmissionSerializer


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer


class MissionSubmissionViewSet(viewsets.ModelViewSet):
    queryset = MissionSubmission.objects.all()
    serializer_class = MissionSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        submission = serializer.save(user=self.request.user)
        # Here you would implement the logic to check if the submission is correct
        # For simplicity, we're just marking it as correct
        submission.is_correct = True
        submission.save()
