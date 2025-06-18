export interface FirmwareLocalLog {
  _id: string;
  created_at: string;
  session_id: string;
  node_mac: string;
  node_codename: string;
  firmware_version_origin: string;

  // QoS / monitoring detail
  firmware_size_kb: number;
  upload_duration_app_sec: number;
  upload_duration_esp_sec: number;
  latency_sec: number;
  firmware_version_new: string;
  bytes_written: number;
  download_duration_sec: number;
  download_speed_kbps: number;

  flash_status: "in progress" | "success" | "failed";
}

export interface LocalLogsListParams {
  page?: number;
  page_size?: number;
  flash_status?: string;
}

export interface LocalLogFilterOptions {
  flash_statuses: string[];
}
