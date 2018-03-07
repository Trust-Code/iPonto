import boto3


class Rekognition(object):

    def __init__(self, aws_access_key, aws_secret_key):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key

    def _get_client(self):
        return boto3.client(
            'rekognition', aws_access_key_id='',
            aws_secret_access_key='',
            region_name='us-east-1')

    def index_image(self, image, identifier):
        client = self._get_client()
        # client.create_collection(
        #      CollectionId='danimar'
        # )
        response = client.index_faces(
            CollectionId='danimar',
            Image={
                'Bytes': image,
            },
            ExternalImageId=identifier,
        )
        return response

    def search_face(self, image):
        client = self._get_client()
        response = client.search_faces_by_image(
            CollectionId='danimar',
            Image={
                'Bytes': image,
            },
            MaxFaces=10,
            FaceMatchThreshold=90.0
        )
        return response

    def delete_faces(self):
        client = self._get_client()
        response = client.list_faces(
            CollectionId='danimar',
        )
        if len(response['Faces']) > 0:
            response = client.delete_faces(
                CollectionId='danimar',
                FaceIds=[x['FaceId'] for x in response['Faces']]
            )
        print(response)
