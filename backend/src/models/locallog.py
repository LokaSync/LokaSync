from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from bson import ObjectId

from models.common import PyObjectId
from enums.locallog import LocalLogStatus
from utils.validator import validate_input
from utils.datetime import get_current_datetime, convert_datetime_to_str


class LocalLogModel(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    created_at: datetime = Field(..., default_factory=get_current_datetime)
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=255
    )
    node_codename: str = Field(
        ...,
        min_length=3,
        max_length=255
    )
    node_mac: str = Field(
        ...,
        min_length=12,
    )
    firmware_version_origin: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    # For QoS purpose
    firmware_size_kb: Optional[float] = Field(default=None)  # Firmware size in KB
    bytes_written: Optional[int] = Field(default=None)  # Bytes received by ESP32
    download_duration_sec: Optional[float] = Field(default=None)  # Download time (s)
    download_speed_kbps: Optional[float] = Field(default=None)  # Download speed (kB/s)
    upload_duration_app_sec: Optional[float] = Field(default=None)  # Upload time from app to ESP32
    upload_duration_esp_sec: Optional[float] = Field(default=None)  # Upload time reported by ESP32
    latency_sec: Optional[float] = Field(default=None)  # Latency between app and ESP32
    firmware_version_new: Optional[str] = Field(default=None)  # New firmware version flashed
    flash_status: Optional[LocalLogStatus] = Field(default=LocalLogStatus.IN_PROGRESS) # OTA update complete


    @field_validator("node_codename", "firmware_version_origin")
    def validate_string_fields(cls, v):
        return v.strip()


    class Config:
        """
        Configuration for the Log Model.
        
        Settings:
            validate_assignment: Ensures that field values are validated when assigned.
            populate_by_name: Allows the model to populate fields using the field's alias.
            validate_by_name: Allows the model to populate fields using the field's alias.
            arbitrary_types_allowed: Allows the use of arbitrary Python types like ObjectId.
            json_encoders: Custom JSON encoder for ObjectId to convert it to a string.
        """
        validate_assignment = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = { ObjectId: str, datetime: convert_datetime_to_str }
        json_schema_extra = {
            "example": {
                "_id": "123456789",
                "created_at": "2025-06-08T19:04:31.679626",
                "session_id": "session-123456789",
                "node_mac": "00:1A:2B:3C:4D:5E",
                "node_codename": "APNode_Penyemaian_1A",
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