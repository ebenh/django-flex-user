REST API
========

To make the REST API available, modify your :mod:`urls.py` as follows:

.. code-block:: python
    :emphasize-lines: 3, 6-8

    urlpatterns = [
        ...
        path('api/accounts/', include('django_flex_user.urls')),
    ]

    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
    ]

