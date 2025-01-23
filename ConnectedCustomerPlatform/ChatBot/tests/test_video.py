from django.test import TestCase
from ChatBot.constant.success_messages import SuccessMessages
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .test_error_data import create_data_video
from django.core.management import call_command
import uuid


class BaseTestCase(TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        
        super().setUpClass()
        call_command('makemigrations')
        call_command('migrate')


class VideoCorrectionTestCase(BaseTestCase):
    
    def setUp(self):
        
        self.client = APIClient()
        file, error = create_data_video()
        
        self.file = file
        self.error = error
        
    def test_get_video_transcription(self):
        
        file_uuid = self.file.knowledge_source_uuid
        
        response = self.client.get(
            reverse('ChatBot:get_video_transcription', kwargs={'file_uuid' : file_uuid})
        )
        
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result']['transcription'], [
        {
            "text": " What's up team? My name is Gabe Gowler. I am the senior lead technician here at  Combine Hills and welcome to my two-second lean video. So the whole purpose of the  two-second lean is to eliminate waste. Things that bug you on a daily basis",
            "start": "00:00:00",
            "end": "00:00:18",
            "duration": 18
        },
        {
            "text": " areas where you can improve or whether it be at the shop or at the turbine. So my  video is going to be on one of our outbuildings. Combine Hills over the years  that has become a complete disaster. Let me show you around. So as you can see,",
            "start": "00:00:18",
            "end": "00:00:36",
            "duration": 18.4
        },
        {
            "text": " there's nothing user friendly about this place. It's completely gotten out of control  and it's very unusual. Slip hazards, trip hazards, balls,  um, getting in and out of here is to get parts or tools as ridiculous and quite",
            "start": "00:00:37",
            "end": "00:00:58",
            "duration": 20.960000000000008
        },
        {
            "text": " frankly, this is what bugs me when I come out here. So I'm going to lean this baby up with the  help of yours. They purchase some shelving and we are going to fix this place.  So I can't wait to see you on the next video. This is leaner up.",
            "start": "00:00:58",
            "end": "00:01:15",
            "duration": 16.479999999999997
        },
        {
            "text": " Welcome back, Dean. Yeah, let's check out some improvements here.  Boom. So as you can see, we took a very  unusual space and made it useful. We eliminated waste. Couldn't even walk around in here before.",
            "start": "00:01:17",
            "end": "00:01:33",
            "duration": 16.480000000000004
        },
        {
            "text": " We're saving time. I'm not stumbling around to get in here to get things  and most importantly, we're going to eliminate the hazards. It's not perfect by any means,  but it is way better and it doesn't irritate me anymore. So there you have it. I'll",
            "start": "00:01:40",
            "end": "00:01:58",
            "duration": 18.64
        },
        {
            "text": " encourage you guys in your home life or work life. If you have something that's bugging you,  fix it. Thanks for watching.",
            "start": "00:02:00",
            "end": "00:02:06",
            "duration": 5.920000000000002
        }
    ])
        
        self.assertEqual(self.file.knowledge_source_path in json_response['result']['video_path'], True)
    
    def test_get_video_transcription_negative(self):
        
        file_uuid = str(uuid.uuid4())
        
        response = self.client.get(
            reverse('ChatBot:get_video_transcription', kwargs={'file_uuid' : file_uuid})
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_video_transcription(self):
        
        file_uuid = self.file.knowledge_source_uuid
        error_uuid = self.error.error_uuid
        
        transcription = [
        {
            "text": " What's up team? My name is Gabe Gowler",
            "start": "00:00:00",
            "end": "00:00:18",
            "duration": 18
        },
        {
            "text": " areas where you can improve or whether it be at the shop or at the turbine.",
            "start": "00:00:18",
            "end": "00:00:36",
            "duration": 18.4
        },
        {
            "text": " there's nothing user friendly about this place.",
            "start": "00:00:37",
            "end": "00:00:58",
            "duration": 20.960000000000008
        },
        {
            "text": " frankly, this is what bugs me when I come out here.",
            "start": "00:00:58",
            "end": "00:01:15",
            "duration": 16.479999999999997
        },
        {
            "text": " Welcome back, Dean.",
            "start": "00:01:17",
            "end": "00:01:33",
            "duration": 16.480000000000004
        },
        {
            "text": " We're saving time.",
            "start": "00:01:40",
            "end": "00:01:58",
            "duration": 18.64
        },
        {
            "text": " encourage you guys in your home life or work life.",
            "start": "00:02:00",
            "end": "00:02:06",
            "duration": 5.920000000000002
        }
    ]
        
        response = self.client.post(
            reverse('ChatBot:update_video_transcription'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'transcription' : transcription
            },
            format="json"
        )
        
        json_response = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response['result'], SuccessMessages.VIDEO_TRANSCRIPTION_UPDATE_SUCCESS)
    
    def test_update_video_transcription_negative(self):
        
        file_uuid = str(uuid.uuid4())
        error_uuid = self.error.error_uuid
        
        transcription = [
        {
            "text": " What's up team? My name is Gabe Gowler",
            "start": "00:00:00",
            "end": "00:00:18",
            "duration": 18
        },
        {
            "text": " areas where you can improve or whether it be at the shop or at the turbine.",
            "start": "00:00:18",
            "end": "00:00:36",
            "duration": 18.4
        },
        {
            "text": " there's nothing user friendly about this place.",
            "start": "00:00:37",
            "end": "00:00:58",
            "duration": 20.960000000000008
        },
        {
            "text": " frankly, this is what bugs me when I come out here.",
            "start": "00:00:58",
            "end": "00:01:15",
            "duration": 16.479999999999997
        },
        {
            "text": " Welcome back, Dean.",
            "start": "00:01:17",
            "end": "00:01:33",
            "duration": 16.480000000000004
        },
        {
            "text": " We're saving time.",
            "start": "00:01:40",
            "end": "00:01:58",
            "duration": 18.64
        },
        {
            "text": " encourage you guys in your home life or work life.",
            "start": "00:02:00",
            "end": "00:02:06",
            "duration": 5.920000000000002
        }
    ]
        
        response = self.client.post(
            reverse('ChatBot:update_video_transcription'),
            data={
                'file_uuid' : file_uuid,
                'error_uuid' : error_uuid,
                'transcription' : transcription
            },
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)