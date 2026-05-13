import pandas as pd
from pathlib import Path
from loguru import logger

class ExportUtils:
    @staticmethod
    def export_to_csv(data: list, output_path: Path):
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            logger.info(f"Successfully exported data to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            return False

    @staticmethod
    def export_to_json(data: list, output_path: Path):
        try:
            df = pd.DataFrame(data)
            df.to_json(output_path, orient="records", indent=4)
            logger.info(f"Successfully exported data to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            return False
