from fastapi import Depends
from pymongo import DESCENDING
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection
)

from enums.locallog import LocalLogStatus
from models.locallog import LocalLogModel
from schemas.locallog import LocalLogFilterOptions
from cores.dependencies import (
    get_db_connection,
    get_local_logs_collection
)
from utils.datetime import get_current_datetime
from utils.logger import logger


class LocalLogRepository:
    def __init__(
        self,
        db: AsyncIOMotorDatabase = Depends(get_db_connection),
        logs_collection: AsyncIOMotorCollection = Depends(get_local_logs_collection)
    ):
        self.db = db
        self.logs_collection = logs_collection
    
    async def upsert_log(
        self,
        filter_query: Dict[str, Any],
        update_fields: Dict[str, Any],
        log_data: Dict[str, Any]
    ) -> Optional[LocalLogModel]:
        """
        Upsert log entry in MongoDB.
        Returns LogModel with proper _id if successful, None otherwise.
        """
        try:
            existing = await self.logs_collection.find_one(filter_query)

            if existing:
                await self.logs_collection.update_one(
                    filter_query,
                    {"$set": update_fields}
                )
                logger.db_info("Log updated in MongoDB")
                updated_log = await self.logs_collection.find_one(filter_query)
                return LocalLogModel(**updated_log) if updated_log else None
            else:
                insert_data = {**filter_query, **update_fields}

                # Optional fields default
                optional_fields = [
                    "firmware_size_kb",
                    "bytes_written",
                    "download_duration_sec",
                    "download_speed_kbps",
                    "upload_duration_app_sec",
                    "upload_duration_esp_sec",
                    "latency_sec",
                    "firmware_version_new"
                ]
                for field in optional_fields:
                    insert_data.setdefault(field, None)

                # Set alias field if not already
                insert_data.setdefault("firmware_version-origin", log_data.get("firmware_version-origin", None))

                insert_data.setdefault("flash_status", LocalLogStatus.IN_PROGRESS)
                insert_data.setdefault("created_at", get_current_datetime())

                result = await self.logs_collection.insert_one(insert_data)
                logger.db_info(f"Log inserted into MongoDB with ID: {result.inserted_id}")
                insert_data["_id"] = result.inserted_id
                return LocalLogModel(**insert_data)
        except Exception as e:
            logger.db_error("MongoDB upsert failed", e)
            return None

    async def get_all_logs(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 10,
    ) -> List[LocalLogModel]:
        logger.db_info(f"Repository: Retrieving logs - Skip: {skip}, Limit: {limit}, Filters: {filters}")

        try:
            cursor = (
                self.logs_collection
                .find(filters or {})
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            logs = await cursor.to_list(length=limit)
            logger.db_info(f"Repository: Retrieved {len(logs)} logs from database")
            return [LocalLogModel(**log) for log in logs]
        except Exception as e:
            logger.db_error("Repository: Failed to retrieve logs", e)
            return []
    
    async def get_detail_log(self, session_id: str) -> Optional[LocalLogModel]:
        """
        Retrieve a detailed log entry by session id.
        Returns LogModel if found, None otherwise.
        """
        logger.db_info(f"Repository: Retrieving log for session id '{session_id}'")

        try:
            log = await self.logs_collection.find_one({
                "session_id": session_id
            })
            if log:
                logger.db_info(f"Repository: Log found for session id '{session_id}'")
                return LocalLogModel(**log)
            else:
                logger.db_info(f"Repository: No log found for session id '{session_id}'")
                return None
        except Exception as e:
            logger.db_error(f"Repository: Failed to retrieve log for session id '{session_id}'", e)
            return None
    
    async def get_node_by_codename(self, node_codename: str) -> bool:
        logger.db_info(f"Repository: Checking if log exists for node '{node_codename}'")
        try:
            node_exists = await self.logs_collection.find_one({"node_codename": node_codename})
            result = True if node_exists else False
            logger.db_info(f"Repository: Log exists for node '{node_codename}': {result}")
            return result
        except Exception as e:
            logger.db_error(f"Repository: Failed to check log existence for node '{node_codename}'", e)
            return False

    async def delete_log(self, session_id: str) -> int:
        logger.db_info(f"Repository: Deleting logs for session id '{session_id}'")

        try:
            result = await self.logs_collection.delete_one({"session_id": session_id})
            logger.db_info(f"Repository: Deleted {result.deleted_count} log(s) for session id '{session_id}'")

            return result.deleted_count
        except Exception as e:
            logger.db_error(f"Repository: Failed to delete logs for session id '{session_id}'", e)
            return 0
    
    async def count_logs(self, filters: Dict[str, Any]) -> int:
        logger.db_info(f"Repository: Counting logs with filters: {filters}")
        
        try:
            count = await self.logs_collection.count_documents(filters)
            logger.db_info(f"Repository: Total logs count: {count}")
            return count
        except Exception as e:
            logger.db_error("Repository: Failed to count logs", e)
            return 0
    
    async def get_filter_options(self) -> LocalLogFilterOptions:
        logger.db_info("Repository: Getting log filter options")
        
        try:
            pipeline = [
                {"$group": {
                    "_id": None,
                    "node_codename": {"$addToSet": "$node_codename"},
                    "flash_status": {"$addToSet": "$flash_status"}
                }},
                {"$project": {
                    "_id": 0,
                    "node_location": 1,
                    "flash_status": 1
                }}
            ]

            result = await self.logs_collection.aggregate(pipeline).to_list(length=1)

            # Get all flash statuses from the LogStatus enum
            all_flash_statuses = [status.value for status in LocalLogStatus]

            if result:
                filter_options = LocalLogFilterOptions(
                    node_locations=result[0].get("node_codename", []),
                    node_types=[],  # Empty, since model doesn't include node_type
                    flash_statuses=all_flash_statuses
                )
            else:
                filter_options = LocalLogFilterOptions(
                    node_locations=[],
                    node_types=[],
                    flash_statuses=all_flash_statuses
                )

            logger.db_info("Repository: Log filter options retrieved successfully")
            return filter_options
        except Exception as e:
            logger.db_error("Repository: Failed to get log filter options", e)
            return LocalLogFilterOptions(
                node_locations=[],
                node_types=[],
                flash_statuses=[status.value for status in LocalLogStatus]
            )