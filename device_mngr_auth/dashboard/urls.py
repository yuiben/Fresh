from django.urls import path
from device_mngr_auth.dashboard.views import (
    DashboardAPIView
    )

dashboard_urls = [
    path("dashboard/", DashboardAPIView.as_view(),name="dashboard"),
]
