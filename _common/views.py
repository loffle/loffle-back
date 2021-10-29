from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet


class CommonViewSet(ModelViewSet):
    # 저장 시 자동으로 요청한 사용자 설정
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 삭제 시 `is_deleted` 값 True로 설정
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return Response(status=HTTP_204_NO_CONTENT)