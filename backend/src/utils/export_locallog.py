import csv
import io
from datetime import datetime
from typing import List, BinaryIO

from fpdf import FPDF
from models.locallog import LocalLogModel
from utils.datetime import convert_datetime_to_str


class PDF(FPDF):
    def header(self):
        # Set font
        self.set_font('Arial', 'B', 16)
        # Move to the right
        self.cell(80)
        # Title
<<<<<<< HEAD
        self.cell(30, 10, 'LokaSync OTA - Log Export', 0, 0, 'C')
=======
        self.cell(30, 10, 'LokaSync OTA - Local Log Export', 0, 0, 'C')
>>>>>>> 89b069b4bab9267b191b84041a5433ab6aa0bda5
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        # Export date
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 10, f'Generated: {export_date}', 0, 0, 'R')


def create_csv_from_local_logs(logs: List[LocalLogModel]) -> BinaryIO:
    """
    Creates a CSV file from a list of log models.
    
    Args:
        logs: List of LogModel objects
        
    Returns:
        A file-like object containing the CSV data
    """
    output = io.StringIO()

    field_mappings = {
        "_id": "Doc ID",
        "created_at": "Created At",
        "session_id": "Session ID",
        "node_mac": "Node MAC",
        "node_codename": "Node Codename",
        "firmware_version_origin": "Previous Version",
        "firmware_version_new": "New Version",
        "firmware_size_kb": "Firmware Size (KB)",
        "upload_duration_app_sec": "Upload Duration App (s)",
        "upload_duration_esp_sec": "Upload Duration ESP (s)",
        "latency_sec": "Latency (s)",
        "bytes_written": "Bytes Written",
        "download_duration_sec": "Download Duration (s)",
        "download_speed_kbps": "Download Speed (Kb/s)",
        "flash_status": "Flash Status"
    }

    if logs:
        fieldnames = list(field_mappings.keys())
    else:
        fieldnames = list(field_mappings.keys())

    writer = csv.writer(output)
    writer.writerow([field_mappings.get(field, field) for field in fieldnames])

    for log in logs:
        log_dict = log.model_dump()
        row = []
        for field in fieldnames:
            value = log_dict.get(field)
            if isinstance(value, datetime):
                value = convert_datetime_to_str(value)
            row.append(value)
        writer.writerow(row)

    binary_output = io.BytesIO()
    binary_output.write(output.getvalue().encode('utf-8'))
    binary_output.seek(0)
    return binary_output

def create_pdf_from_local_logs(logs: List[LocalLogModel]) -> BinaryIO:
    """
    Creates a PDF file from a list of log models.
    
    Args:
        logs: List of LogModel objects
        
    Returns:
        A file-like object containing the PDF data
    """
    pdf = PDF()
    pdf.add_page()

    if not logs:
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "No logs available for export", 0, 1, 'C')
        output = io.BytesIO()
        pdf_content = pdf.output(dest='S')
        output.write(pdf_content.encode('latin1') if isinstance(pdf_content, str) else pdf_content)
        output.seek(0)
        return output

    # Summary table with key information
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Local Log Summary", 0, 1, 'C')
    pdf.ln(5)

    # Define column widths for summary table - use page width effectively
    page_width = pdf.w - 20
    col_widths = {
        "session_id": page_width * 0.15,
        "node_codename": page_width * 0.35,
        "firmware_version_origin": page_width * 0.15,
        "created_at": page_width * 0.20, 
        "flash_status": page_width * 0.15,
    }

    # Add table headers with proper formatting
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)

    # Center the table
    start_x = (pdf.w - sum(col_widths.values())) / 2
    pdf.set_x(start_x)

    pdf.cell(col_widths["session_id"], 8, "Session ID", 1, 0, 'C', 1)
    pdf.cell(col_widths["node_codename"], 8, "Node Codename", 1, 0, 'C', 1)
    pdf.cell(col_widths["firmware_version_origin"], 8, "Previous Version", 1, 0, 'C', 1)
    pdf.cell(col_widths["created_at"], 8, "Created At", 1, 0, 'C', 1)
    pdf.cell(col_widths["flash_status"], 8, "Status", 1, 1, 'C', 1)

    # Add data rows
    pdf.set_font("Arial", size=8)
    for i, log in enumerate(logs):
        # Alternate row colors for better readability
        if i % 2 == 0:
            pdf.set_fill_color(245, 245, 245)  # Light gray for even rows
        else:
            pdf.set_fill_color(255, 255, 255)  # White for odd rows
        
        # Center the table row
        pdf.set_x(start_x)
        
        # Truncate long text to fit in cells
        session_id = str(log.session_id)[:12] + "..." if len(str(log.session_id)) > 15 else str(log.session_id)
        node_codename = log.node_codename[:30] + "..." if len(log.node_codename) > 33 else log.node_codename
        firmware_version_origin = log.firmware_version_origin[:12] + "..." if len(log.firmware_version_origin) > 15 else log.firmware_version_origin
        created_at = convert_datetime_to_str(log.created_at)[:16]  # Show date and time without seconds
        flash_status = str(log.flash_status)[:12] + "..." if len(str(log.flash_status)) > 15 else str(log.flash_status)
        
        pdf.cell(col_widths["session_id"], 8, session_id, 1, 0, 'C', 1)
        pdf.cell(col_widths["node_codename"], 8, node_codename, 1, 0, 'L', 1)
        pdf.cell(col_widths["firmware_version_origin"], 8, firmware_version_origin, 1, 0, 'C', 1)
        pdf.cell(col_widths["created_at"], 8, created_at, 1, 0, 'C', 1)
        pdf.cell(col_widths["flash_status"], 8, flash_status, 1, 1, 'C', 1)

    # Add detailed logs on new pages
    if logs:
        # Field mappings for detailed view
        field_mappings = {
            "_id": "Doc ID",
            "created_at": "Created At",
            "session_id": "Session ID",
            "node_mac": "Node MAC",
            "node_codename": "Node Codename",
            "firmware_version_origin": "Previous Version",
            "firmware_version_new": "New Version",
            "firmware_size_kb": "Firmware Size (KB)",
            "upload_duration_app_sec": "Upload Duration App (s)",
            "upload_duration_esp_sec": "Upload Duration ESP (s)",
            "latency_sec": "Latency (s)",
            "bytes_written": "Bytes Written",
            "download_duration_sec": "Download Duration (s)",
            "download_speed_kbps": "Download Speed (Kb/s)",
            "flash_status": "Flash Status"
        }
        
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Detailed Log Information", 0, 1, 'C')
        pdf.ln(5)

        for i, log in enumerate(logs):
            # Add page break if needed
            if pdf.get_y() > 250:  # Near bottom of page
                pdf.add_page()
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, f"Log {i+1}: {log.node_codename}", 0, 1)
            pdf.ln(2)
            
            log_dict = log.model_dump()
            pdf.set_font("Arial", '', 9)
            
            for key, value in log_dict.items():
                if value is not None:  # Only show fields with values
                    human_key = field_mappings.get(key, key.replace('_', ' ').title())
                    
                    if isinstance(value, datetime):
                        value = convert_datetime_to_str(value)
                    
                    # Format the key-value pair
                    pdf.set_font("Arial", 'B', 9)
                    pdf.cell(50, 6, f"{human_key}:", 0, 0)
                    pdf.set_font("Arial", '', 9)
                    
                    # Handle long values with text wrapping
                    value_str = str(value)
                    if len(value_str) > 80:
                        # Use multi_cell for long text
                        x_pos = pdf.get_x()
                        y_pos = pdf.get_y()
                        pdf.set_x(x_pos)
                        pdf.multi_cell(0, 6, value_str, 0, 1)
                    else:
                        pdf.cell(0, 6, value_str, 0, 1)
            
            pdf.ln(5)  # Add some space between logs
    
    output = io.BytesIO()
    pdf_content = pdf.output(dest='S')
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('latin1'))
    else:
        output.write(pdf_content)
    output.seek(0)
    
    return output