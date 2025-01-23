from WiseFlow.views.entity_views import EntityViewSet
from django.urls import path

from WiseFlow.views.intent_classification_handler_views import IntentClassificationHandlerViewSet

urlpatterns = [
    path('entity_examples',EntityViewSet.as_view({
            'post': 'add_entity_examples'
        }), name='add_entity_examples'),
    
    path('test_entity_prompt',EntityViewSet.as_view({
            'post': 'test_entity_prompt'
        }), name='test_entity_prompt'),

    # Wiseflow api's
    path('entity', EntityViewSet.as_view({
        'post': 'create_entity',
        'put': 'update_entity'
    }), name="add_edit_wiseflow_entity"),

    path('entity/get_entities', EntityViewSet.as_view({
        'post': 'get_entities'
    }), name="get_wiseflow_entities"),

    path('entity/<str:entity_uuid>', EntityViewSet.as_view({
        'delete': 'delete_entity',
        'get': 'get_entity'
    }), name="get_delete_wiseflow_entity"),

    path('parent_entities', EntityViewSet.as_view({'get': 'get_parent_entities'}), name="get_parent_entities"),

    path('test_intent_classification',IntentClassificationHandlerViewSet.as_view({
            'post': 'intent_classification_handler'
        }), name='intent_classification')
]
