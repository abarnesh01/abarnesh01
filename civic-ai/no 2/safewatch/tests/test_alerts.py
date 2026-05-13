import unittest
from alerts.alert_manager import AlertManager

class TestAlerts(unittest.TestCase):
    def test_alert_manager_init(self):
        # Initialize without telegram credentials
        manager = AlertManager(telegram_enabled=False)
        self.assertIsNotNone(manager)

if __name__ == "__main__":
    unittest.main()
