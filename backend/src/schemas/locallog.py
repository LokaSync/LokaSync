from typing import List, Optional

from schemas.common import (
    BaseAPIResponse,
    BasePagination,
    BaseFilterOptions
)
from models.locallog import LocalLogModel
from enums.locallog import LocalLogStatus


class LocalLogFilterOptions(BaseFilterOptions):
    """ Filter options specific to logs data. """
    flash_statuses: List[LocalLogStatus]


class SingleLocalLogResponse(BaseAPIResponse):
    """ Response schema for a single log entry. """
    data: Optional[LocalLogModel] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Log retrieved successfully",
                "status_code": 200,
                "data": {
                    "_id": "123456789",
                    "created_at": "2025-06-08T19:04:31.679626",
                    "session_id": "session-123456789",
                    "node_codename": "APNode_Penyemaian_1A",
                    "node_mac": "00:1A:2B:3C:4D:5E",
                    "firmware_version_origin": "1.0.3",
                    "firmware_size_kb": 1100.976,
                    "upload_duration_app_sec": 8.70,
                    "upload_duration_esp_sec": 8.33,
                    "latency_sec": 0.37,
                    "firmware_version_new": "v1.1.0_AP-Node-Isolate2-Async-10s.ino",
                    "bytes_written": 1100976,
                    "download_duration_sec": 8.33,
                    "download_speed_kbps": 129.03,
                    "flash_status": str(LocalLogStatus.IN_PROGRESS)
                }
            }
        }


class LocalLogDataResponse(BaseAPIResponse, BasePagination):
    filter_options: LocalLogFilterOptions = {}
    data: List[LocalLogModel] = []

    class Config:
        json_schema_extra = {
            "example": {
                "message": "List of logs retrieved successfully",
                "status_code": 200,
                "page": 1,
                "page_size": 10,
                "total_data": 0,
                "total_page": 1,
                "filter_options": {
                    "node_locations": [
                        "Cibubur-SayuranPagi",
                        "Bogor-SayuranPagi"
                    ],
                    "node_types": [
                        "Penyemaian",
                        "Pembibitan"
                    ],
                    "flash_statuses": [
                        LocalLogStatus.IN_PROGRESS,
                        LocalLogStatus.SUCCESS,
                        LocalLogStatus.FAILED
                    ]
                },
                "data": [
                    {
                        "_id": "123456789",
                        "created_at": "2025-06-08T19:04:31.679626",
                        "session_id": "session-123456789",
                        "node_codename": "APNode_Penyemaian_1A",
                        "node_mac": "00:1A:2B:3C:4D:5E",
                        "firmware_version_origin": "1.0.3",
                        "firmware_size_kb": 1100.976,
                        "upload_duration_app_sec": 8.70,
                        "upload_duration_esp_sec": 8.33,
                        "latency_sec": 0.37,
                        "firmware_version_new": "v1.1.0_AP-Node-Isolate2-Async-10s.ino",
                        "bytes_written": 1100976,
                        "download_duration_sec": 8.33,
                        "download_speed_kbps": 129.03,
                        "flash_status": str(LocalLogStatus.IN_PROGRESS)
                    }
                ]
            }
        }